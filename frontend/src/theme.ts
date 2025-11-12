import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#1864ab' },
    secondary: { main: '#364fc7' },
    background: { default: '#10151a', paper: '#1b2530' },
  },
  shape: { borderRadius: 10 },
  components: {
    MuiButton: { styleOverrides: { root: { textTransform: 'none', borderRadius: 6 } } },
  }
});

export default theme;
