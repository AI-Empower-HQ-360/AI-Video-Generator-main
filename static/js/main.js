// Main JavaScript for AI Empower Heart with accessibility enhancements
document.addEventListener('DOMContentLoaded', function() {
  console.log('AI Empower Heart application loaded');
    
  // Initialize accessibility features
  initAccessibilityFeatures();
    
  // Add smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
            
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        // Focus the target for screen readers
        target.setAttribute('tabindex', '-1');
        target.focus();
                
        target.scrollIntoView({
          behavior: 'smooth'
        });
                
        // Remove tabindex after focus is lost
        target.addEventListener('blur', function() {
          this.removeAttribute('tabindex');
        }, { once: true });
      }
    });
  });
    
  // Enhanced keyboard navigation
  setupKeyboardNavigation();
    
  // Announce page navigation to screen readers
  announcePageLoad();
});

function initAccessibilityFeatures() {
  // Add focus management for dynamic content
  const mainContent = document.getElementById('main-content');
  if (mainContent) {
    mainContent.setAttribute('tabindex', '-1');
  }
    
  // Enhance form controls
  enhanceFormControls();
    
  // Add keyboard shortcuts
  setupKeyboardShortcuts();
    
  // Monitor for accessibility violations in development
  if (window.location.hostname === 'localhost') {
    monitorAccessibility();
  }
}

function enhanceFormControls() {
  // Add aria-describedby for form validation
  const formControls = document.querySelectorAll('input, textarea, select');
  formControls.forEach(control => {
    // Add real-time validation feedback
    control.addEventListener('blur', function() {
      validateFormControl(this);
    });
        
    control.addEventListener('input', function() {
      // Clear validation errors on input
      clearValidationError(this);
    });
  });
}

function validateFormControl(control) {
  const isValid = control.checkValidity();
    
  if (!isValid) {
    showValidationError(control, control.validationMessage);
  } else {
    clearValidationError(control);
  }
}

function showValidationError(control, message) {
  // Remove existing error
  clearValidationError(control);
    
  const errorId = control.id + '-error';
  const errorElement = document.createElement('div');
  errorElement.id = errorId;
  errorElement.className = 'text-danger small mt-1';
  errorElement.setAttribute('role', 'alert');
  errorElement.textContent = message;
    
  control.parentNode.appendChild(errorElement);
  control.setAttribute('aria-describedby', errorId);
  control.setAttribute('aria-invalid', 'true');
    
  // Announce error to screen readers
  announceToScreenReader(`Error: ${message}`);
}

function clearValidationError(control) {
  const errorId = control.id + '-error';
  const errorElement = document.getElementById(errorId);
    
  if (errorElement) {
    errorElement.remove();
    control.removeAttribute('aria-describedby');
    control.setAttribute('aria-invalid', 'false');
  }
}

function setupKeyboardNavigation() {
  // Handle Escape key to close modals/dropdowns
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
      // Close any open Bootstrap modals
      const openModals = document.querySelectorAll('.modal.show');
      openModals.forEach(modal => {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
          bsModal.hide();
        }
      });
            
      // Close any open dropdowns
      const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
      openDropdowns.forEach(dropdown => {
        const toggle = dropdown.previousElementSibling;
        if (toggle && toggle.classList.contains('dropdown-toggle')) {
          const bsDropdown = bootstrap.Dropdown.getInstance(toggle);
          if (bsDropdown) {
            bsDropdown.hide();
          }
        }
      });
    }
  });
    
  // Improve navigation with arrow keys for card grids
  const cardGrids = document.querySelectorAll('.row');
  cardGrids.forEach(grid => {
    const cards = grid.querySelectorAll('.card[tabindex="0"]');
    if (cards.length > 0) {
      setupGridNavigation(cards);
    }
  });
}

function setupGridNavigation(cards) {
  cards.forEach((card, index) => {
    card.addEventListener('keydown', function(event) {
      let newIndex = index;
            
      switch (event.key) {
      case 'ArrowRight':
        newIndex = (index + 1) % cards.length;
        break;
      case 'ArrowLeft':
        newIndex = index === 0 ? cards.length - 1 : index - 1;
        break;
      case 'ArrowDown':
        // Move to next row (assume 4 cards per row)
        newIndex = Math.min(index + 4, cards.length - 1);
        break;
      case 'ArrowUp':
        // Move to previous row
        newIndex = Math.max(index - 4, 0);
        break;
      default:
        return; // Don't prevent default for other keys
      }
            
      event.preventDefault();
      cards[newIndex].focus();
    });
  });
}

function setupKeyboardShortcuts() {
  document.addEventListener('keydown', function(event) {
    // Alt + H for home
    if (event.altKey && event.key.toLowerCase() === 'h') {
      event.preventDefault();
      const homeLink = document.querySelector('a[href="/"]');
      if (homeLink) {
        homeLink.click();
      }
    }
        
    // Alt + D for dashboard
    if (event.altKey && event.key.toLowerCase() === 'd') {
      event.preventDefault();
      const dashboardLink = document.querySelector('a[href="/dashboard"]');
      if (dashboardLink) {
        dashboardLink.click();
      }
    }
        
    // Alt + M for main content
    if (event.altKey && event.key.toLowerCase() === 'm') {
      event.preventDefault();
      const mainContent = document.getElementById('main-content');
      if (mainContent) {
        mainContent.focus();
      }
    }
  });
}

function announcePageLoad() {
  const pageTitle = document.title;
  const mainHeading = document.querySelector('h1');
  const headingText = mainHeading ? mainHeading.textContent : '';
    
  const announcement = `Page loaded: ${pageTitle}. ${headingText}`;
    
  // Delay announcement to ensure page is fully loaded
  setTimeout(() => {
    announceToScreenReader(announcement);
  }, 1000);
}

function announceToScreenReader(message) {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'visually-hidden';
  announcement.textContent = message;
    
  document.body.appendChild(announcement);
    
  setTimeout(() => {
    if (document.body.contains(announcement)) {
      document.body.removeChild(announcement);
    }
  }, 1000);
}

function monitorAccessibility() {
  // Simple accessibility monitoring for development
  console.log('🔍 Monitoring accessibility...');
    
  // Check for missing alt text
  const images = document.querySelectorAll('img:not([alt])');
  if (images.length > 0) {
    console.warn('⚠️ Images without alt text found:', images);
  }
    
  // Check for missing form labels
  const inputs = document.querySelectorAll('input:not([aria-label]):not([aria-labelledby])');
  inputs.forEach(input => {
    const label = document.querySelector(`label[for="${input.id}"]`);
    if (!label) {
      console.warn('⚠️ Input without label found:', input);
    }
  });
    
  // Check for low contrast (basic check)
  checkBasicContrast();
}

function checkBasicContrast() {
  // Basic contrast checking - would need more sophisticated tools for full compliance
  const elements = document.querySelectorAll('*');
  elements.forEach(element => {
    const styles = window.getComputedStyle(element);
    const bgColor = styles.backgroundColor;
    const textColor = styles.color;
        
    // Skip elements with transparent backgrounds
    if (bgColor === 'rgba(0, 0, 0, 0)' || bgColor === 'transparent') {
      return;
    }
        
    // Basic heuristic - would need proper color contrast calculation
    if (textColor === bgColor) {
      console.warn('⚠️ Potential contrast issue:', element);
    }
  });
}

// Utility function to check if user prefers reduced motion
function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

// Enhanced smooth scrolling that respects user preferences
function smoothScrollTo(target, options = {}) {
  const defaultOptions = {
    behavior: prefersReducedMotion() ? 'auto' : 'smooth',
    block: 'start',
    inline: 'nearest'
  };
    
  target.scrollIntoView({ ...defaultOptions, ...options });
}

// Global error handler for better user experience
window.addEventListener('error', function(event) {
  console.error('Application error:', event.error);
  announceToScreenReader('An error occurred. Please try again or contact support if the problem persists.');
});

// Export functions for use in other scripts
window.AIEmpowerHeart = {
  announceToScreenReader,
  smoothScrollTo,
  validateFormControl,
  prefersReducedMotion
};
