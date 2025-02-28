import React, { useState } from 'react';
import { 
  Typography, 
  Box, 
  Card, 
  CardContent, 
  TextField, 
  Button, 
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Grid,
  Alert,
  Snackbar,
  SelectChangeEvent
} from '@mui/material';
import { Save as SaveIcon } from '@mui/icons-material';
import { solarizedDark } from '../theme/solarizedDarkTheme';

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState({
    generation: {
      default_model: 'claude-3-sonnet-20240229',
      temperature: 0.7,
      diversity_preference: 'high',
      backstory_detail_level: 'medium',
    },
    validation: {
      strictness: 'medium',
      coherence_threshold: 0.8,
    },
    persistence: {
      format: 'yaml',
      default_save_location: './personas',
    },
  });

  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleInputChange = (section: string, field: string, value: any) => {
    setSettings({
      ...settings,
      [section]: {
        ...settings[section as keyof typeof settings],
        [field]: value,
      },
    });
  };

  const handleSelectChange = (section: string, field: string) => (event: SelectChangeEvent<string>) => {
    handleInputChange(section, field, event.target.value);
  };

  const handleSliderChange = (section: string, field: string) => (_: Event, value: number | number[]) => {
    handleInputChange(section, field, value);
  };

  const handleSaveSettings = () => {
    // In a real app, this would save to the backend
    console.log('Saving settings:', settings);
    setSnackbar({
      open: true,
      message: 'Settings saved successfully!',
      severity: 'success',
    });
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ color: solarizedDark.base2 }}>
          Settings
        </Typography>
        <Typography variant="body1" sx={{ mt: 1 }}>
          Configure the behavior of the Persona Panel application.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Generation Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2" sx={{ mb: 2, color: solarizedDark.blue }}>
                Generation Settings
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth sx={{ mb: 3 }}>
                    <InputLabel>Default Model</InputLabel>
                    <Select
                      value={settings.generation.default_model}
                      onChange={handleSelectChange('generation', 'default_model')}
                      label="Default Model"
                    >
                      <MenuItem value="claude-3-sonnet-20240229">Claude 3 Sonnet</MenuItem>
                      <MenuItem value="claude-3-opus-20240229">Claude 3 Opus</MenuItem>
                      <MenuItem value="gpt-4">GPT-4</MenuItem>
                      <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Box sx={{ mb: 3 }}>
                    <Typography gutterBottom>Temperature: {settings.generation.temperature}</Typography>
                    <Slider
                      value={settings.generation.temperature}
                      onChange={handleSliderChange('generation', 'temperature')}
                      min={0}
                      max={1}
                      step={0.1}
                      valueLabelDisplay="auto"
                      sx={{
                        '& .MuiSlider-thumb': {
                          backgroundColor: solarizedDark.blue,
                        },
                        '& .MuiSlider-track': {
                          backgroundColor: solarizedDark.blue,
                        },
                      }}
                    />
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth sx={{ mb: 3 }}>
                    <InputLabel>Diversity Preference</InputLabel>
                    <Select
                      value={settings.generation.diversity_preference}
                      onChange={handleSelectChange('generation', 'diversity_preference')}
                      label="Diversity Preference"
                    >
                      <MenuItem value="low">Low</MenuItem>
                      <MenuItem value="medium">Medium</MenuItem>
                      <MenuItem value="high">High</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth sx={{ mb: 3 }}>
                    <InputLabel>Backstory Detail Level</InputLabel>
                    <Select
                      value={settings.generation.backstory_detail_level}
                      onChange={handleSelectChange('generation', 'backstory_detail_level')}
                      label="Backstory Detail Level"
                    >
                      <MenuItem value="low">Low</MenuItem>
                      <MenuItem value="medium">Medium</MenuItem>
                      <MenuItem value="high">High</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Validation Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2" sx={{ mb: 2, color: solarizedDark.cyan }}>
                Validation Settings
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth sx={{ mb: 3 }}>
                    <InputLabel>Strictness</InputLabel>
                    <Select
                      value={settings.validation.strictness}
                      onChange={handleSelectChange('validation', 'strictness')}
                      label="Strictness"
                    >
                      <MenuItem value="low">Low</MenuItem>
                      <MenuItem value="medium">Medium</MenuItem>
                      <MenuItem value="high">High</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Box sx={{ mb: 3 }}>
                    <Typography gutterBottom>Coherence Threshold: {settings.validation.coherence_threshold}</Typography>
                    <Slider
                      value={settings.validation.coherence_threshold}
                      onChange={handleSliderChange('validation', 'coherence_threshold')}
                      min={0}
                      max={1}
                      step={0.1}
                      valueLabelDisplay="auto"
                      sx={{
                        '& .MuiSlider-thumb': {
                          backgroundColor: solarizedDark.cyan,
                        },
                        '& .MuiSlider-track': {
                          backgroundColor: solarizedDark.cyan,
                        },
                      }}
                    />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Persistence Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2" sx={{ mb: 2, color: solarizedDark.violet }}>
                Persistence Settings
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth sx={{ mb: 3 }}>
                    <InputLabel>Format</InputLabel>
                    <Select
                      value={settings.persistence.format}
                      onChange={handleSelectChange('persistence', 'format')}
                      label="Format"
                    >
                      <MenuItem value="yaml">YAML</MenuItem>
                      <MenuItem value="json">JSON</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Default Save Location"
                    value={settings.persistence.default_save_location}
                    onChange={(e) => handleInputChange('persistence', 'default_save_location', e.target.value)}
                    sx={{ mb: 3 }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<SaveIcon />}
          onClick={handleSaveSettings}
          size="large"
        >
          Save Settings
        </Button>
      </Box>

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

export default SettingsPage; 