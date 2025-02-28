import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Card, 
  CardContent, 
  Grid, 
  TextField, 
  Button, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Slider, 
  CircularProgress, 
  Snackbar, 
  Alert, 
  Divider,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  SelectChangeEvent
} from '@mui/material';
import { 
  AutoAwesome as GenerateIcon,
  Person as PersonIcon,
  Save as SaveIcon,
  Check as CheckIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { personasApi, dimensionsApi } from '../services/api';
import { Persona, Dimension, GenerationSettings } from '../types';
import { solarizedDark } from '../theme/solarizedDarkTheme';

const STORAGE_KEY = 'generated_personas';

const GeneratePersonasPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [dimensions, setDimensions] = useState<Dimension[]>([]);
  const [generatedPersonas, setGeneratedPersonas] = useState<Persona[]>([]);
  const [selectedDimensions, setSelectedDimensions] = useState<string[]>([]);
  const [generationSettings, setGenerationSettings] = useState<GenerationSettings>({
    num_personas: 3,
    diversity_level: 'medium'
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error'
  });

  useEffect(() => {
    fetchDimensions();
    
    // Load any previously generated personas from session storage
    const storedPersonas = sessionStorage.getItem(STORAGE_KEY);
    if (storedPersonas) {
      try {
        const parsedPersonas = JSON.parse(storedPersonas);
        setGeneratedPersonas(parsedPersonas);
      } catch (error) {
        console.error('Error parsing stored personas:', error);
      }
    }
  }, []);

  // Save generated personas to session storage whenever they change
  useEffect(() => {
    if (generatedPersonas.length > 0) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(generatedPersonas));
    }
  }, [generatedPersonas]);

  const fetchDimensions = async () => {
    setLoading(true);
    try {
      const response = await dimensionsApi.getAll();
      if (response.success && response.data) {
        setDimensions(response.data);
        // Select all dimensions by default
        setSelectedDimensions(response.data.map(d => d.name));
      }
    } catch (error) {
      console.error('Error fetching dimensions:', error);
      setSnackbar({
        open: true,
        message: 'Failed to fetch dimensions',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleNumPersonasChange = (_: Event, value: number | number[]) => {
    setGenerationSettings({
      ...generationSettings,
      num_personas: value as number
    });
  };

  const handleDiversityChange = (event: SelectChangeEvent<string>) => {
    setGenerationSettings({
      ...generationSettings,
      diversity_level: event.target.value as 'low' | 'medium' | 'high'
    });
  };

  const handleDimensionsChange = (event: SelectChangeEvent<string[]>) => {
    setSelectedDimensions(event.target.value as string[]);
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleGeneratePersonas = async () => {
    setGenerating(true);
    try {
      // Create a modified settings object that includes selected dimensions
      const settings = {
        ...generationSettings,
        dimensions: selectedDimensions
      };
      
      const response = await personasApi.generate(settings as any);
      if (response.success && response.data) {
        setGeneratedPersonas(response.data);
        setSnackbar({
          open: true,
          message: `Successfully generated ${response.data.length} personas`,
          severity: 'success'
        });
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Failed to generate personas',
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Error generating personas:', error);
      setSnackbar({
        open: true,
        message: 'An error occurred while generating personas',
        severity: 'error'
      });
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveAll = async () => {
    setLoading(true);
    try {
      let savedCount = 0;
      for (const persona of generatedPersonas) {
        const response = await personasApi.create(persona);
        if (response.success) {
          savedCount++;
        }
      }
      
      setSnackbar({
        open: true,
        message: `Saved ${savedCount} of ${generatedPersonas.length} personas to your library`,
        severity: 'success'
      });
      
      // Clear the generated personas after saving
      setGeneratedPersonas([]);
      sessionStorage.removeItem(STORAGE_KEY);
      
      // Navigate to personas page
      navigate('/personas');
    } catch (error) {
      console.error('Error saving personas:', error);
      setSnackbar({
        open: true,
        message: 'An error occurred while saving personas',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleViewPersona = (persona: Persona) => {
    // Store the persona in session storage temporarily
    sessionStorage.setItem('temp_persona', JSON.stringify(persona));
    // Navigate to the preview page
    navigate(`/personas/preview/${persona.id}`);
  };

  const handleClearPersonas = () => {
    setGeneratedPersonas([]);
    sessionStorage.removeItem(STORAGE_KEY);
    setSnackbar({
      open: true,
      message: 'Generated personas cleared',
      severity: 'success'
    });
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  const getAvatarColor = (id: string) => {
    const colors = [
      solarizedDark.blue,
      solarizedDark.cyan,
      solarizedDark.green,
      solarizedDark.magenta,
      solarizedDark.orange,
      solarizedDark.red,
      solarizedDark.violet,
      solarizedDark.yellow
    ];
    
    // Simple hash function to get a consistent color for the same ID
    const hash = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" sx={{ color: solarizedDark.base2 }}>
          Generate Personas
        </Typography>
        <Typography variant="body1" sx={{ mt: 1 }}>
          Automatically generate diverse personas using Claude AI
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Generation Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2" sx={{ mb: 2, color: solarizedDark.blue }}>
                Generation Settings
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Box sx={{ mb: 4 }}>
                <Typography gutterBottom>
                  Number of Personas: {generationSettings.num_personas}
                </Typography>
                <Slider
                  value={generationSettings.num_personas}
                  onChange={handleNumPersonasChange}
                  min={1}
                  max={10}
                  step={1}
                  marks
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

              <FormControl fullWidth sx={{ mb: 4 }}>
                <InputLabel>Diversity Level</InputLabel>
                <Select
                  value={generationSettings.diversity_level}
                  onChange={handleDiversityChange}
                  label="Diversity Level"
                >
                  <MenuItem value="low">Low - Similar personas</MenuItem>
                  <MenuItem value="medium">Medium - Balanced diversity</MenuItem>
                  <MenuItem value="high">High - Maximum diversity</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mb: 4 }}>
                <InputLabel>Dimensions to Include</InputLabel>
                <Select
                  multiple
                  value={selectedDimensions}
                  onChange={handleDimensionsChange}
                  label="Dimensions to Include"
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {(selected as string[]).map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                >
                  {dimensions.map((dimension) => (
                    <MenuItem key={dimension.name} value={dimension.name}>
                      {dimension.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Button
                variant="contained"
                color="primary"
                startIcon={<GenerateIcon />}
                onClick={handleGeneratePersonas}
                disabled={generating || loading || selectedDimensions.length === 0}
                fullWidth
                size="large"
              >
                {generating ? (
                  <>
                    <CircularProgress size={24} sx={{ mr: 1, color: 'white' }} />
                    Generating...
                  </>
                ) : (
                  'Generate Personas'
                )}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Generated Personas */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h5" component="h2" sx={{ color: solarizedDark.green }}>
                  Generated Personas
                </Typography>
                {generatedPersonas.length > 0 && (
                  <Button 
                    variant="outlined" 
                    color="error" 
                    size="small" 
                    startIcon={<DeleteIcon />}
                    onClick={handleClearPersonas}
                  >
                    Clear All
                  </Button>
                )}
              </Box>
              <Divider sx={{ mb: 3 }} />

              {generatedPersonas.length > 0 ? (
                <>
                  <List sx={{ mb: 3 }}>
                    {generatedPersonas.map((persona) => (
                      <ListItem
                        key={persona.id}
                        sx={{
                          mb: 1,
                          border: `1px solid ${solarizedDark.base01}`,
                          borderRadius: 1,
                        }}
                        secondaryAction={
                          <Button
                            variant="outlined"
                            size="small"
                            onClick={() => handleViewPersona(persona)}
                          >
                            View
                          </Button>
                        }
                      >
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: getAvatarColor(persona.id) }}>
                            {getInitials(persona.name)}
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={persona.name}
                          secondary={
                            <Box sx={{ mt: 0.5 }}>
                              {persona.traits.slice(0, 3).map((trait) => (
                                <Chip
                                  key={trait.dimension}
                                  label={`${trait.dimension}: ${trait.value}`}
                                  size="small"
                                  sx={{ mr: 0.5, mb: 0.5 }}
                                />
                              ))}
                              {persona.traits.length > 3 && (
                                <Chip
                                  label={`+${persona.traits.length - 3} more`}
                                  size="small"
                                  variant="outlined"
                                  sx={{ mb: 0.5 }}
                                />
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>

                  <Button
                    variant="contained"
                    color="success"
                    startIcon={<SaveIcon />}
                    onClick={handleSaveAll}
                    disabled={loading}
                    fullWidth
                  >
                    {loading ? (
                      <>
                        <CircularProgress size={24} sx={{ mr: 1, color: 'white' }} />
                        Saving...
                      </>
                    ) : (
                      'Save All to Library'
                    )}
                  </Button>
                </>
              ) : (
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    py: 8,
                  }}
                >
                  <PersonIcon sx={{ fontSize: 60, color: solarizedDark.base01, mb: 2 }} />
                  <Typography variant="body1" color="textSecondary" align="center">
                    No personas generated yet.
                  </Typography>
                  <Typography variant="body2" color="textSecondary" align="center" sx={{ mt: 1 }}>
                    Configure your settings and click "Generate Personas" to create AI-generated personas.
                  </Typography>
                </Box>
              )}
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

export default GeneratePersonasPage; 