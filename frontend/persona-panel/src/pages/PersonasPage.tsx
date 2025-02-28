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
  TextField,
  InputAdornment,
  IconButton,
  Divider,
  Avatar,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Alert
} from '@mui/material';
import { 
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Person as PersonIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  AutoAwesome as GenerateIcon
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { personasApi } from '../services/api';
import { Persona } from '../types';
import { solarizedDark } from '../theme/solarizedDarkTheme';

const PersonasPage: React.FC = () => {
  const [personas, setPersonas] = useState<Record<string, Persona>>({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [personaToDelete, setPersonaToDelete] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchPersonas();
  }, []);

  const fetchPersonas = async () => {
    setLoading(true);
    try {
      const response = await personasApi.getAll();
      if (response.success && response.data) {
        setPersonas(response.data);
      }
    } catch (error) {
      console.error('Error fetching personas:', error);
      setSnackbar({
        open: true,
        message: 'Failed to load personas',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleDeleteClick = (id: string) => {
    setPersonaToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (personaToDelete) {
      try {
        const response = await personasApi.delete(personaToDelete);
        if (response.success) {
          // Remove from local state
          const newPersonas = { ...personas };
          delete newPersonas[personaToDelete];
          setPersonas(newPersonas);
          
          setSnackbar({
            open: true,
            message: 'Persona deleted successfully',
            severity: 'success',
          });
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
    setPersonaToDelete(null);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setPersonaToDelete(null);
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const filteredPersonas = Object.entries(personas).filter(([_, persona]) => 
    persona.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    persona.traits.some(trait => 
      trait.dimension.toLowerCase().includes(searchTerm.toLowerCase()) ||
      String(trait.value).toLowerCase().includes(searchTerm.toLowerCase())
    ) ||
    persona.backstory.toLowerCase().includes(searchTerm.toLowerCase())
  );

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

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
        <Typography variant="h4" component="h1" sx={{ color: solarizedDark.base2 }}>
          Personas
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            component={Link} 
            to="/personas/generate" 
            variant="contained" 
            color="secondary" 
            startIcon={<GenerateIcon />}
          >
            Generate Personas
          </Button>
          <Button 
            component={Link} 
            to="/personas/new" 
            variant="contained" 
            color="primary" 
            startIcon={<AddIcon />}
          >
            Create Persona
          </Button>
        </Box>
      </Box>

      <Box sx={{ mb: 4 }}>
        <TextField
          fullWidth
          placeholder="Search personas by name, traits, or backstory..."
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                <IconButton>
                  <FilterIcon />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : filteredPersonas.length === 0 ? (
        <Box sx={{ textAlign: 'center', my: 4 }}>
          <Typography variant="h6">
            {searchTerm ? 'No personas match your search' : 'No personas found'}
          </Typography>
          <Typography variant="body1" sx={{ mt: 1 }}>
            {searchTerm ? 'Try a different search term' : 'Create your first persona to get started'}
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {filteredPersonas.map(([id, persona]) => (
            <Grid item xs={12} md={6} lg={4} key={id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar 
                      sx={{ 
                        bgcolor: getAvatarColor(id),
                        color: solarizedDark.base3,
                        mr: 2
                      }}
                    >
                      {getInitials(persona.name)}
                    </Avatar>
                    <Typography variant="h6" component="h2" sx={{ color: solarizedDark.base2 }}>
                      {persona.name}
                    </Typography>
                  </Box>
                  
                  <Divider sx={{ mb: 2 }} />
                  
                  <Box sx={{ mb: 2 }}>
                    {persona.traits.slice(0, 5).map((trait, index) => (
                      <Chip 
                        key={`${id}-${trait.dimension}-${index}`}
                        label={`${trait.dimension}: ${trait.value}`}
                        size="small"
                        sx={{ mr: 1, mb: 1 }}
                      />
                    ))}
                    {persona.traits.length > 5 && (
                      <Chip 
                        label={`+${persona.traits.length - 5} more`}
                        size="small"
                        variant="outlined"
                        sx={{ mr: 1, mb: 1 }}
                      />
                    )}
                  </Box>
                  
                  <Typography variant="body2" sx={{ 
                    mb: 2,
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    {persona.backstory}
                  </Typography>
                </CardContent>
                
                <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                  <Button 
                    startIcon={<ViewIcon />}
                    onClick={() => navigate(`/personas/${id}`)}
                    size="small"
                  >
                    View
                  </Button>
                  <Box>
                    <IconButton 
                      size="small" 
                      onClick={() => navigate(`/personas/${id}/edit`)}
                      sx={{ color: solarizedDark.blue, mr: 1 }}
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton 
                      size="small" 
                      onClick={() => handleDeleteClick(id)}
                      sx={{ color: solarizedDark.red }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </CardActions>
              </Card>
            </Grid>
          ))}
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

export default PersonasPage; 