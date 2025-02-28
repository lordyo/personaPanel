import { createTheme } from '@mui/material/styles';

// Solarized Dark color palette
const solarizedDark = {
  base03: '#002b36',
  base02: '#073642',
  base01: '#586e75',
  base00: '#657b83',
  base0: '#839496',
  base1: '#93a1a1',
  base2: '#eee8d5',
  base3: '#fdf6e3',
  yellow: '#b58900',
  orange: '#cb4b16',
  red: '#dc322f',
  magenta: '#d33682',
  violet: '#6c71c4',
  blue: '#268bd2',
  cyan: '#2aa198',
  green: '#859900',
};

const solarizedDarkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: solarizedDark.blue,
      light: solarizedDark.cyan,
      dark: solarizedDark.violet,
      contrastText: solarizedDark.base3,
    },
    secondary: {
      main: solarizedDark.magenta,
      light: solarizedDark.violet,
      dark: solarizedDark.red,
      contrastText: solarizedDark.base3,
    },
    error: {
      main: solarizedDark.red,
    },
    warning: {
      main: solarizedDark.orange,
    },
    info: {
      main: solarizedDark.cyan,
    },
    success: {
      main: solarizedDark.green,
    },
    background: {
      default: solarizedDark.base03,
      paper: solarizedDark.base02,
    },
    text: {
      primary: solarizedDark.base1,
      secondary: solarizedDark.base0,
      disabled: solarizedDark.base01,
    },
    divider: solarizedDark.base01,
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
      color: solarizedDark.base2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
      color: solarizedDark.base2,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
      color: solarizedDark.base1,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
      color: solarizedDark.base1,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
      color: solarizedDark.base1,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
      color: solarizedDark.base1,
    },
    body1: {
      fontSize: '1rem',
      color: solarizedDark.base0,
    },
    body2: {
      fontSize: '0.875rem',
      color: solarizedDark.base0,
    },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: solarizedDark.base02,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: solarizedDark.base03,
          borderRight: `1px solid ${solarizedDark.base01}`,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: solarizedDark.base02,
          borderRadius: 8,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 4,
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: solarizedDark.base01,
            },
            '&:hover fieldset': {
              borderColor: solarizedDark.blue,
            },
            '&.Mui-focused fieldset': {
              borderColor: solarizedDark.blue,
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          backgroundColor: solarizedDark.base02,
        },
        colorPrimary: {
          backgroundColor: solarizedDark.blue,
        },
        colorSecondary: {
          backgroundColor: solarizedDark.magenta,
        },
      },
    },
  },
});

export default solarizedDarkTheme;
export { solarizedDark }; 