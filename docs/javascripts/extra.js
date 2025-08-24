// Custom JavaScript for Symmetra Documentation

document.addEventListener('DOMContentLoaded', function() {
  // Initialize custom functionality
  initMermaidCustomization();
  initCodeBlockEnhancements();
  initNavigationEnhancements();
  initPerformanceMetrics();
  initSearchEnhancements();
  initLogoSwitching();
});

/**
 * Customize Mermaid diagrams for better appearance
 */
function initMermaidCustomization() {
  // Wait for mermaid to be available
  if (typeof mermaid !== 'undefined') {
    mermaid.initialize({
      theme: 'default',
      themeVariables: {
        primaryColor: '#3f51b5',
        primaryTextColor: '#ffffff',
        primaryBorderColor: '#303f9f',
        lineColor: '#757575',
        sectionBkgColor: '#f5f5f5',
        altSectionBkgColor: '#ffffff',
        gridColor: '#e0e0e0',
        secondaryColor: '#ff4081',
        tertiaryColor: '#e8eaf6'
      },
      flowchart: {
        htmlLabels: true,
        curve: 'basis',
        padding: 10
      },
      sequence: {
        diagramMarginX: 50,
        diagramMarginY: 10,
        actorMargin: 50,
        width: 150,
        height: 65,
        boxMargin: 10,
        boxTextMargin: 5,
        noteMargin: 10,
        messageMargin: 35,
        mirrorActors: true,
        bottomMarginAdj: 1,
        useMaxWidth: true
      },
      gitGraph: {
        mainBranchName: 'main',
        showBranches: true,
        showCommitLabel: true
      }
    });
  }

  // Add loading states to mermaid diagrams
  const mermaidElements = document.querySelectorAll('.mermaid');
  mermaidElements.forEach(element => {
    element.setAttribute('data-processed', 'false');
    
    // Observer to detect when mermaid has processed the diagram
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && element.querySelector('svg')) {
          element.setAttribute('data-processed', 'true');
          observer.disconnect();
        }
      });
    });
    
    observer.observe(element, { childList: true, subtree: true });
  });
}

/**
 * Enhance code blocks with additional functionality
 */
function initCodeBlockEnhancements() {
  // Add copy button animations
  const copyButtons = document.querySelectorAll('.md-clipboard');
  copyButtons.forEach(button => {
    button.addEventListener('click', function() {
      // Add temporary success state
      const originalTitle = this.title;
      this.title = 'Copied!';
      this.classList.add('md-clipboard--success');
      
      setTimeout(() => {
        this.title = originalTitle;
        this.classList.remove('md-clipboard--success');
      }, 2000);
    });
  });

  // Enhance syntax highlighting with line highlighting
  const codeBlocks = document.querySelectorAll('pre code');
  codeBlocks.forEach(block => {
    // Add line numbers if not already present
    if (!block.classList.contains('linenums')) {
      const lines = block.textContent.split('\n');
      if (lines.length > 5) {
        block.classList.add('linenums');
      }
    }
  });
}

/**
 * Add navigation enhancements
 */
function initNavigationEnhancements() {
  // Smooth scrolling for anchor links
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  anchorLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
        
        // Update URL
        history.pushState(null, null, this.getAttribute('href'));
      }
    });
  });

  // Add active section highlighting in TOC
  const tocLinks = document.querySelectorAll('.md-nav__link');
  const sections = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
  
  if (sections.length > 0 && tocLinks.length > 0) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          if (id) {
            // Remove active class from all TOC links
            tocLinks.forEach(link => link.classList.remove('md-nav__link--active'));
            
            // Add active class to current section's TOC link
            const activeLink = document.querySelector(`.md-nav__link[href="#${id}"]`);
            if (activeLink) {
              activeLink.classList.add('md-nav__link--active');
            }
          }
        }
      });
    }, {
      rootMargin: '-20% 0% -60% 0%'
    });

    sections.forEach(section => {
      if (section.id) {
        observer.observe(section);
      }
    });
  }
}

/**
 * Add performance metrics visualization
 */
function initPerformanceMetrics() {
  // Animate metric counters
  const metricValues = document.querySelectorAll('.metric-value');
  
  const animateCounter = (element, target, duration = 2000) => {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        element.textContent = target;
        clearInterval(timer);
      } else {
        element.textContent = Math.floor(current);
      }
    }, 16);
  };

  // Observe metrics and animate when they come into view
  const metricsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.hasAttribute('data-animated')) {
        const value = parseFloat(entry.target.textContent) || 0;
        if (value > 0) {
          entry.target.setAttribute('data-animated', 'true');
          animateCounter(entry.target, value);
        }
      }
    });
  });

  metricValues.forEach(metric => {
    metricsObserver.observe(metric);
  });
}

/**
 * Enhance search functionality
 */
function initSearchEnhancements() {
  const searchInput = document.querySelector('.md-search__input');
  
  if (searchInput) {
    // Add search shortcuts
    document.addEventListener('keydown', function(e) {
      // Ctrl/Cmd + K to focus search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
      
      // Escape to clear search
      if (e.key === 'Escape' && document.activeElement === searchInput) {
        searchInput.value = '';
        searchInput.blur();
      }
    });

    // Add search suggestions based on page content
    const searchSuggestions = [
      'quick start',
      'installation',
      'configuration',
      'claude code integration',
      'mcp tools',
      'guidance capture',
      'vector search',
      'architecture',
      'best practices',
      'troubleshooting'
    ];

    // Add placeholder text rotation
    let suggestionIndex = 0;
    const rotatePlaceholder = () => {
      if (searchInput && !searchInput.value) {
        searchInput.placeholder = `Search... (try "${searchSuggestions[suggestionIndex]}")`;
        suggestionIndex = (suggestionIndex + 1) % searchSuggestions.length;
      }
    };
    
    setInterval(rotatePlaceholder, 3000);
  }
}

/**
 * Add theme-aware enhancements
 */
function initThemeEnhancements() {
  // Listen for theme changes
  const themeObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'attributes' && mutation.attributeName === 'data-md-color-scheme') {
        const theme = document.documentElement.getAttribute('data-md-color-scheme');
        updateMermaidTheme(theme);
      }
    });
  });

  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-md-color-scheme']
  });
}

/**
 * Update mermaid theme based on site theme
 */
function updateMermaidTheme(theme) {
  if (typeof mermaid !== 'undefined') {
    const isDark = theme === 'slate';
    mermaid.initialize({
      theme: isDark ? 'dark' : 'default',
      themeVariables: {
        primaryColor: isDark ? '#5c6bc0' : '#3f51b5',
        primaryTextColor: isDark ? '#ffffff' : '#000000',
        primaryBorderColor: isDark ? '#424242' : '#303f9f',
        lineColor: isDark ? '#ffffff' : '#757575',
        sectionBkgColor: isDark ? '#424242' : '#f5f5f5',
        altSectionBkgColor: isDark ? '#303030' : '#ffffff',
        gridColor: isDark ? '#616161' : '#e0e0e0'
      }
    });

    // Re-render all mermaid diagrams
    const mermaidElements = document.querySelectorAll('.mermaid');
    mermaidElements.forEach(element => {
      if (element.getAttribute('data-processed') === 'true') {
        // Clear and re-render
        element.innerHTML = element.getAttribute('data-original-content') || element.textContent;
        mermaid.init(undefined, element);
      }
    });
  }
}

/**
 * Add keyboard navigation enhancements
 */
function initKeyboardNavigation() {
  document.addEventListener('keydown', function(e) {
    // Alt + Left/Right for page navigation
    if (e.altKey && !e.ctrlKey && !e.metaKey) {
      const prevLink = document.querySelector('.md-footer__link--prev');
      const nextLink = document.querySelector('.md-footer__link--next');
      
      if (e.key === 'ArrowLeft' && prevLink) {
        e.preventDefault();
        prevLink.click();
      } else if (e.key === 'ArrowRight' && nextLink) {
        e.preventDefault();
        nextLink.click();
      }
    }
  });
}

// Initialize all enhancements
document.addEventListener('DOMContentLoaded', function() {
  initThemeEnhancements();
  initKeyboardNavigation();
});

// Add utility functions for other scripts
window.SymmetraDocs = {
  showNotification: function(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.textContent = message;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 12px 24px;
      background: var(--md-primary-fg-color);
      color: white;
      border-radius: 4px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
      z-index: 1000;
      transform: translateX(100%);
      transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Animate out and remove
    setTimeout(() => {
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 300);
    }, duration);
  },
  
  highlightCode: function(selector, lineNumbers) {
    const codeBlocks = document.querySelectorAll(selector);
    codeBlocks.forEach(block => {
      const lines = block.querySelectorAll('.linenodiv pre');
      lineNumbers.forEach(num => {
        const line = lines[num - 1];
        if (line) {
          line.style.backgroundColor = 'rgba(255, 255, 0, 0.2)';
        }
      });
    });
  }
};

/**
 * Logo switching is now handled by Material for MkDocs built-in .only-light and .only-dark classes
 * No custom JavaScript needed for theme-based logo switching
 */
function initLogoSwitching() {
  // Logo switching is now handled automatically by Material theme classes
  // .only-light and .only-dark are built-in Material for MkDocs classes
  console.log('Logo switching handled by Material theme classes (.only-light/.only-dark)');
}