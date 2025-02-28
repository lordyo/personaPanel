import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import { solarizedDark } from '../theme/solarizedDarkTheme';

const NotFound: React.FC = () => {
  return (
    <Box 
      sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center',
        minHeight: '60vh',
        textAlign: 'center'
      }}
    >
      <Typography variant="h1" component="h1" sx={{ color: solarizedDark.blue, mb: 2 }}>
        404
      </Typography>
      <Typography variant="h4" component="h2" sx={{ color: solarizedDark.base2, mb: 3 }}>
        Page Not Found
      </Typography>
      <Typography variant="body1" sx={{ mb: 4, maxWidth: '600px' }}>
        The page you are looking for doesn't exist or has been moved.
      </Typography>
      <Button 
        component={Link} 
        to="/" 
        variant="contained" 
        color="primary"
        size="large"
      >
        Return to Dashboard
      </Button>
    </Box>
  );
};

export default NotFound; 