/**
 * Solarized Dark Theme
 * 
 * This file defines the Solarized Dark color palette and theme settings 
 * for consistent use across the application.
 */

const theme = {
  // Base colors from Solarized Dark palette
  colors: {
    base03: '#002b36',  // Background
    base02: '#073642',  // Card Background
    base01: '#586e75',  // Content
    base00: '#657b83',  // Content
    base0: '#839496',   // Text
    base1: '#93a1a1',   // Heading
    base2: '#eee8d5',   // Highlight
    base3: '#fdf6e3',   // Highlight
    yellow: '#b58900',  // Primary Buttons
    orange: '#cb4b16',  // Notifications
    red: '#dc322f',     // Destructive
    magenta: '#d33682', // Special
    violet: '#6c71c4',  // Special
    blue: '#268bd2',    // Interactive/Links
    cyan: '#2aa198',    // Success
    green: '#859900',   // Positive
  },
  
  // Common semantic color mapping
  background: '#002b36',      // Base background (base03)
  cardBackground: '#073642',  // Secondary background (base02)
  text: '#839496',            // Main text color (base0)
  heading: '#93a1a1',         // Heading text color (base1)
  primary: '#268bd2',         // Primary interactive elements (blue)
  secondary: '#2aa198',       // Secondary interactive elements (cyan)
  accent: '#b58900',          // Accent/highlight elements (yellow)
  error: '#dc322f',           // Error states (red)
  warning: '#cb4b16',         // Warning states (orange)
  success: '#859900',         // Success states (green)
  special: '#d33682',         // Special states (magenta)
  border: 'rgba(131, 148, 150, 0.2)', // Border color based on text color

  // Typography
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    monoFamily: "'Fira Code', monospace",
    fontSize: {
      small: '0.875rem',
      base: '1rem',
      large: '1.25rem',
      xlarge: '1.5rem',
      xxlarge: '2rem',
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.2,
      base: 1.6,
      loose: 2,
    },
  },

  // Spacing
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',  
    md: '1rem',    
    lg: '1.5rem',  
    xl: '2rem',    
    xxl: '3rem',   
  },

  // Borders
  borderRadius: {
    small: '4px',
    medium: '8px',
    large: '12px',
    round: '50%',
  },

  // Shadows
  shadows: {
    small: '0 2px 5px rgba(0, 0, 0, 0.2)',
    medium: '0 5px 15px rgba(0, 0, 0, 0.3)',
    large: '0 10px 25px rgba(0, 0, 0, 0.4)',
  },

  // Transitions
  transitions: {
    fast: '0.2s ease',
    medium: '0.3s ease',
    slow: '0.5s ease',
  },
};

export default theme; 