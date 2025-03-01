import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Container, Paper, Button, 
  CircularProgress, Alert, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow,
  Chip, IconButton, Tooltip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { simulationApi } from '../services/api';
import VisibilityIcon from '@mui/icons-material/Visibility';
import AddIcon from '@mui/icons-material/Add';
import theme from '../theme';

/**
 * Page for viewing saved simulations
 */
const SimulationList = () => {
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSimulations = async () => {
      try {
        const data = await simulationApi.getAll();
        setSimulations(data);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching simulations:", err);
        setError("Failed to load simulations. Please try again later.");
        setLoading(false);
      }
    };

    fetchSimulations();
  }, []);

  const handleViewSimulation = (id) => {
    navigate(`/simulations/${id}`);
  };

  const handleCreateSimulation = () => {
    navigate('/simulations/create');
  };

  // Format date to a more readable format
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
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
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography 
            variant="h4" 
            component="h1"
            sx={{ color: theme.heading }}
          >
            Simulations
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateSimulation}
            sx={{
              bgcolor: theme.primary,
              color: theme.colors.base3,
              '&:hover': {
                bgcolor: theme.colors.violet,
              }
            }}
          >
            Create Simulation
          </Button>
        </Box>

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

        {simulations.length === 0 ? (
          <Paper 
            elevation={2} 
            sx={{ 
              p: 4, 
              textAlign: 'center',
              bgcolor: theme.cardBackground,
              color: theme.text,
              borderRadius: theme.borderRadius.medium
            }}
          >
            <Typography variant="h6" sx={{ color: theme.heading }}>
              No simulations found
            </Typography>
            <Typography variant="body1" sx={{ mt: 2, mb: 3, color: theme.text }}>
              Create your first simulation to get started
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleCreateSimulation}
              sx={{
                bgcolor: theme.primary,
                color: theme.colors.base3,
                '&:hover': {
                  bgcolor: theme.colors.violet,
                }
              }}
            >
              Create Simulation
            </Button>
          </Paper>
        ) : (
          <TableContainer 
            component={Paper} 
            sx={{ 
              bgcolor: theme.cardBackground,
              borderRadius: theme.borderRadius.medium,
              boxShadow: theme.shadows.medium
            }}
          >
            <Table>
              <TableHead>
                <TableRow sx={{ 
                  '& th': { 
                    color: theme.colors.base2,
                    bgcolor: theme.colors.base01,
                    fontWeight: theme.typography.fontWeight.semibold
                  }
                }}>
                  <TableCell>Name</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Context</TableCell>
                  <TableCell>Entities</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {simulations.map((simulation) => (
                  <TableRow 
                    key={simulation.id}
                    hover
                    sx={{ 
                      '&:hover': { 
                        bgcolor: `${theme.colors.base02} !important`
                      },
                      '& td': { 
                        color: theme.text,
                        borderColor: theme.border
                      }
                    }}
                  >
                    <TableCell>{simulation.name}</TableCell>
                    <TableCell>{formatDate(simulation.created_at)}</TableCell>
                    <TableCell>
                      {simulation.context.length > 70 
                        ? `${simulation.context.substring(0, 70)}...` 
                        : simulation.context}
                    </TableCell>
                    <TableCell>
                      {simulation.entities.length > 0 ? (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {simulation.entities.slice(0, 3).map((entity, index) => (
                            <Chip 
                              key={index} 
                              label={entity.name} 
                              size="small"
                              sx={{ 
                                bgcolor: theme.colors.base01,
                                color: theme.colors.base2,
                                '& .MuiChip-label': { 
                                  px: 1 
                                }
                              }} 
                            />
                          ))}
                          {simulation.entities.length > 3 && (
                            <Chip 
                              label={`+${simulation.entities.length - 3} more`} 
                              size="small"
                              sx={{ 
                                bgcolor: theme.colors.base01,
                                color: theme.colors.base0
                              }} 
                            />
                          )}
                        </Box>
                      ) : (
                        <Typography variant="body2" sx={{ color: theme.colors.base01 }}>
                          No entities
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View Details">
                        <IconButton 
                          onClick={() => handleViewSimulation(simulation.id)}
                          size="small"
                          sx={{ 
                            color: theme.primary,
                            '&:hover': { 
                              color: theme.colors.violet,
                              bgcolor: 'rgba(38, 139, 210, 0.1)'
                            }
                          }}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </Container>
  );
};

export default SimulationList; 