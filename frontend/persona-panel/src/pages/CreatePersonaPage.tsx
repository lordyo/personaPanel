import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Card, 
  CardContent, 
  Grid, 
  TextField,
  Button, 
  Divider,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Snackbar,
  Alert,
  SelectChangeEvent,
  FormHelperText
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  Add as AddIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { personasApi, dimensionsApi } from '../services/api';
import { Persona, Dimension, Trait } from '../types';
import { solarizedDark } from '../theme/solarizedDarkTheme';

const CreatePersonaPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [dimensions, setDimensions] = useState<Dimension[]>([]);
  const [loadingDimensions, setLoadingDimensions] = useState(true);
  
  const [persona, setPersona] = useState<Omit<Persona, 'id'>>({
    name: '',
    traits: [],
    backstory: '',
  });
  
  const [errors, setErrors] = useState({
    name: '',
    traits: '',
    backstory: ''
  });
  
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });

  useEffect(() => {
    fetchDimensions();
  }, []);

  const fetchDimensions = async () => {
    setLoadingDimensions(true);
    try {
      const response = await dimensionsApi.getAll();
      if (response.success && response.data) {
        setDimensions(response.data);
      }
    } catch (error) {
      console.error('Error fetching dimensions:', error);
      setSnackbar({
        open: true,
        message: 'Failed to load dimensions',
        severity: 'error',
      });
    } finally {
      setLoadingDimensions(false);
    }
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPersona({ ...persona, name: e.target.value });
    if (e.target.value) {
      setErrors({ ...errors, name: '' });
    }
  };

  const handleBackstoryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPersona({ ...persona, backstory: e.target.value });
    if (e.target.value) {
      setErrors({ ...errors, backstory: '' });
    }
  };

  const handleAddTrait = () => {
    const newTraits = [...persona.traits];
    newTraits.push({
      dimension: dimensions[0]?.name || '',
      value: '',
      explanation: ''
    });
    setPersona({ ...persona, traits: newTraits });
    setErrors({ ...errors, traits: '' });
  };

  const handleTraitDimensionChange = (index: number) => (e: SelectChangeEvent) => {
    const newTraits = [...persona.traits];
    newTraits[index].dimension = e.target.value;
    setPersona({ ...persona, traits: newTraits });
  };

  const handleTraitValueChange = (index: number) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTraits = [...persona.traits];
    newTraits[index].value = e.target.value;
    setPersona({ ...persona, traits: newTraits });
  };

  const handleTraitExplanationChange = (index: number) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTraits = [...persona.traits];
    newTraits[index].explanation = e.target.value;
    setPersona({ ...persona, traits: newTraits });
  };

  const handleRemoveTrait = (index: number) => {
    const newTraits = [...persona.traits];
    newTraits.splice(index, 1);
    setPersona({ ...persona, traits: newTraits });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const validateForm = (): boolean => {
    const newErrors = {
      name: '',
      traits: '',
      backstory: ''
    };
    
    let isValid = true;
    
    if (!persona.name.trim()) {
      newErrors.name = 'Name is required';
      isValid = false;
    }
    
    if (persona.traits.length === 0) {
      newErrors.traits = 'At least one trait is required';
      isValid = false;
    } else {
      for (const trait of persona.traits) {
        if (!trait.dimension || !trait.value) {
          newErrors.traits = 'All traits must have a dimension and value';
          isValid = false;
          break;
        }
      }
    }
    
    if (!persona.backstory.trim()) {
      newErrors.backstory = 'Backstory is required';
      isValid = false;
    }
    
    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await personasApi.create(persona);
      if (response.success && response.data) {
        setSnackbar({
          open: true,
          message: 'Persona created successfully',
          severity: 'success',
        });
        
        // Navigate to the new persona after a short delay
        setTimeout(() => {
          if (response.data && response.data.id) {
            navigate(`/personas/${response.data.id}`);
          } else {
            navigate('/personas');
          }
        }, 1500);
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Failed to create persona',
          severity: 'error',
        });
      }
    } catch (error) {
      console.error('Error creating persona:', error);
      setSnackbar({
        open: true,
        message: 'An error occurred while creating the persona',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton 
            onClick={() => navigate('/personas')} 
            sx={{ mr: 2 }}
            aria-label="Back to personas"
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" component="h1" sx={{ color: solarizedDark.base2 }}>
            Create New Persona
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Basic Information */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2" sx={{ mb: 2, color: solarizedDark.blue }}>
                Basic Information
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <TextField
                fullWidth
                label="Name"
                value={persona.name}
                onChange={handleNameChange}
                error={!!errors.name}
                helperText={errors.name}
                sx={{ mb: 3 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Traits */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h5" component="h2" sx={{ color: solarizedDark.cyan }}>
                  Traits
                </Typography>
                <Button 
                  variant="outlined" 
                  color="primary" 
                  startIcon={<AddIcon />}
                  onClick={handleAddTrait}
                  disabled={loadingDimensions}
                >
                  Add Trait
                </Button>
              </Box>
              <Divider sx={{ mb: 3 }} />
              
              {errors.traits && (
                <FormHelperText error sx={{ mb: 2, fontSize: '0.9rem' }}>
                  {errors.traits}
                </FormHelperText>
              )}
              
              {loadingDimensions ? (
                <Typography>Loading dimensions...</Typography>
              ) : persona.traits.length === 0 ? (
                <Typography sx={{ textAlign: 'center', my: 3, color: solarizedDark.base01 }}>
                  No traits added yet. Click "Add Trait" to begin.
                </Typography>
              ) : (
                persona.traits.map((trait, index) => (
                  <Box key={index} sx={{ mb: 3, p: 2, bgcolor: solarizedDark.base03, borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                        Trait {index + 1}
                      </Typography>
                      <IconButton 
                        size="small" 
                        color="error" 
                        onClick={() => handleRemoveTrait(index)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <FormControl fullWidth sx={{ mb: 2 }}>
                          <InputLabel>Dimension</InputLabel>
                          <Select
                            value={trait.dimension}
                            onChange={handleTraitDimensionChange(index)}
                            label="Dimension"
                          >
                            {dimensions.map((dim) => (
                              <MenuItem key={dim.name} value={dim.name}>
                                {dim.name}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Value"
                          value={trait.value}
                          onChange={handleTraitValueChange(index)}
                          sx={{ mb: 2 }}
                        />
                      </Grid>
                      
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Explanation (Optional)"
                          value={trait.explanation || ''}
                          onChange={handleTraitExplanationChange(index)}
                          multiline
                          rows={2}
                        />
                      </Grid>
                    </Grid>
                  </Box>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Backstory */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" component="h2" sx={{ mb: 2, color: solarizedDark.magenta }}>
                Backstory
              </Typography>
              <Divider sx={{ mb: 3 }} />
              
              <TextField
                fullWidth
                label="Backstory"
                value={persona.backstory}
                onChange={handleBackstoryChange}
                multiline
                rows={6}
                error={!!errors.backstory}
                helperText={errors.backstory}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
        <Button 
          variant="outlined" 
          color="inherit" 
          onClick={() => navigate('/personas')}
          sx={{ mr: 2 }}
        >
          Cancel
        </Button>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleSubmit}
          disabled={loading}
        >
          Create Persona
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

export default CreatePersonaPage; 