import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Card, 
  CardContent, 
  Grid, 
  Chip, 
  Button, 
  Divider, 
  CircularProgress,
  Paper,
  Avatar,
  Snackbar,
  Alert
} from '@mui/material';
import { 
  ArrowBack as BackIcon,
  Save as SaveIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { personasApi } from '../services/api';
import { Persona } from '../types';
import { solarizedDark } from '../theme/solarizedDarkTheme';

const PersonaPreviewPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [persona, setPersona] = useState<Persona | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error'
  });

  useEffect(() => {
    // Try to get the persona from session storage
    const storedPersona = sessionStorage.getItem('temp_persona');
    if (storedPersona) {
      try {
        const parsedPersona = JSON.parse(storedPersona);
        setPersona(parsedPersona);
      } catch (error) {
        console.error('Error parsing stored persona:', error);
        setSnackbar({
          open: true,
          message: 'Error loading persona preview',
          severity: 'error'
        });
        navigate('/personas/generate');
      }
    } else {
      // If no persona in session storage, redirect back to generate page
      setSnackbar({
        open: true,
        message: 'No persona to preview',
        severity: 'error'
      });
      navigate('/personas/generate');
    }
  }, [navigate]);

  const handleSavePersona = async () => {
    if (!persona) return;
    
    setSaving(true);
    try {
      console.log('About to save persona:', persona);
      const response = await personasApi.create(persona);
      console.log('Save persona response:', response);
      
      if (response.success && response.data) {
        setSnackbar({
          open: true,
          message: 'Persona saved successfully',
          severity: 'success'
        });
        
        // Clear from session storage
        sessionStorage.removeItem('temp_persona');
        console.log('Removed persona from session storage. Redirecting to personas list...');
        
        // Navigate to personas list
        setTimeout(() => {
          navigate('/personas');
        }, 1500);
      } else {
        console.error('Failed to save persona. API returned error:', response.error);
        setSnackbar({
          open: true,
          message: response.error || 'Failed to save persona',
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Exception while saving persona:', error);
      setSnackbar({
        open: true,
        message: 'An error occurred while saving the persona',
        severity: 'error'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleGoBack = () => {
    navigate('/personas/generate');
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  // Helper function to get initials for avatar
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  // Helper function to get avatar color based on persona id
  const getAvatarColor = (id: string) => {
    const colors = [
      solarizedDark.blue,
      solarizedDark.cyan,
      solarizedDark.green,
      solarizedDark.yellow,
      solarizedDark.orange,
      solarizedDark.red,
      solarizedDark.magenta,
      solarizedDark.violet
    ];
    
    // Simple hash function to get consistent color for same id
    const hash = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
  };

  if (!persona) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Button 
            startIcon={<BackIcon />} 
            onClick={handleGoBack}
            sx={{ mr: 2 }}
          >
            Back
          </Button>
          <Typography variant="h4" component="h1" sx={{ color: solarizedDark.base2 }}>
            Persona Preview
          </Typography>
        </Box>
        <Button
          variant="contained"
          color="primary"
          startIcon={<SaveIcon />}
          onClick={handleSavePersona}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Persona'}
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Persona Header */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar 
                  sx={{ 
                    bgcolor: getAvatarColor(persona.id),
                    color: solarizedDark.base3,
                    width: 64,
                    height: 64,
                    fontSize: 24,
                    mr: 2
                  }}
                >
                  {getInitials(persona.name)}
                </Avatar>
                <Box>
                  <Typography variant="h4" component="h2" sx={{ color: solarizedDark.base2 }}>
                    {persona.name}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Traits */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h5" component="h3" sx={{ mb: 2, color: solarizedDark.blue }}>
                Traits
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Grid container spacing={2}>
                {persona.traits.map((trait) => (
                  <Grid item xs={12} key={trait.dimension}>
                    <Paper 
                      elevation={0} 
                      sx={{ 
                        p: 2, 
                        bgcolor: solarizedDark.base02,
                        borderRadius: 1
                      }}
                    >
                      <Typography variant="subtitle1" component="h4" sx={{ color: solarizedDark.blue, mb: 0.5 }}>
                        {trait.dimension.charAt(0).toUpperCase() + trait.dimension.slice(1)}
                      </Typography>
                      <Typography variant="body1">
                        {trait.value}
                      </Typography>
                      {trait.explanation && (
                        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                          {trait.explanation}
                        </Typography>
                      )}
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Backstory */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h5" component="h3" sx={{ mb: 2, color: solarizedDark.green }}>
                Backstory
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                {persona.backstory}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default PersonaPreviewPage; 