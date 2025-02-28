import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Card, 
  CardContent, 
  Grid, 
  Chip,
  CircularProgress,
  Button,
  Divider,
  Avatar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Alert
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Chat as ChatIcon
} from '@mui/icons-material';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { personasApi } from '../services/api';
import { Persona } from '../types';
import { solarizedDark } from '../theme/solarizedDarkTheme';

const PersonaDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [persona, setPersona] = useState<Persona | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });

  useEffect(() => {
    if (id) {
      fetchPersona(id);
    }
  }, [id]);

  const fetchPersona = async (personaId: string) => {
    setLoading(true);
    try {
      const response = await personasApi.getById(personaId);
      if (response.success && response.data) {
        setPersona(response.data);
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Failed to load persona',
          severity: 'error',
        });
      }
    } catch (error) {
      console.error('Error fetching persona:', error);
      setSnackbar({
        open: true,
        message: 'An error occurred while loading the persona',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (id) {
      try {
        const response = await personasApi.delete(id);
        if (response.success) {
          setSnackbar({
            open: true,
            message: 'Persona deleted successfully',
            severity: 'success',
          });
          
          // Navigate back to personas list after a short delay
          setTimeout(() => {
            navigate('/personas');
          }, 1500);
        } else {
          setSnackbar({
            open: true,
            message: response.error || 'Failed to delete persona',
            severity: 'error',
          });
        }
      } catch (error) {
        console.error('Error deleting persona:', error);
        setSnackbar({
          open: true,
          message: 'An error occurred while deleting the persona',
          severity: 'error',
        });
      }
    }
    setDeleteDialogOpen(false);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
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
  const getAvatarColor = (personaId: string) => {
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
    const hash = personaId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
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
            {loading ? 'Loading Persona...' : persona?.name || 'Persona Not Found'}
          </Typography>
        </Box>
        
        {!loading && persona && (
          <Box>
            <Button 
              variant="outlined" 
              color="primary" 
              startIcon={<EditIcon />}
              component={Link}
              to={`/personas/${id}/edit`}
              sx={{ mr: 2 }}
            >
              Edit
            </Button>
            <Button 
              variant="outlined" 
              color="error" 
              startIcon={<DeleteIcon />}
              onClick={handleDeleteClick}
            >
              Delete
            </Button>
          </Box>
        )}
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : !persona ? (
        <Box sx={{ textAlign: 'center', my: 4 }}>
          <Typography variant="h6">
            Persona Not Found
          </Typography>
          <Typography variant="body1" sx={{ mt: 1 }}>
            The requested persona could not be found.
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            component={Link}
            to="/personas"
            sx={{ mt: 3 }}
          >
            Back to Personas
          </Button>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {/* Persona Header */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Avatar 
                    sx={{ 
                      bgcolor: getAvatarColor(id || ''),
                      color: solarizedDark.base3,
                      width: 80,
                      height: 80,
                      fontSize: '2rem',
                      mr: 3
                    }}
                  >
                    {getInitials(persona.name)}
                  </Avatar>
                  <Box>
                    <Typography variant="h4" component="h2" sx={{ color: solarizedDark.base2, mb: 1 }}>
                      {persona.name}
                    </Typography>
                    <Button 
                      variant="outlined" 
                      size="small" 
                      startIcon={<ChatIcon />}
                      component={Link}
                      to={`/discussions/new?persona=${id}`}
                    >
                      Start Discussion
                    </Button>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Traits */}
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" component="h3" sx={{ mb: 2, color: solarizedDark.blue }}>
                  Traits
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Box>
                  {persona.traits.map((trait, index) => (
                    <Box key={index} sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" sx={{ color: solarizedDark.base2 }}>
                        {trait.dimension}
                      </Typography>
                      <Typography variant="body1">
                        {trait.value.toString()}
                      </Typography>
                      {trait.explanation && (
                        <Typography variant="caption" sx={{ display: 'block', mt: 0.5, color: solarizedDark.base01 }}>
                          {trait.explanation}
                        </Typography>
                      )}
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Backstory */}
          <Grid item xs={12} md={8}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" component="h3" sx={{ mb: 2, color: solarizedDark.cyan }}>
                  Backstory
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                  {persona.backstory}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Additional Attributes (if any) */}
          {persona.additional_attributes && Object.keys(persona.additional_attributes).length > 0 && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" component="h3" sx={{ mb: 2, color: solarizedDark.violet }}>
                    Additional Attributes
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  <Grid container spacing={2}>
                    {Object.entries(persona.additional_attributes).map(([key, value]) => (
                      <Grid item xs={12} sm={6} md={4} key={key}>
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" sx={{ color: solarizedDark.base2 }}>
                            {key}
                          </Typography>
                          <Typography variant="body1">
                            {value.toString()}
                          </Typography>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
      >
        <DialogTitle>Delete Persona</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this persona? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error">Delete</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
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

export default PersonaDetail; 