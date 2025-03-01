import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Container, Paper, Button, 
  CircularProgress, Alert, Divider, Grid, Card,
  CardContent, CardHeader, Chip, IconButton
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { simulationApi } from '../services/api';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PersonIcon from '@mui/icons-material/Person';
import theme from '../theme';

/**
 * Page for viewing simulation details
 */
const SimulationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [simulation, setSimulation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSimulation = async () => {
      try {
        const data = await simulationApi.getById(id);
        setSimulation(data);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching simulation:", err);
        setError("Failed to load simulation details. Please try again later.");
        setLoading(false);
      }
    };

    if (id) {
      fetchSimulation();
    }
  }, [id]);

  const handleBack = () => {
    navigate('/simulations');
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

  if (error) {
    return (
      <Container maxWidth="lg">
        <Box my={4}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={handleBack}
            sx={{
              mb: 3,
              color: theme.text,
              '&:hover': {
                color: theme.primary,
                bgcolor: 'transparent',
              }
            }}
          >
            Back to Simulations
          </Button>
          
          <Alert 
            severity="error" 
            sx={{ 
              color: theme.error,
              '& .MuiAlert-icon': {
                color: theme.error
              }
            }}
          >
            {error}
          </Alert>
        </Box>
      </Container>
    );
  }

  if (!simulation) {
    return (
      <Container maxWidth="lg">
        <Box my={4}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={handleBack}
            sx={{
              mb: 3,
              color: theme.text,
              '&:hover': {
                color: theme.primary,
                bgcolor: 'transparent',
              }
            }}
          >
            Back to Simulations
          </Button>
          
          <Alert 
            severity="warning" 
            sx={{ 
              color: theme.warning,
              '& .MuiAlert-icon': {
                color: theme.warning
              }
            }}
          >
            Simulation not found
          </Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box my={4}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBack}
          sx={{
            mb: 3,
            color: theme.text,
            '&:hover': {
              color: theme.primary,
              bgcolor: 'transparent',
            }
          }}
        >
          Back to Simulations
        </Button>

        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom
          sx={{ color: theme.heading }}
        >
          {simulation.name}
        </Typography>

        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            mb: 3,
            color: theme.colors.base00
          }}
        >
          <AccessTimeIcon fontSize="small" sx={{ mr: 1 }} />
          <Typography variant="body2">
            Created {formatDate(simulation.created_at)}
          </Typography>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper 
              elevation={2} 
              sx={{ 
                p: 3, 
                mb: 3, 
                bgcolor: theme.cardBackground,
                borderRadius: theme.borderRadius.medium,
                boxShadow: theme.shadows.small
              }}
            >
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{ color: theme.heading }}
              >
                Context
              </Typography>
              <Typography 
                variant="body1" 
                paragraph
                sx={{ color: theme.text, whiteSpace: 'pre-line' }}
              >
                {simulation.context}
              </Typography>
            </Paper>

            <Paper 
              elevation={2} 
              sx={{ 
                p: 3, 
                bgcolor: theme.cardBackground,
                borderRadius: theme.borderRadius.medium,
                boxShadow: theme.shadows.small
              }}
            >
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{ color: theme.heading }}
              >
                Simulation Results
              </Typography>
              
              <Typography 
                variant="body1"
                sx={{ color: theme.text, whiteSpace: 'pre-line' }}
              >
                {simulation.result ? (
                  simulation.result.content
                ) : (
                  <Box sx={{ 
                    color: theme.colors.base01,
                    fontStyle: 'italic', 
                    py: 2 
                  }}>
                    No simulation results available
                  </Box>
                )}
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper 
              elevation={2} 
              sx={{ 
                p: 3, 
                mb: 3, 
                bgcolor: theme.cardBackground,
                borderRadius: theme.borderRadius.medium,
                boxShadow: theme.shadows.small
              }}
            >
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{ color: theme.heading }}
              >
                Simulation Details
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography 
                  variant="subtitle2"
                  sx={{ color: theme.colors.base1, mb: 0.5 }}
                >
                  Interaction Type
                </Typography>
                <Chip 
                  label={simulation.interaction_type || "Solo"}
                  size="small"
                  sx={{ 
                    bgcolor: theme.colors.base01,
                    color: theme.colors.base2
                  }} 
                />
              </Box>
              
              <Divider sx={{ my: 2, borderColor: theme.border }} />
              
              <Typography 
                variant="subtitle2"
                sx={{ color: theme.colors.base1, mb: 1 }}
              >
                Entities
              </Typography>
              
              {simulation.entities && simulation.entities.length > 0 ? (
                simulation.entities.map((entity, index) => (
                  <Box 
                    key={index}
                    sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      mb: 1,
                      color: theme.text
                    }}
                  >
                    <PersonIcon fontSize="small" sx={{ mr: 1, color: theme.colors.base1 }} />
                    <Typography variant="body2">
                      {entity.name}
                    </Typography>
                  </Box>
                ))
              ) : (
                <Typography 
                  variant="body2"
                  sx={{ color: theme.colors.base01, fontStyle: 'italic' }}
                >
                  No entities in this simulation
                </Typography>
              )}
            </Paper>

            {simulation.entities && simulation.entities.length > 0 && (
              <Paper 
                elevation={2} 
                sx={{ 
                  p: 0, 
                  bgcolor: theme.cardBackground,
                  borderRadius: theme.borderRadius.medium,
                  boxShadow: theme.shadows.small,
                  overflow: 'hidden'
                }}
              >
                <Typography 
                  variant="h6" 
                  sx={{ 
                    p: 2, 
                    color: theme.heading,
                    bgcolor: theme.colors.base02
                  }}
                >
                  Entity Details
                </Typography>
                
                {simulation.entities.map((entity, index) => (
                  <Card 
                    key={index} 
                    elevation={0}
                    sx={{ 
                      mb: 0, 
                      bgcolor: 'transparent',
                      borderRadius: 0,
                      borderBottom: index < simulation.entities.length - 1 ? `1px solid ${theme.border}` : 'none'
                    }}
                  >
                    <CardHeader
                      title={entity.name}
                      titleTypographyProps={{ 
                        variant: 'subtitle1',
                        sx: { color: theme.heading }
                      }}
                      sx={{ pb: 0 }}
                    />
                    <CardContent>
                      {entity.attributes && Object.entries(entity.attributes).length > 0 ? (
                        Object.entries(entity.attributes).map(([key, value]) => (
                          <Box key={key} sx={{ mb: 1 }}>
                            <Typography 
                              variant="caption" 
                              component="div"
                              sx={{ color: theme.colors.base1 }}
                            >
                              {key}
                            </Typography>
                            <Typography 
                              variant="body2"
                              sx={{ color: theme.text }}
                            >
                              {typeof value === 'object' 
                                ? JSON.stringify(value) 
                                : String(value)}
                            </Typography>
                          </Box>
                        ))
                      ) : (
                        <Typography 
                          variant="body2"
                          sx={{ color: theme.colors.base01, fontStyle: 'italic' }}
                        >
                          No attributes defined
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </Paper>
            )}
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default SimulationDetail; 