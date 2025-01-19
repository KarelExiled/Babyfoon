import { initDashboard } from './dashboard.js';
import { initArchitectureDiagram } from './architecture.js';
import { handleContactForm } from './contact.js';

document.addEventListener('DOMContentLoaded', () => {
  // Initialize all components
  initDashboard();
  initArchitectureDiagram();
  handleContactForm();
  
  // Smooth scroll for navigation
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });
});