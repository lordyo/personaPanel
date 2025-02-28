import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Button, 
  Card, 
  CardContent, 
  Grid, 
  Chip,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  IconButton,
  Tooltip,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Divider
} from '@mui/material';
import { 
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { dimensionsApi } from '../services/api';
import { Dimension, DimensionType, ImportanceLevel } from '../types';
import { solarizedDark } from '../theme/solarizedDarkTheme';

const DimensionsPage: React.FC = () => {
  const [dimensions, setDimensions] = useState<Dimension[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [currentDimension, setCurrentDimension] = useState<Partial<Dimension> | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    fetchDimensions();
  }, []);

  const fetchDimensions = async () => {
    setLoading(true);
    try {
      const response = await dimensionsApi.getAll();
      if (response.success && response.data) {
        setDimensions(response.data);
      }
    } catch (error) {
      console.error('Error fetching dimensions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (dimension?: Dimension) => {
    if (dimension) {
      setCurrentDimension(dimension);
      setIsEditing(true);
    } else {
      setCurrentDimension({
        name: '',
        description: '',
        type: DimensionType.CATEGORICAL,
        importance: ImportanceLevel.MEDIUM,
        constraints: {}
      });
      setIsEditing(false);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setCurrentDimension(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCurrentDimension(prev => prev ? { ...prev, [name]: value } : null);
  };

  const handleSelectChange = (e: SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    setCurrentDimension(prev => prev ? { ...prev, [name]: value } : null);
  };

  const handleCategoricalConstraintsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const values = e.target.value.split(',').map(val => val.trim());
    setCurrentDimension(prev => {
      if (!prev) return null;
      
      // Create default equal probabilities if not already set
      const probabilities = prev.constraints?.probabilities || values.map(() => 1);
      
      return {
        ...prev,
        constraints: {
          ...prev.constraints,
          allowed_values: values,
          probabilities: probabilities.slice(0, values.length)
        }
      };
    });
  };

  const handleProbabilitiesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const probabilities = e.target.value.split(',').map(val => parseFloat(val.trim())).filter(val => !isNaN(val));
    setCurrentDimension(prev => {
      if (!prev) return null;
      return {
        ...prev,
        constraints: {
          ...prev.constraints,
          probabilities
        }
      };
    });
  };

  const handleNumericConstraintChange = (field: string, value: any) => {
    setCurrentDimension(prev => {
      if (!prev) return null;
      return {
        ...prev,
        constraints: {
          ...prev.constraints,
          [field]: value
        }
      };
    });
  };

  const handleSaveDimension = async () => {
    if (!currentDimension || !currentDimension.name || !currentDimension.description) {
      return;
    }

    try {
      if (isEditing) {
        await dimensionsApi.update(currentDimension.name, currentDimension);
      } else {
        await dimensionsApi.create(currentDimension as Omit<Dimension, 'id'>);
      }
      fetchDimensions();
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving dimension:', error);
    }
  };

  const handleDeleteDimension = async (name: string) => {
    if (window.confirm(`Are you sure you want to delete the dimension "${name}"?`)) {
      try {
        await dimensionsApi.delete(name);
        fetchDimensions();
      } catch (error) {
        console.error('Error deleting dimension:', error);
      }
    }
  };

  const getImportanceColor = (importance: ImportanceLevel) => {
    switch (importance) {
      case ImportanceLevel.HIGH:
        return solarizedDark.red;
      case ImportanceLevel.MEDIUM:
        return solarizedDark.yellow;
      case ImportanceLevel.LOW:
        return solarizedDark.green;
      default:
        return solarizedDark.base0;
    }
  };

  const getTypeColor = (type: DimensionType) => {
    switch (type) {
      case DimensionType.CATEGORICAL:
        return solarizedDark.blue;
      case DimensionType.NUMERIC:
        return solarizedDark.cyan;
      case DimensionType.TEXT:
        return solarizedDark.violet;
      default:
        return solarizedDark.base0;
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1" sx={{ color: solarizedDark.base2 }}>
          Dimensions
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Dimension
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {dimensions.map((dimension) => (
            <Grid item xs={12} md={6} lg={4} key={dimension.name}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="h2" sx={{ color: solarizedDark.base2 }}>
                      {dimension.name}
                    </Typography>
                    <Box>
                      <Tooltip title="Edit">
                        <IconButton 
                          size="small" 
                          onClick={() => handleOpenDialog(dimension)}
                          sx={{ color: solarizedDark.blue }}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDeleteDimension(dimension.name)}
                          sx={{ color: solarizedDark.red }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>
                  
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    {dimension.description}
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Chip 
                      label={`Type: ${dimension.type}`} 
                      size="small" 
                      sx={{ mr: 1, mb: 1, backgroundColor: getTypeColor(dimension.type), color: solarizedDark.base3 }} 
                    />
                    <Chip 
                      label={`Importance: ${dimension.importance}`} 
                      size="small" 
                      sx={{ mr: 1, mb: 1, backgroundColor: getImportanceColor(dimension.importance), color: solarizedDark.base3 }} 
                    />
                  </Box>
                  
                  {dimension.type === DimensionType.CATEGORICAL && dimension.constraints?.allowed_values && (
                    <Box>
                      <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                        Allowed Values:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
                        {dimension.constraints.allowed_values.map((value, index) => (
                          <Chip 
                            key={index} 
                            label={value.toString()} 
                            size="small" 
                            variant="outlined"
                            sx={{ mr: 1, mb: 1 }} 
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                  
                  {dimension.type === DimensionType.NUMERIC && dimension.constraints?.min !== undefined && dimension.constraints?.max !== undefined && (
                    <Box>
                      <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                        Range: {dimension.constraints.min} - {dimension.constraints.max}
                      </Typography>
                      {dimension.constraints.distribution && (
                        <Chip 
                          label={`Distribution: ${dimension.constraints.distribution}`} 
                          size="small" 
                          variant="outlined"
                          sx={{ mr: 1, mb: 1 }} 
                        />
                      )}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>{isEditing ? 'Edit Dimension' : 'Add Dimension'}</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              name="name"
              label="Name"
              fullWidth
              value={currentDimension?.name || ''}
              onChange={handleInputChange}
              disabled={isEditing}
              sx={{ mb: 2 }}
            />
            
            <TextField
              name="description"
              label="Description"
              fullWidth
              multiline
              rows={3}
              value={currentDimension?.description || ''}
              onChange={handleInputChange}
              sx={{ mb: 2 }}
            />
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Type</InputLabel>
              <Select
                name="type"
                value={currentDimension?.type || DimensionType.CATEGORICAL}
                onChange={handleSelectChange}
                label="Type"
              >
                <MenuItem value={DimensionType.CATEGORICAL}>Categorical</MenuItem>
                <MenuItem value={DimensionType.NUMERIC}>Numeric</MenuItem>
                <MenuItem value={DimensionType.TEXT}>Text</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Importance</InputLabel>
              <Select
                name="importance"
                value={currentDimension?.importance || ImportanceLevel.MEDIUM}
                onChange={handleSelectChange}
                label="Importance"
              >
                <MenuItem value={ImportanceLevel.LOW}>Low</MenuItem>
                <MenuItem value={ImportanceLevel.MEDIUM}>Medium</MenuItem>
                <MenuItem value={ImportanceLevel.HIGH}>High</MenuItem>
              </Select>
            </FormControl>
            
            {currentDimension?.type === DimensionType.CATEGORICAL && (
              <>
                <TextField
                  label="Allowed Values (comma separated)"
                  fullWidth
                  value={currentDimension?.constraints?.allowed_values?.join(', ') || ''}
                  onChange={handleCategoricalConstraintsChange}
                  helperText="Enter allowed values separated by commas"
                  sx={{ mb: 2 }}
                />
                
                <TextField
                  label="Probabilities (comma separated)"
                  fullWidth
                  value={currentDimension?.constraints?.probabilities?.join(', ') || ''}
                  onChange={handleProbabilitiesChange}
                  helperText="Enter probability weights for each value (must match the number of allowed values)"
                  sx={{ mb: 2 }}
                />
              </>
            )}
            
            {currentDimension?.type === DimensionType.NUMERIC && (
              <>
                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                  <TextField
                    label="Min Value"
                    type="number"
                    value={currentDimension?.constraints?.min || 0}
                    onChange={(e) => handleNumericConstraintChange('min', parseInt(e.target.value))}
                    sx={{ flex: 1 }}
                  />
                  <TextField
                    label="Max Value"
                    type="number"
                    value={currentDimension?.constraints?.max || 100}
                    onChange={(e) => handleNumericConstraintChange('max', parseInt(e.target.value))}
                    sx={{ flex: 1 }}
                  />
                </Box>
                
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Distribution</InputLabel>
                  <Select
                    value={currentDimension?.constraints?.distribution || 'uniform'}
                    onChange={(e) => handleNumericConstraintChange('distribution', e.target.value)}
                    label="Distribution"
                  >
                    <MenuItem value="uniform">Uniform</MenuItem>
                    <MenuItem value="normal">Normal (Bell Curve)</MenuItem>
                    <MenuItem value="skewed">Skewed</MenuItem>
                  </Select>
                </FormControl>
                
                {currentDimension?.constraints?.distribution === 'normal' && (
                  <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                    <TextField
                      label="Mean"
                      type="number"
                      value={currentDimension?.constraints?.mean || ((currentDimension?.constraints?.min || 0) + (currentDimension?.constraints?.max || 100)) / 2}
                      onChange={(e) => handleNumericConstraintChange('mean', parseInt(e.target.value))}
                      sx={{ flex: 1 }}
                    />
                    <TextField
                      label="Standard Deviation"
                      type="number"
                      value={currentDimension?.constraints?.std_dev || ((currentDimension?.constraints?.max || 100) - (currentDimension?.constraints?.min || 0)) / 6}
                      onChange={(e) => handleNumericConstraintChange('std_dev', parseInt(e.target.value))}
                      sx={{ flex: 1 }}
                    />
                  </Box>
                )}
                
                {currentDimension?.constraints?.distribution === 'skewed' && (
                  <>
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Skew Direction</InputLabel>
                      <Select
                        value={currentDimension?.constraints?.skew_direction || 'right'}
                        onChange={(e) => handleNumericConstraintChange('skew_direction', e.target.value)}
                        label="Skew Direction"
                      >
                        <MenuItem value="left">Left (Higher values more common)</MenuItem>
                        <MenuItem value="right">Right (Lower values more common)</MenuItem>
                      </Select>
                    </FormControl>
                    
                    <TextField
                      label="Skew Factor (0-1)"
                      type="number"
                      inputProps={{ min: 0, max: 1, step: 0.1 }}
                      value={currentDimension?.constraints?.skew_factor || 0.5}
                      onChange={(e) => handleNumericConstraintChange('skew_factor', parseFloat(e.target.value))}
                      fullWidth
                      sx={{ mb: 2 }}
                    />
                  </>
                )}
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSaveDimension} variant="contained" color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DimensionsPage; 