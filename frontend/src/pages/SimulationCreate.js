import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, TextField, Button, 
  Container, Paper, FormControl, InputLabel, 
  Select, MenuItem, CircularProgress, Alert, FormHelperText,
  RadioGroup, FormControlLabel, Radio, Divider, Chip, List, ListItem,
  ListItemText, ListItemIcon, Checkbox, Card, CardContent, Grid, FormLabel, Switch
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { entityTypeApi, entityApi, simulationApi } from '../services/api';
import theme from '../theme';

/**
 * Page for creating and running simulations
 */
const SimulationCreate = () => {
  const location = useLocation();
  const continuationData = location.state?.continuationData;

  // States for form data and UI control
  const [entityTypes, setEntityTypes] = useState([]);
  const [entities, setEntities] = useState({});  // Map of entity type ID to entities array
  const [loading, setLoading] = useState(true);
  const [loadingEntities, setLoadingEntities] = useState(false);
  const [error, setError] = useState(null);
  
  // Form state
  const [simulationName, setSimulationName] = useState('');
  const [simulationContext, setSimulationContext] = useState('');
  const [interactionType, setInteractionType] = useState('dyadic');
  const [selectedEntityTypeId, setSelectedEntityTypeId] = useState('');
  const [selectedEntityIds, setSelectedEntityIds] = useState([]);
  const [nRounds, setNRounds] = useState(1);
  const [isContinuation, setIsContinuation] = useState(false);
  const [lastRoundNumber, setLastRoundNumber] = useState(0);
  const [previousInteraction, setPreviousInteraction] = useState('');
  
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  // Set form values from continuation data if available
  useEffect(() => {
    if (continuationData) {
      setSimulationContext(continuationData.context || '');
      setInteractionType(continuationData.interaction_type || 'dyadic');
      setNRounds(continuationData.n_rounds || 3);
      setLastRoundNumber(continuationData.last_round_number || 0);
      setPreviousInteraction(continuationData.previous_interaction || '');
      setIsContinuation(true);
      setSimulationName(`Continuation ${new Date().toLocaleString()}`);
      
      if (continuationData.entity_ids && continuationData.entity_ids.length > 0) {
        setSelectedEntityIds(continuationData.entity_ids);
      }
    }
  }, [continuationData]);

  // Fetch entity types on component mount
  useEffect(() => {
    const fetchEntityTypes = async () => {
      try {
        console.log("Fetching entity types...");
        const response = await entityTypeApi.getAll();
        console.log("Entity types response:", response);
        
        if (response && response.status === 'success') {
          setEntityTypes(response.data || []);
          
          // If there's at least one entity type, select it by default
          if (response.data && response.data.length > 0) {
            setSelectedEntityTypeId(response.data[0].id);
          }
          
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

  // Fetch entities when entity type is selected
  useEffect(() => {
    const fetchEntitiesForType = async (entityTypeId) => {
      if (!entityTypeId) return;
      
      // Skip if we already loaded this entity type's entities
      if (entities[entityTypeId]) return;
      
      setLoadingEntities(true);
      try {
        console.log(`Fetching entities for type ${entityTypeId}...`);
        const response = await entityApi.getByType(entityTypeId);
        console.log("Entities response:", response);
        
        if (response && response.status === 'success') {
          setEntities(prev => ({
            ...prev,
            [entityTypeId]: response.data || []
          }));
          setError(null);
        } else {
          console.error('Error fetching entities:', response?.message || 'Unknown error');
          setError(`Failed to load entities: ${response?.message || 'Unknown error'}`);
        }
      } catch (err) {
        console.error("Error fetching entities:", err);
        setError(`Failed to load entities: ${err.message || 'Please try again later.'}`);
      } finally {
        setLoadingEntities(false);
      }
    };

    if (selectedEntityTypeId) {
      fetchEntitiesForType(selectedEntityTypeId);
    }
  }, [selectedEntityTypeId, entities]);

  // Handle interaction type change
  const handleInteractionTypeChange = (event) => {
    const newType = event.target.value;
    setInteractionType(newType);
    
    // Clear selected entities if changing interaction type
    setSelectedEntityIds([]);
  };

  // Handle entity type selection
  const handleEntityTypeChange = (event) => {
    setSelectedEntityTypeId(event.target.value);
  };
  
  // Handle entity selection/deselection
  const handleEntityToggle = (entityId) => {
    const currentIndex = selectedEntityIds.indexOf(entityId);
    const newSelectedEntityIds = [...selectedEntityIds];
    
    if (currentIndex === -1) {
      // Add entity if it doesn't violate max constraints for the interaction type
      if (interactionType === 'solo' && newSelectedEntityIds.length >= 1) {
        // Replace the entity for solo interaction
        newSelectedEntityIds[0] = entityId;
      } else if (interactionType === 'dyadic' && newSelectedEntityIds.length >= 2) {
        // Replace the second entity for dyadic interaction
        newSelectedEntityIds[1] = entityId;
      } else {
        // Add entity
        newSelectedEntityIds.push(entityId);
      }
    } else {
      // Remove entity
      newSelectedEntityIds.splice(currentIndex, 1);
    }
    
    setSelectedEntityIds(newSelectedEntityIds);
  };

  // Handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    
    try {
      // Validate selections based on interaction type
      if (interactionType === 'solo' && selectedEntityIds.length !== 1) {
        setError("Solo interaction requires exactly 1 entity");
        setSubmitting(false);
        return;
      } else if (interactionType === 'dyadic' && selectedEntityIds.length !== 2) {
        setError("Dyadic interaction requires exactly 2 entities");
        setSubmitting(false);
        return;
      } else if (interactionType === 'group' && selectedEntityIds.length < 3) {
        setError("Group interaction requires at least 3 entities");
        setSubmitting(false);
        return;
      }
      
      const simulationData = {
        name: simulationName,
        context: simulationContext,
        interaction_type: interactionType,
        entity_ids: selectedEntityIds,
        n_rounds: nRounds
      };
      
      // Add continuation parameters if this is a continuation
      if (isContinuation) {
        simulationData.last_round_number = lastRoundNumber;
        simulationData.previous_interaction = previousInteraction;
      }
      
      console.log("Creating simulation with data:", simulationData);
      const response = await simulationApi.create(simulationData);
      console.log('Simulation created:', response);
      navigate('/simulations');
    } catch (err) {
      console.error("Error creating simulation:", err);
      setError(`Failed to create simulation: ${err.message || 'Please check your inputs and try again.'}`);
      setSubmitting(false);
    }
  };

  // Find entity by ID across all entity types
  const findEntityById = (entityId) => {
    for (const typeId in entities) {
      const entity = entities[typeId].find(e => e.id === entityId);
      if (entity) return entity;
    }
    return null;
  };

  // Render selected entities
  const renderSelectedEntities = () => {
    return (
      <Box mt={2}>
        <Typography variant="h6" sx={{ color: theme.heading, mb: 1 }}>
          Selected Entities ({selectedEntityIds.length})
        </Typography>
        
        {selectedEntityIds.length === 0 ? (
          <Typography sx={{ color: theme.textSecondary, fontStyle: 'italic' }}>
            No entities selected
          </Typography>
        ) : (
          <Grid container spacing={2}>
            {selectedEntityIds.map((entityId, index) => {
              const entity = findEntityById(entityId);
              if (!entity) return null;
              
              return (
                <Grid item xs={12} sm={6} md={4} key={entityId}>
                  <Card 
                    sx={{ 
                      bgcolor: theme.colors.base01,
                      color: theme.text,
                      position: 'relative'
                    }}
                  >
                    <CardContent>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                        {entity.name}
                      </Typography>
                      <Typography variant="body2" sx={{ color: theme.textSecondary, mb: 1 }}>
                        Type: {entityTypes.find(t => t.id === entity.entity_type_id)?.name || 'Unknown'}
                      </Typography>
                      <Chip 
                        label={`Entity ${index + 1}`} 
                        size="small"
                        sx={{ 
                          position: 'absolute',
                          top: 8,
                          right: 8,
                          bgcolor: theme.colors.blue,
                          color: theme.buttonText,
                        }}
                      />
                      <Button
                        size="small"
                        variant="outlined"
                        color="error"
                        onClick={() => handleEntityToggle(entityId)}
                        sx={{ 
                          mt: 1, 
                          borderColor: theme.error,
                          color: theme.error,
                          '&:hover': {
                            borderColor: theme.error,
                            bgcolor: 'rgba(244, 67, 54, 0.1)',
                          }
                        }}
                      >
                        Remove
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        )}
      </Box>
    );
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
    <Container maxWidth="lg">
      <Box my={4}>
        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom
          sx={{ color: theme.heading }}
        >
          {isContinuation ? 'Continue Simulation' : 'Create New Simulation'}
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
            <Grid container spacing={3}>
              {/* Left Column - Basic Info */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" sx={{ color: theme.heading, mb: 2 }}>
                  Basic Information
                </Typography>
                
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
                
                <FormControl component="fieldset" sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" sx={{ color: theme.heading, mb: 1 }}>
                    Interaction Type
                  </Typography>
                  <RadioGroup
                    row
                    name="interaction-type"
                    value={interactionType}
                    onChange={handleInteractionTypeChange}
                  >
                    <FormControlLabel 
                      value="solo" 
                      control={<Radio />} 
                      label="Solo (1 entity)" 
                      sx={{ color: theme.text }}
                      disabled={isContinuation && continuationData}
                    />
                    <FormControlLabel 
                      value="dyadic" 
                      control={<Radio />} 
                      label="Dyadic (2 entities)" 
                      sx={{ color: theme.text }}
                      disabled={isContinuation && continuationData}
                    />
                    <FormControlLabel 
                      value="group" 
                      control={<Radio />} 
                      label="Group (3+ entities)" 
                      sx={{ color: theme.text }}
                      disabled={isContinuation && continuationData}
                    />
                  </RadioGroup>
                  {isContinuation && continuationData && (
                    <FormHelperText sx={{ color: theme.textSecondary }}>
                      Interaction type cannot be changed for continuations
                    </FormHelperText>
                  )}
                </FormControl>
                
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                  <FormControl fullWidth>
                    <FormLabel>Number of Dialogue Rounds</FormLabel>
                    <TextField
                      id="n-rounds"
                      type="number"
                      value={nRounds}
                      onChange={(e) => setNRounds(Math.max(1, parseInt(e.target.value) || 1))}
                      fullWidth
                      variant="outlined"
                      margin="normal"
                      helperText="Each round typically includes a thought and dialogue from each participant. More rounds create longer, more detailed interactions."
                      inputProps={{ min: 1, max: 10 }}
                    />
                  </FormControl>
                  
                  {!continuationData && (
                    <FormControl sx={{ width: '45%' }}>
                      <Button
                        variant="outlined"
                        color="primary"
                        onClick={() => setIsContinuation(!isContinuation)}
                        sx={{
                          borderColor: theme.border,
                          color: theme.text,
                          '&:hover': {
                            borderColor: theme.primary,
                            backgroundColor: 'rgba(97, 175, 254, 0.1)',
                          },
                        }}
                      >
                        {isContinuation ? "Remove Continuation Settings" : "Add Continuation Settings"}
                      </Button>
                    </FormControl>
                  )}
                </Box>
                
                {(isContinuation || continuationData) && (
                  <Box sx={{ mb: 3, p: 2, border: `1px solid ${theme.border}`, borderRadius: theme.borderRadius.small }}>
                    <Typography variant="h6" gutterBottom sx={{ color: theme.heading }}>
                      Continuation Settings
                    </Typography>
                    
                    <TextField
                      fullWidth
                      label="Last Round Number"
                      variant="outlined"
                      type="number"
                      InputProps={{ inputProps: { min: 0 } }}
                      value={lastRoundNumber}
                      onChange={(e) => setLastRoundNumber(parseInt(e.target.value) || 0)}
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
                      helperText="The last round number from the previous interaction"
                      FormHelperTextProps={{
                        sx: { color: theme.text }
                      }}
                    />
                    
                    <TextField
                      fullWidth
                      label="Previous Interaction"
                      variant="outlined"
                      multiline
                      rows={6}
                      value={previousInteraction}
                      onChange={(e) => setPreviousInteraction(e.target.value)}
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
                      helperText="Paste the previous interaction content here for continuation"
                      FormHelperTextProps={{
                        sx: { color: theme.text }
                      }}
                    />
                  </Box>
                )}
              </Grid>
              
              {/* Right Column - Entity Selection */}
              <Grid item xs={12} md={6}>
                <Typography variant="h6" sx={{ color: theme.heading, mb: 2 }}>
                  Entity Selection
                </Typography>
                
                <FormControl 
                  fullWidth 
                  variant="outlined" 
                  margin="normal"
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
                    '& .MuiSelect-icon': {
                      color: theme.text,
                    },
                  }}
                  disabled={isContinuation && continuationData}
                >
                  <InputLabel id="entity-type-select-label">Select Entity Type</InputLabel>
                  <Select
                    labelId="entity-type-select-label"
                    id="entity-type-select"
                    value={selectedEntityTypeId}
                    onChange={handleEntityTypeChange}
                    label="Select Entity Type"
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
                  {isContinuation && continuationData && (
                    <FormHelperText sx={{ color: theme.textSecondary }}>
                      Entities cannot be changed for continuations
                    </FormHelperText>
                  )}
                </FormControl>
                
                {loadingEntities ? (
                  <Box display="flex" justifyContent="center" my={4}>
                    <CircularProgress size={30} sx={{ color: theme.primary }} />
                  </Box>
                ) : (
                  <>
                    {selectedEntityTypeId && entities[selectedEntityTypeId] && (
                      <Paper 
                        elevation={0} 
                        sx={{ 
                          maxHeight: 300, 
                          overflow: 'auto',
                          bgcolor: theme.colors.base01,
                          borderRadius: theme.borderRadius.small,
                          mb: 3,
                          ...(isContinuation && continuationData ? { opacity: 0.6, pointerEvents: 'none' } : {})
                        }}
                      >
                        <List dense>
                          {entities[selectedEntityTypeId].map((entity) => {
                            const isSelected = selectedEntityIds.includes(entity.id);
                            
                            return (
                              <ListItem 
                                key={entity.id}
                                button
                                onClick={() => handleEntityToggle(entity.id)}
                                sx={{
                                  borderBottom: `1px solid ${theme.colors.base02}`,
                                  '&:last-child': {
                                    borderBottom: 'none',
                                  },
                                  bgcolor: isSelected ? 'rgba(97, 175, 254, 0.1)' : 'transparent',
                                }}
                              >
                                <ListItemIcon>
                                  <Checkbox
                                    edge="start"
                                    checked={isSelected}
                                    tabIndex={-1}
                                    disableRipple
                                    sx={{
                                      color: theme.text,
                                      '&.Mui-checked': {
                                        color: theme.colors.blue,
                                      },
                                    }}
                                  />
                                </ListItemIcon>
                                <ListItemText 
                                  primary={entity.name} 
                                  secondary={entity.description?.substring(0, 60) + '...'}
                                  primaryTypographyProps={{
                                    sx: { color: theme.text }
                                  }}
                                  secondaryTypographyProps={{
                                    sx: { color: theme.textSecondary }
                                  }}
                                />
                              </ListItem>
                            );
                          })}
                        </List>
                      </Paper>
                    )}
                    
                    {!isContinuation && renderSelectedEntities()}
                  </>
                )}
                
                <Box sx={{ mt: 4 }}>
                  <Typography variant="subtitle2" color={theme.textSecondary} gutterBottom>
                    {interactionType === 'solo' ? 
                      'Select exactly 1 entity for solo interaction' : 
                      interactionType === 'dyadic' ? 
                      'Select exactly 2 entities for dyadic interaction' : 
                      'Select at least 3 entities for group interaction'}
                  </Typography>
                  
                  <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    mt: 2
                  }}>
                    <Chip 
                      label={`${selectedEntityIds.length} entities selected`}
                      sx={{ 
                        bgcolor: theme.colors.base01,
                        color: theme.text,
                        mb: { xs: 2, sm: 0 }
                      }}
                    />
                    
                    <Button 
                      variant="contained" 
                      color="primary" 
                      type="submit"
                      disabled={submitting}
                      sx={{
                        bgcolor: theme.primary,
                        color: theme.buttonText,
                        '&:hover': {
                          bgcolor: theme.primaryHover,
                        },
                        '&.Mui-disabled': {
                          bgcolor: theme.disabled,
                          color: theme.disabledText,
                        },
                      }}
                    >
                      {submitting ? (
                        <CircularProgress size={24} sx={{ color: theme.buttonText }} />
                      ) : isContinuation ? (
                        "Continue Simulation"
                      ) : (
                        "Create Simulation"
                      )}
                    </Button>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </form>
        </Paper>
      </Box>
    </Container>
  );
};

export default SimulationCreate; 