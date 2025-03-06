import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, TextField, Button, 
  Container, Paper, FormControl, InputLabel, 
  Select, MenuItem, CircularProgress, Alert
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { entityTypeApi, simulationApi } from '../services/api';
import theme from '../theme';

/**
 * Page for creating and running simulations
 */
const SimulationCreate = () => {
  // States for form data and UI control
  const [entityTypes, setEntityTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedEntityTypes, setSelectedEntityTypes] = useState([]);
  const [simulationName, setSimulationName] = useState('');
  const [simulationContext, setSimulationContext] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  // Fetch entity types on component mount
  useEffect(() => {
    const fetchEntityTypes = async () => {
      try {
        console.log("Fetching entity types...");
        const response = await entityTypeApi.getAll();
        console.log("Entity types response:", response);
        
        if (response && response.status === 'success') {
          setEntityTypes(response.data || []);
          setError(null);
        } else {
          console.error('Error fetching entity types:', response?.message || 'Unknown error');
          setError(`Failed to load entity types: ${response?.message || 'Unknown error'}`);
          setEntityTypes([]);
        }
        setLoading(false);
      } catch (err) {
        console.error("Error fetching entity types:", err);
        setError(`Failed to load entity types: ${err.message || 'Please try again later.'}`);
        setEntityTypes([]);
        setLoading(false);
      }
    };

    fetchEntityTypes();
  }, []);

  // Handle entity type selection
  const handleEntityTypeChange = (event) => {
    setSelectedEntityTypes(event.target.value);
  };

  // Handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    
    try {
      const simulationData = {
        name: simulationName,
        context: simulationContext,
        entity_type_ids: selectedEntityTypes
      };
      
      const response = await simulationApi.create(simulationData);
      console.log('Simulation created:', response);
      navigate('/simulations');
    } catch (err) {
      console.error("Error creating simulation:", err);
      setError("Failed to create simulation. Please check your inputs and try again.");
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="80vh"
        bgcolor={theme.background}
      >
        <CircularProgress sx={{ color: theme.primary }} />
      </Box>
    );
  }

  return (
    <Container maxWidth="md">
      <Box my={4}>
        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom
          sx={{ color: theme.heading }}
        >
          Create New Simulation
        </Typography>
        
        <Paper 
          elevation={3} 
          sx={{ 
            p: 4, 
            mt: 2, 
            bgcolor: theme.cardBackground,
            borderRadius: theme.borderRadius.medium,
            boxShadow: theme.shadows.medium
          }}
        >
          {error && (
            <Alert 
              severity="error" 
              sx={{ 
                mb: 3,
                color: theme.error,
                '& .MuiAlert-icon': {
                  color: theme.error
                }
              }}
            >
              {error}
            </Alert>
          )}
          
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Simulation Name"
              variant="outlined"
              margin="normal"
              required
              value={simulationName}
              onChange={(e) => setSimulationName(e.target.value)}
              sx={{
                mb: 3,
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: theme.border,
                  },
                  '&:hover fieldset': {
                    borderColor: theme.primary,
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: theme.primary,
                  },
                },
                '& .MuiInputLabel-root': {
                  color: theme.text,
                },
                '& .MuiInputBase-input': {
                  color: theme.text,
                },
              }}
            />
            
            <TextField
              fullWidth
              label="Simulation Context"
              variant="outlined"
              margin="normal"
              required
              multiline
              rows={4}
              value={simulationContext}
              onChange={(e) => setSimulationContext(e.target.value)}
              sx={{
                mb: 3,
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: theme.border,
                  },
                  '&:hover fieldset': {
                    borderColor: theme.primary,
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: theme.primary,
                  },
                },
                '& .MuiInputLabel-root': {
                  color: theme.text,
                },
                '& .MuiInputBase-input': {
                  color: theme.text,
                },
              }}
              helperText="Describe the environment or setting for this simulation"
              FormHelperTextProps={{
                sx: { color: theme.text }
              }}
            />
            
            <FormControl 
              fullWidth 
              variant="outlined" 
              margin="normal"
              required
              sx={{
                mb: 4,
                '& .MuiOutlinedInput-root': {
                  '& fieldset': {
                    borderColor: theme.border,
                  },
                  '&:hover fieldset': {
                    borderColor: theme.primary,
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: theme.primary,
                  },
                },
                '& .MuiInputLabel-root': {
                  color: theme.text,
                },
                '& .MuiInputBase-input': {
                  color: theme.text,
                },
                '& .MuiSelect-icon': {
                  color: theme.text,
                },
              }}
            >
              <InputLabel id="entity-type-select-label">Entity Types</InputLabel>
              <Select
                labelId="entity-type-select-label"
                id="entity-type-select"
                multiple
                value={selectedEntityTypes}
                onChange={handleEntityTypeChange}
                label="Entity Types"
                MenuProps={{
                  PaperProps: {
                    sx: {
                      bgcolor: theme.cardBackground,
                      color: theme.text,
                      '& .MuiMenuItem-root': {
                        '&:hover': {
                          bgcolor: theme.colors.base01,
                        },
                        '&.Mui-selected': {
                          bgcolor: `${theme.colors.base01} !important`,
                          color: theme.colors.base2,
                        },
                      },
                    },
                  },
                }}
              >
                {Array.isArray(entityTypes) ? (
                  entityTypes.map((type) => (
                    <MenuItem key={type.id} value={type.id}>
                      {type.name}
                    </MenuItem>
                  ))
                ) : (
                  <MenuItem disabled>No entity types available</MenuItem>
                )}
              </Select>
            </FormControl>
            
            <Box display="flex" justifyContent="flex-end">
              <Button
                variant="contained"
                color="primary"
                type="button"
                onClick={() => navigate('/simulations')}
                disabled={submitting}
                sx={{
                  mr: 2,
                  bgcolor: 'transparent',
                  color: theme.text,
                  borderColor: theme.border,
                  '&:hover': {
                    bgcolor: theme.colors.base01,
                  },
                }}
              >
                Cancel
              </Button>
              <Button
                variant="contained"
                type="submit"
                disabled={submitting}
                sx={{
                  bgcolor: theme.primary,
                  color: theme.colors.base3,
                  '&:hover': {
                    bgcolor: theme.colors.violet,
                  },
                  '&.Mui-disabled': {
                    bgcolor: theme.colors.base01,
                    color: theme.colors.base00,
                  }
                }}
              >
                {submitting ? <CircularProgress size={24} sx={{ color: theme.colors.base3 }} /> : 'Create Simulation'}
              </Button>
            </Box>
          </form>
        </Paper>
      </Box>
    </Container>
  );
};

export default SimulationCreate; 