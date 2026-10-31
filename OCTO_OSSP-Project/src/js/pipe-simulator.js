// pipe-simulator.js - Anonymous Pipe Simulation Engine (Smooth Flight)
import { showToast } from './main.js';

let isPipeAnimating = false;
let pipeAnimationTimer = null;

export function initPipeSimulator() {
  const btnSend = document.getElementById('btnPipeSend');
  const btnReset = document.getElementById('btnPipeReset');
  const inputMsg = document.getElementById('pipeInput');

  if (btnSend) {
    btnSend.addEventListener('click', runPipeSimulation);
  }

  if (btnReset) {
    btnReset.addEventListener('click', resetPipeSimulation);
  }

  if (inputMsg) {
    inputMsg.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        runPipeSimulation();
      }
    });
  }
}

function runPipeSimulation() {
  if (isPipeAnimating) return;

  const inputMsg = document.getElementById('pipeInput');
  const text = inputMsg ? inputMsg.value.trim() : '';

  if (!text) {
    showToast('Please enter a message to send!');
    if (inputMsg) inputMsg.focus();
    return;
  }

  isPipeAnimating = true;
  setControlsDisabled(true);

  const packet = document.getElementById('pipePacket');
  const output = document.getElementById('pipeOutput');
  const indicatorA = document.getElementById('pipeIndicatorA');
  const indicatorB = document.getElementById('pipeIndicatorB');

  const processA = document.getElementById('pipeProcessA');
  const processB = document.getElementById('pipeProcessB');
  const pipeChannel = document.getElementById('pipeChannel');

  // Set packet text dynamically to user input
  if (packet) {
    packet.textContent = text;
    packet.title = text;
    packet.style.display = 'block';
    packet.style.transition = 'none';
    
    // Position at Process A
    const rectA = processA.getBoundingClientRect();
    const rectPipe = pipeChannel.getBoundingClientRect();
    const startX = rectA.left + (rectA.width / 2) - (rectPipe.left + rectPipe.width / 2);
    
    packet.style.transform = `translateX(${startX}px) scale(0.8)`;
    packet.style.opacity = '0';
  }

  // Reset output display
  if (output) {
    output.classList.remove('has-data');
    output.innerHTML = `<span style="color: var(--cyan-accent); font-style: italic;">Reading from pipe...</span>`;
  }

  // Step 1 -> Step 2: WRITING (write())
  updatePipeTimeline(2);
  if (indicatorA) indicatorA.classList.add('active');

  // Animation Sequence
  setTimeout(() => {
    // Step 3: TRANSMITTING through pipe
    updatePipeTimeline(3);

    if (packet) {
      packet.style.transition = 'transform 1.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease';
      packet.style.opacity = '1';
      packet.style.transform = 'translateX(0px) scale(1)'; // Center of Pipe Tube
    }

    // Step 4: READING (read()) into Process B
    pipeAnimationTimer = setTimeout(() => {
      updatePipeTimeline(4);
      if (indicatorA) indicatorA.classList.remove('active');
      if (indicatorB) indicatorB.classList.add('active');

      if (packet) {
        const rectB = processB.getBoundingClientRect();
        const rectPipe = pipeChannel.getBoundingClientRect();
        const endX = rectB.left + (rectB.width / 2) - (rectPipe.left + rectPipe.width / 2);

        packet.style.transition = 'transform 1.0s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s ease';
        packet.style.transform = `translateX(${endX}px) scale(0.8)`;
        packet.style.opacity = '0';
      }

      // Step 5: MESSAGE RECEIVED
      setTimeout(() => {
        updatePipeTimeline(5);
        if (indicatorB) indicatorB.classList.remove('active');

        if (output) {
          output.classList.add('has-data');
          output.textContent = text;
        }

        isPipeAnimating = false;
        setControlsDisabled(false);
      }, 700);

    }, 1500);

  }, 400);
}

function updatePipeTimeline(activeStep) {
  for (let i = 1; i <= 5; i++) {
    const stepEl = document.getElementById(`pipeStep${i}`);
    if (!stepEl) continue;

    stepEl.classList.remove('active', 'completed');
    if (i < activeStep) {
      stepEl.classList.add('completed');
    } else if (i === activeStep) {
      stepEl.classList.add('active');
    }
  }
}

function resetPipeSimulation() {
  if (pipeAnimationTimer) clearTimeout(pipeAnimationTimer);
  isPipeAnimating = false;

  const btnSend = document.getElementById('btnPipeSend');
  const inputMsg = document.getElementById('pipeInput');
  const packet = document.getElementById('pipePacket');
  const output = document.getElementById('pipeOutput');
  const indicatorA = document.getElementById('pipeIndicatorA');
  const indicatorB = document.getElementById('pipeIndicatorB');

  setControlsDisabled(false);

  if (indicatorA) indicatorA.classList.remove('active');
  if (indicatorB) indicatorB.classList.remove('active');

  if (packet) {
    packet.style.transition = 'none';
    packet.style.opacity = '0';
    packet.style.transform = 'none';
  }

  if (output) {
    output.classList.remove('has-data');
    output.innerHTML = `<span style="color: var(--text-dim); font-style: italic;">Awaiting transmission...</span>`;
  }

  updatePipeTimeline(1);
}

function setControlsDisabled(disabled) {
  const btnSend = document.getElementById('btnPipeSend');
  const inputMsg = document.getElementById('pipeInput');

  if (btnSend) btnSend.disabled = disabled;
  if (inputMsg) inputMsg.disabled = disabled;
}
