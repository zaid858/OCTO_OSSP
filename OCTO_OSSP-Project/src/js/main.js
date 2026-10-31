// main.js - Core application controller & navigation manager
import { initPipeSimulator } from './pipe-simulator.js';
import { initFifoSimulator } from './fifo-simulator.js';

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initAccordions();
  initPipeSimulator();
  initFifoSimulator();
});

// Toast notification helper
export function showToast(message) {
  const toast = document.getElementById('toastMsg');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 2500);
}

// Navigation Tab Switcher
function initNavigation() {
  const navButtons = document.querySelectorAll('.nav-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  function switchTab(tabId) {
    navButtons.forEach(btn => {
      if (btn.dataset.tab === tabId) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    tabContents.forEach(content => {
      if (content.id === tabId) {
        content.classList.add('active');
      } else {
        content.classList.remove('active');
      }
    });
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.dataset.tab;
      switchTab(targetTab);
    });
  });

  // Overview CTA Button
  const startBtn = document.getElementById('btnStartSim');
  if (startBtn) {
    startBtn.addEventListener('click', () => {
      switchTab('fifo-sim');
    });
  }

  // Back to Simulator CTA Button
  const backBtn = document.getElementById('btnBackToSim');
  if (backBtn) {
    backBtn.addEventListener('click', () => {
      switchTab('pipe-sim');
    });
  }
}

// Accordion Toggles
function initAccordions() {
  setupAccordion('pipeCodeHeader', 'pipeCodeContent', 'pipeCodeArrow');
  setupAccordion('fifoCodeHeader', 'fifoCodeContent', 'fifoCodeArrow');
}

function setupAccordion(headerId, contentId, arrowId) {
  const header = document.getElementById(headerId);
  const content = document.getElementById(contentId);
  const arrow = document.getElementById(arrowId);

  if (header && content) {
    header.addEventListener('click', () => {
      const isOpen = content.classList.contains('open');
      if (isOpen) {
        content.classList.remove('open');
        if (arrow) arrow.textContent = '▼';
      } else {
        content.classList.add('open');
        if (arrow) arrow.textContent = '▲';
      }
    });
  }
}
