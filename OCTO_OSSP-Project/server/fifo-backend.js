/**
 * fifo-backend.js
 * Backend coordinator for Linux Named FIFO IPC.
 * Connects the web simulator directly to the real Linux C implementation:
 * linux-implementation/myfifo
 */

import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

const isWindows = process.platform === 'win32';
const wslProjectDir = '/home/g_jashwanth_reddy/OCTO_OSSP-project/linux-implementation';

function runWslCommand(command) {
  return new Promise((resolve) => {
    const proc = spawn('wsl', ['bash', '-c', command]);
    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (d) => { stdout += d.toString(); });
    proc.stderr.on('data', (d) => { stderr += d.toString(); });

    proc.on('close', (code) => {
      resolve({
        code: code || 0,
        stdout,
        stderr
      });
    });

    proc.on('error', (err) => {
      resolve({
        code: 1,
        stdout: '',
        stderr: err.message
      });
    });
  });
}

/**
 * Checks if the shared FIFO exists and verifies lock state.
 */
export async function getFifoStatus() {
  if (isWindows) {
    const res = await runWslCommand(`cd ${wslProjectDir} && test -p myfifo && echo "IS_FIFO" || echo "NOT_FIFO"`);
    const isFifo = res.stdout.includes('IS_FIFO');
    return {
      exists: isFifo,
      is_fifo: isFifo,
      path: 'linux-implementation/myfifo',
      display_path: 'linux-implementation/myfifo_display.txt',
      environment: 'Linux (WSL Ubuntu)'
    };
  } else {
    const localFifoPath = path.join(projectRoot, 'linux-implementation', 'myfifo');
    try {
      const stats = fs.statSync(localFifoPath);
      return {
        exists: true,
        is_fifo: stats.isFIFO(),
        path: 'linux-implementation/myfifo',
        display_path: 'linux-implementation/myfifo_display.txt',
        environment: 'Linux Native'
      };
    } catch {
      return {
        exists: false,
        is_fifo: false,
        path: 'linux-implementation/myfifo',
        display_path: 'linux-implementation/myfifo_display.txt',
        environment: 'Linux Native'
      };
    }
  }
}

/**
 * Get current in-flight display file content.
 */
export async function getFifoDisplay() {
  if (isWindows) {
    const res = await runWslCommand(`cd ${wslProjectDir} && test -f myfifo_display.txt && cat myfifo_display.txt || true`);
    return {
      content: res.stdout.trim()
    };
  } else {
    const dispPath = path.join(projectRoot, 'linux-implementation', 'myfifo_display.txt');
    try {
      const content = fs.readFileSync(dispPath, 'utf8');
      return { content: content.trim() };
    } catch {
      return { content: '' };
    }
  }
}

/**
 * Executes a real FIFO message transfer:
 * 1. Coordinates with run_transfer.sh to perform lock checking and real myfifo transmission.
 * 2. Updates display file myfifo_display.txt for 1-2 seconds during transmission.
 * 3. Returns actual received message verified from fifo_reader.
 */
export async function transferFifoMessage(message) {
  if (!message || typeof message !== 'string' || message.trim().length === 0) {
    return {
      success: false,
      error: 'Message payload cannot be empty.'
    };
  }

  const cleanMessage = message.trim();

  if (isWindows) {
    return transferViaWsl(cleanMessage);
  } else {
    return transferNativeLinux(cleanMessage);
  }
}

async function transferViaWsl(cleanMessage) {
  const escapedMsg = cleanMessage.replace(/'/g, "'\\''");

  // Also sync Windows display file
  const winDisplayFile = path.join(projectRoot, 'linux-implementation', 'myfifo_display.txt');
  try {
    fs.writeFileSync(winDisplayFile, cleanMessage + '\n', 'utf8');
  } catch {}

  // Single fast execution through real Linux myfifo
  const result = await runWslCommand(`${wslProjectDir}/run_transfer.sh '${escapedMsg}'`);
  const output = result.stdout + '\n' + result.stderr;

  // Clear Windows display file after communication
  try {
    fs.writeFileSync(winDisplayFile, '', 'utf8');
  } catch {}

  if (output.includes('FIFO is currently being used by another communication session.') || result.code === 2) {
    return {
      success: false,
      error: 'FIFO is currently being used by another communication session. Please try again.'
    };
  }

  // Parse exact output from reader: [PROCESS B RECEIVED OUTPUT]: "..."
  const match = output.match(/\[PROCESS B RECEIVED OUTPUT\]:\s*"([^"]+)"/);
  const receivedMsg = match ? match[1] : null;

  if (!receivedMsg) {
    return {
      success: false,
      error: 'Failed to receive payload through linux-implementation/myfifo: ' + output.slice(0, 300)
    };
  }

  return {
    success: true,
    sent_message: cleanMessage,
    received_message: receivedMsg,
    bytes_transferred: Buffer.byteLength(receivedMsg, 'utf8') + 1,
    fifo_path: 'linux-implementation/myfifo',
    display_file: 'linux-implementation/myfifo_display.txt',
    steps: [
      { step: 1, syscall: 'lstat("linux-implementation/myfifo")', status: 'verified (S_ISFIFO)' },
      { step: 2, syscall: 'open("linux-implementation/myfifo", O_WRONLY)', status: 'success' },
      { step: 3, syscall: `write(fd, "${cleanMessage}", ${Buffer.byteLength(cleanMessage, 'utf8') + 1})`, status: 'success' },
      { step: 4, syscall: 'open("linux-implementation/myfifo", O_RDONLY)', status: 'success' },
      { step: 5, syscall: `read(fd, buffer, 512)`, status: 'success' },
      { step: 6, syscall: 'close(fd)', status: 'success' }
    ]
  };
}

async function transferNativeLinux(cleanMessage) {
  const linuxDir = path.join(projectRoot, 'linux-implementation');
  const readerBin = path.join(linuxDir, 'fifo_reader');
  const writerBin = path.join(linuxDir, 'fifo_writer');
  const dispPath = path.join(linuxDir, 'myfifo_display.txt');

  // Update display file
  try {
    fs.writeFileSync(dispPath, cleanMessage + '\n', 'utf8');
  } catch {}

  return new Promise((resolve) => {
    // Spawn reader (Process B)
    const reader = spawn(readerBin, ['--timeout', '6'], { cwd: linuxDir });
    let readerOut = '';
    let readerErr = '';

    reader.stdout.on('data', (d) => { readerOut += d.toString(); });
    reader.stderr.on('data', (d) => { readerErr += d.toString(); });

    setTimeout(() => {
      // Spawn writer (Process A)
      const writer = spawn(writerBin, [cleanMessage], { cwd: linuxDir });
      let writerOut = '';
      let writerErr = '';

      writer.stdout.on('data', (d) => { writerOut += d.toString(); });
      writer.stderr.on('data', (d) => { writerErr += d.toString(); });

      writer.on('close', () => {
        reader.on('close', () => {
          const combined = readerOut + '\n' + writerOut + '\n' + readerErr + '\n' + writerErr;

          // Clear display file after communication
          try {
            fs.writeFileSync(dispPath, '', 'utf8');
          } catch {}

          if (combined.includes('FIFO is currently being used by another communication session.')) {
            return resolve({
              success: false,
              error: 'FIFO is currently being used by another communication session. Please try again.'
            });
          }

          const match = combined.match(/\[PROCESS B RECEIVED OUTPUT\]:\s*"([^"]+)"/);
          const receivedMsg = match ? match[1] : null;

          if (!receivedMsg) {
            return resolve({
              success: false,
              error: 'Failed to receive payload through linux-implementation/myfifo: ' + combined.slice(0, 300)
            });
          }

          return resolve({
            success: true,
            sent_message: cleanMessage,
            received_message: receivedMsg,
            bytes_transferred: Buffer.byteLength(receivedMsg, 'utf8') + 1,
            fifo_path: 'linux-implementation/myfifo',
            display_file: 'linux-implementation/myfifo_display.txt',
            steps: [
              { step: 1, syscall: 'lstat("linux-implementation/myfifo")', status: 'verified (S_ISFIFO)' },
              { step: 2, syscall: 'open("linux-implementation/myfifo", O_WRONLY)', status: 'success' },
              { step: 3, syscall: `write(fd, "${cleanMessage}", ${Buffer.byteLength(cleanMessage, 'utf8') + 1})`, status: 'success' },
              { step: 4, syscall: 'open("linux-implementation/myfifo", O_RDONLY)', status: 'success' },
              { step: 5, syscall: `read(fd, buffer, 512)`, status: 'success' },
              { step: 6, syscall: 'close(fd)', status: 'success' }
            ]
          });
        });
      });
    }, 120);
  });
}

/**
 * Get recent received messages history.
 */
export async function getFifoHistory() {
  if (isWindows) {
    const res = await runWslCommand(`cd ${wslProjectDir} && test -f received_messages.txt && tail -n 20 received_messages.txt || true`);
    return {
      history: res.stdout.trim().split('\n').filter(Boolean)
    };
  } else {
    const histPath = path.join(projectRoot, 'linux-implementation', 'received_messages.txt');
    try {
      const content = fs.readFileSync(histPath, 'utf8');
      return {
        history: content.trim().split('\n').filter(Boolean).slice(-20)
      };
    } catch {
      return { history: [] };
    }
  }
}

/**
 * Explicitly reset and clear display file to 0 bytes.
 */
export async function resetFifoState() {
  const winDisplayFile = path.join(projectRoot, 'linux-implementation', 'myfifo_display.txt');
  try {
    fs.writeFileSync(winDisplayFile, '', 'utf8');
  } catch {}

  if (isWindows) {
    await runWslCommand(`truncate -s 0 ${wslProjectDir}/myfifo_display.txt`);
  } else {
    const localDispPath = path.join(projectRoot, 'linux-implementation', 'myfifo_display.txt');
    try {
      fs.writeFileSync(localDispPath, '', 'utf8');
    } catch {}
  }
  return { success: true, cleared: true };
}
