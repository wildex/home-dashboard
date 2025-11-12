import { Appliances } from './components/Appliances';
import { Dashboard } from './components/Dashboard';
import './app.css';
import { Box, Typography, Container } from '@mui/material';

export default function App() {
  return (
    <Container maxWidth="lg" sx={{ py:2 }}>
      <Box component="header" mb={2}>
        <Typography variant="h4" fontWeight={600}>Домашня панель</Typography>
      </Box>
      <Box component="main" display="flex" flexDirection="column" gap={2}>
        <Dashboard />
        <Appliances />
      </Box>
    </Container>
  );
}
