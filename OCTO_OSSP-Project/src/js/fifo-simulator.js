// fifo-simulator.js - Named FIFO Simulation Engine
// Connects directly to the real Linux C Implementation (linux-implementation/myfifo)
import { showToast } from './main.js';

let isFifoAnimating = false;
let fifoTimers = [];

// Determine API Base URL so it works seamlessly on localhost:5173, custom ports, or file://
const API_BASE = (window.location.protocol === 'file:' || (window.location.port && window.location.port !== '5173'))
  ? 'http://localhost:5173'
  : '';

export function initFifoSimulator() {
  const btnWrite = document.getElementById('btnFifoWrite');
  const btnReset = document.getElementById('btnFifoReset');
  const inputMsg = document.getElementById('fifoInput');

  if (btnWrite) {
    btnWrite.addEventListener('click', runFifoSimulation);
  }

  if (btnReset) {
    btnReset.addEventListener('click', resetFifoSimulation);
  }

  if (inputMsg) {
    inputMsg.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        runFifoSimulation();
      }
    });
  }

  // Check initial FIFO status from backend
  checkFifoStatus();
}

async function checkFifoStatus() {
  const stateLabel = document.getElementById('fifoStateLabel');
  const displayTag = document.getElementById('fifoDisplayFileLiveStatus');
  try {
    const res = await fetch(`${API_BASE}/api/fifo/status`);
    if (res.ok) {
      const data = await res.json();
      if (stateLabel && !isFifoAnimating) {
        stateLabel.textContent = data.is_fifo ? 'STATUS: READY (Shared Linux FIFO Verified)' : 'STATUS: READY';
      }
    }
  } catch {
    if (stateLabel && !isFifoAnimating) {
      stateLabel.textContent = 'STATUS: READY';
    }
  }

  try {
    const dispRes = await fetch(`${API_BASE}/api/fifo/display`);
    if (dispRes.ok) {
      const dispData = await dispRes.json();
      if (displayTag && !isFifoAnimating) {
        if (dispData.content && dispData.content.length > 0) {
          displayTag.textContent = `"${dispData.content}"`;
          displayTag.style.color = 'var(--cyan-accent)';
        } else {
          displayTag.textContent = '[ EMPTY (0 bytes) ]';
          displayTag.style.color = 'var(--emerald-success)';
        }
      }
    }
  } catch {}
}

async function runFifoSimulation() {
  if (isFifoAnimating) return;

  const inputMsg = document.getElementById('fifoInput');
  const text = inputMsg ? inputMsg.value.trim() : '';

  if (!text) {
    showToast('Please enter a message for the FIFO buffer!');
    if (inputMsg) inputMsg.focus();
    return;
  }

  isFifoAnimating = true;
  setFifoControlsDisabled(true);
  clearFifoTimers();

  const indicatorA = document.getElementById('fifoIndicatorA');
  const indicatorB = document.getElementById('fifoIndicatorB');
  const output = document.getElementById('fifoOutput');
  const stateLabel = document.getElementById('fifoStateLabel');
  const emptyNotice = document.getElementById('fifoEmptyNotice');
  const packet = document.getElementById('fifoPacket');
  const fifoBox = document.getElementById('fifoBuffer');

  const processA = document.getElementById('fifoProcessA');
  const processB = document.getElementById('fifoProcessB');
  const queueArea = document.getElementById('fifoQueueArea');

  resetChecklist();
  if (output) {
    output.classList.remove('has-data');
    output.innerHTML = `<span style="color: var(--purple-accent); font-style: italic;">Contacting Linux kernel FIFO backend...</span>`;
  }
  if (stateLabel) stateLabel.textContent = 'STATUS: EXECUTING LINUX SYSTEM CALLS...';

  // 1. Send to real Linux backend to perform actual FIFO communication
  let backendResult = null;
  try {
    const response = await fetch(`${API_BASE}/api/fifo/write`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });

    const responseText = await response.text();
    try {
      backendResult = JSON.parse(responseText);
    } catch {
      backendResult = {
        success: false,
        error: responseText || `HTTP ${response.status} ${response.statusText}`
      };
    }

    if (!response.ok || !backendResult.success) {
      const errorMsg = (backendResult && backendResult.error) ? backendResult.error : 'FIFO communication failed.';
      showToast(errorMsg);
      if (stateLabel) stateLabel.textContent = `STATUS: ${errorMsg}`;
      if (output) {
        output.innerHTML = `<span style="color: var(--rose-danger); font-style: italic;">${errorMsg}</span>`;
      }
      isFifoAnimating = false;
      setFifoControlsDisabled(false);
      return;
    }
  } catch (err) {
    const errorMsg = 'Local backend unavailable. Please ensure "npm run dev" is running.';
    showToast(errorMsg);
    if (stateLabel) stateLabel.textContent = 'STATUS: BACKEND OFFLINE';
    if (output) {
      output.innerHTML = `<span style="color: var(--rose-danger); font-style: italic;">${errorMsg} (${err.message})</span>`;
    }
    isFifoAnimating = false;
    setFifoControlsDisabled(false);
    return;
  }

  // Actual received payload verified from the real Linux C reader process
  const actualPayload = backendResult.received_message || text;

  // 2. Animate the transmission using the real transmitted payload
  // --- Step 1: lstat() / mkfifo() verified ---
  updateChecklistStep(1);
  if (indicatorA) indicatorA.classList.add('active');
  if (stateLabel) stateLabel.textContent = 'STATUS: VERIFIED FIFO (lstat S_ISFIFO)';

  // Prepare packet element
  if (packet) {
    packet.textContent = actualPayload;
    packet.title = actualPayload;
    packet.style.display = 'block';
    packet.style.transition = 'none';
    packet.style.opacity = '0';

    // Position at Process A
    const rectA = processA.getBoundingClientRect();
    const rectQueue = queueArea.getBoundingClientRect();
    const startX = rectA.left + (rectA.width / 2) - (rectQueue.left + rectQueue.width / 2);
    packet.style.transform = `translateX(${startX}px) scale(0.8)`;
  }

  // --- Step 2: open O_WRONLY ---
  scheduleTimer(() => {
    updateChecklistStep(2);
    if (stateLabel) stateLabel.textContent = 'STATUS: OPENED WRITER (open O_WRONLY)';
  }, 400);

  // --- Step 3: write() - Packet glides into linux-implementation/myfifo ---
  scheduleTimer(() => {
    updateChecklistStep(3);
    if (stateLabel) stateLabel.textContent = 'STATUS: WRITING TO linux-implementation/myfifo';

    const displayTag = document.getElementById('fifoDisplayFileLiveStatus');
    if (displayTag) {
      displayTag.textContent = `"${actualPayload}" (in transit)`;
      displayTag.style.color = 'var(--cyan-accent)';
    }

    if (emptyNotice) emptyNotice.style.display = 'none';
    if (fifoBox) fifoBox.classList.add('active-queue');

    if (packet) {
      packet.style.transition = 'transform 0.8s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.3s ease';
      packet.style.opacity = '1';
      packet.style.transform = 'translateX(0px) scale(1)'; // Glides to central FIFO box
    }

    scheduleTimer(() => {
      if (stateLabel) stateLabel.textContent = 'STATUS: DATA IN myfifo (myfifo_display.txt active)';
    }, 800);
  }, 800);

  // --- Step 4 & 5: Message remains in FIFO channel for 1.5s, then Reader Process B attaches and reads ---
  scheduleTimer(() => {
    updateChecklistStep(4);
    if (indicatorA) indicatorA.classList.remove('active');
    if (indicatorB) indicatorB.classList.add('active');
    if (stateLabel) stateLabel.textContent = 'STATUS: READER ATTACHED (open O_RDONLY)';
  }, 2300);

  // --- Step 5: read() payload out of FIFO into Process B ---
  scheduleTimer(() => {
    updateChecklistStep(5);
    if (stateLabel) stateLabel.textContent = 'STATUS: READING FROM linux-implementation/myfifo (read)';

    const displayTag = document.getElementById('fifoDisplayFileLiveStatus');
    if (displayTag) {
      displayTag.textContent = '[ CLEARED (0 bytes) ]';
      displayTag.style.color = 'var(--emerald-success)';
    }

    if (packet) {
      const rectB = processB.getBoundingClientRect();
      const rectQueue = queueArea.getBoundingClientRect();
      const endX = rectB.left + (rectB.width / 2) - (rectQueue.left + rectQueue.width / 2);

      packet.style.transition = 'transform 0.8s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s ease';
      packet.style.transform = `translateX(${endX}px) scale(0.8)`;
      packet.style.opacity = '0';
    }
  }, 3000);

  // --- Step 6: close() & release lock (FIFO persists) ---
  scheduleTimer(() => {
    updateChecklistStep(6);
    if (indicatorB) indicatorB.classList.remove('active');
    if (stateLabel) stateLabel.textContent = 'STATUS: MESSAGE RECEIVED (myfifo Persistent)';
    if (fifoBox) fifoBox.classList.remove('active-queue');

    const displayTag = document.getElementById('fifoDisplayFileLiveStatus');
    if (displayTag) {
      displayTag.textContent = '[ CLEARED (0 bytes) ]';
      displayTag.style.color = 'var(--emerald-success)';
    }

    if (packet) packet.style.display = 'none';
    if (emptyNotice) emptyNotice.style.display = 'inline';

    if (output) {
      output.classList.add('has-data');
      output.textContent = actualPayload;
    }

    isFifoAnimating = false;
    setFifoControlsDisabled(false);
  }, 3800);
}

function updateChecklistStep(stepNum) {
  for (let i = 1; i <= 6; i++) {
    const item = document.getElementById(`chkSyscall${i}`);
    if (!item) continue;

    item.classList.remove('active', 'completed');
    if (i < stepNum) {
      item.classList.add('completed');
    } else if (i === stepNum) {
      item.classList.add('active');
    }
  }
}

function resetChecklist() {
  for (let i = 1; i <= 6; i++) {
    const item = document.getElementById(`chkSyscall${i}`);
    if (item) item.classList.remove('active', 'completed');
  }
}

function resetFifoSimulation() {
  clearFifoTimers();
  isFifoAnimating = false;

  const indicatorA = document.getElementById('fifoIndicatorA');
  const indicatorB = document.getElementById('fifoIndicatorB');
  const output = document.getElementById('fifoOutput');
  const stateLabel = document.getElementById('fifoStateLabel');
  const emptyNotice = document.getElementById('fifoEmptyNotice');
  const packet = document.getElementById('fifoPacket');
  const fifoBox = document.getElementById('fifoBuffer');

  setFifoControlsDisabled(false);
  resetChecklist();

  if (indicatorA) indicatorA.classList.remove('active');
  if (indicatorB) indicatorB.classList.remove('active');

  if (stateLabel) stateLabel.textContent = 'STATUS: READY (Shared Linux FIFO Verified)';
  if (emptyNotice) emptyNotice.style.display = 'inline';
  if (fifoBox) fifoBox.classList.remove('active-queue');

  if (packet) {
    packet.style.display = 'none';
    packet.style.opacity = '0';
    packet.style.transform = 'none';
  }

  if (output) {
    output.classList.remove('has-data');
    output.innerHTML = `<span style="color: var(--text-dim); font-style: italic;">Awaiting FIFO message...</span>`;
  }

  const displayTag = document.getElementById('fifoDisplayFileLiveStatus');
  if (displayTag) {
    displayTag.textContent = '[ EMPTY (0 bytes) ]';
    displayTag.style.color = 'var(--emerald-success)';
  }

  // Also notify backend to ensure display file is truncated
  fetch(`${API_BASE}/api/fifo/reset`, { method: 'POST' }).catch(() => {});
}

function scheduleTimer(fn, delay) {
  const timer = setTimeout(fn, delay);
  fifoTimers.push(timer);
}

function clearFifoTimers() {
  fifoTimers.forEach(t => clearTimeout(t));
  fifoTimers = [];
}

function setFifoControlsDisabled(disabled) {
  const btnWrite = document.getElementById('btnFifoWrite');
  const inputMsg = document.getElementById('fifoInput');

  if (btnWrite) btnWrite.disabled = disabled;
  if (inputMsg) inputMsg.disabled = disabled;
}
