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
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  OutlinedInput,
  Slider
} from '@mui/material';
import { 
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Forum as ForumIcon
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { discussionsApi, personasApi } from '../services/api';
import { Discussion, Persona, DiscussionSettings } from '../types';
import { solarizedDark } from '../theme/solarizedDarkTheme';

const DiscussionsPage: React.FC = () => {
  const [discussions, setDiscussions] = useState<Record<string, Discussion>>({});
  const [personas, setPersonas] = useState<Record<string, Persona>>({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [discussionToDelete, setDiscussionToDelete] = useState<string | null>(null);
  const [newDiscussion, setNewDiscussion] = useState<DiscussionSettings>({
    personas: [],
    topic: '',
    format: 'conversation',
    num_rounds: 3
  });
  const [creatingDiscussion, setCreatingDiscussion] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [discussionsResponse, personasResponse] = await Promise.all([
        discussionsApi.getAll(),
        personasApi.getAll()
      ]);
      
      if (discussionsResponse.success && discussionsResponse.data) {
        setDiscussions(discussionsResponse.data);
      }
      
      if (personasResponse.success && personasResponse.data) {
        setPersonas(personasResponse.data);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setSnackbar({
        open: true,
        message: 'Failed to load discussions',
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
    setDiscussionToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (discussionToDelete) {
      try {
        const response = await discussionsApi.delete(discussionToDelete);
        if (response.success) {
          // Remove from local state
          const newDiscussions = { ...discussions };
          delete newDiscussions[discussionToDelete];
          setDiscussions(newDiscussions);
          
          setSnackbar({
            open: true,
            message: 'Discussion deleted successfully',
            severity: 'success',
          });
        } else {
          setSnackbar({
            open: true,
            message: response.error || 'Failed to delete discussion',
            severity: 'error',
          });
        }
      } catch (error) {
        console.error('Error deleting discussion:', error);
        setSnackbar({
          open: true,
          message: 'An error occurred while deleting the discussion',
          severity: 'error',
        });
      }
    }
    setDeleteDialogOpen(false);
    setDiscussionToDelete(null);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setDiscussionToDelete(null);
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleCreateDialogOpen = () => {
    setNewDiscussion({
      personas: [],
      topic: '',
      format: 'conversation',
      num_rounds: 3
    });
    setCreateDialogOpen(true);
  };

  const handleCreateDialogClose = () => {
    setCreateDialogOpen(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewDiscussion(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (e: SelectChangeEvent<string>) => {
    const { name, value } = e.target;
    setNewDiscussion(prev => ({ ...prev, [name]: value }));
  };

  const handlePersonasChange = (e: SelectChangeEvent<string[]>) => {
    const value = e.target.value as string[];
    setNewDiscussion(prev => ({ ...prev, personas: value }));
  };

  const handleRoundsChange = (_: Event, value: number | number[]) => {
    setNewDiscussion(prev => ({ ...prev, num_rounds: value as number }));
  };

  const handleCreateDiscussion = async () => {
    if (!newDiscussion.topic || newDiscussion.personas.length < 2) {
      setSnackbar({
        open: true,
        message: 'Please provide a topic and select at least two personas',
        severity: 'error',
      });
      return;
    }

    setCreatingDiscussion(true);
    try {
      const response = await discussionsApi.create(newDiscussion);
      if (response.success && response.data) {
        // Add to local state
        setDiscussions(prev => ({
          ...prev,
          [response.data!.id]: response.data!
        }));
        
        setSnackbar({
          open: true,
          message: 'Discussion created successfully',
          severity: 'success',
        });
        
        // Navigate to the new discussion
        navigate(`/discussions/${response.data.id}`);
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Failed to create discussion',
          severity: 'error',
        });
      }
    } catch (error) {
      console.error('Error creating discussion:', error);
      setSnackbar({
        open: true,
        message: 'An error occurred while creating the discussion',
        severity: 'error',
      });
    } finally {
      setCreatingDiscussion(false);
      setCreateDialogOpen(false);
    }
  };

  const filteredDiscussions = Object.entries(discussions).filter(([_, discussion]) => 
    discussion.settings.topic.toLowerCase().includes(searchTerm.toLowerCase()) ||
    discussion.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
    discussion.settings.personas.some(personaId => 
      personas[personaId]?.name.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1" sx={{ color: solarizedDark.base2 }}>
          Discussions
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<AddIcon />}
          onClick={handleCreateDialogOpen}
        >
          Create Discussion
        </Button>
      </Box>

      <Box sx={{ mb: 4 }}>
        <TextField
          fullWidth
          placeholder="Search discussions by topic, content, or participants..."
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
      ) : filteredDiscussions.length === 0 ? (
        <Box sx={{ textAlign: 'center', my: 4 }}>
          <Typography variant="h6">
            {searchTerm ? 'No discussions match your search' : 'No discussions found'}
          </Typography>
          <Typography variant="body1" sx={{ mt: 1 }}>
            {searchTerm ? 'Try a different search term' : 'Create your first discussion to get started'}
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {filteredDiscussions.map(([id, discussion]) => (
            <Grid item xs={12} md={6} key={id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <ForumIcon sx={{ color: solarizedDark.magenta, mr: 2 }} />
                    <Typography variant="h6" component="h2" sx={{ color: solarizedDark.base2 }}>
                      {discussion.settings.topic}
                    </Typography>
                  </Box>
                  
                  <Divider sx={{ mb: 2 }} />
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                      Participants:
                    </Typography>
                    {discussion.settings.personas.map(personaId => (
                      <Chip 
                        key={personaId}
                        label={personas[personaId]?.name || 'Unknown'}
                        size="small"
                        sx={{ mr: 1, mb: 1 }}
                      />
                    ))}
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Chip 
                      label={`Format: ${discussion.settings.format}`}
                      size="small"
                      sx={{ mr: 1, mb: 1, backgroundColor: solarizedDark.violet, color: solarizedDark.base3 }}
                    />
                    <Chip 
                      label={`Rounds: ${discussion.settings.num_rounds}`}
                      size="small"
                      sx={{ mr: 1, mb: 1, backgroundColor: solarizedDark.blue, color: solarizedDark.base3 }}
                    />
                    <Chip 
                      label={`Created: ${formatDate(discussion.created_at)}`}
                      size="small"
                      sx={{ mr: 1, mb: 1 }}
                      variant="outlined"
                    />
                  </Box>
                  
                  <Typography variant="body2" sx={{ 
                    mb: 2,
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    {discussion.content.split('\n').slice(2, 5).join(' ')}...
                  </Typography>
                </CardContent>
                
                <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                  <Button 
                    startIcon={<ViewIcon />}
                    onClick={() => navigate(`/discussions/${id}`)}
                    size="small"
                  >
                    View Discussion
                  </Button>
                  <IconButton 
                    size="small" 
                    onClick={() => handleDeleteClick(id)}
                    sx={{ color: solarizedDark.red }}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create Discussion Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={handleCreateDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create New Discussion</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Discussion Topic"
              name="topic"
              value={newDiscussion.topic}
              onChange={handleInputChange}
              sx={{ mb: 3 }}
              placeholder="e.g., The Future of AI in Healthcare"
            />
            
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Participants</InputLabel>
              <Select
                multiple
                name="personas"
                value={newDiscussion.personas}
                onChange={handlePersonasChange}
                input={<OutlinedInput label="Participants" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((personaId) => (
                      <Chip 
                        key={personaId} 
                        label={personas[personaId]?.name || 'Unknown'} 
                        size="small" 
                      />
                    ))}
                  </Box>
                )}
              >
                {Object.entries(personas).map(([id, persona]) => (
                  <MenuItem key={id} value={id}>
                    {persona.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Format</InputLabel>
              <Select
                name="format"
                value={newDiscussion.format}
                onChange={handleSelectChange}
                label="Format"
              >
                <MenuItem value="conversation">Conversation</MenuItem>
                <MenuItem value="debate">Debate</MenuItem>
                <MenuItem value="interview">Interview</MenuItem>
                <MenuItem value="panel">Panel</MenuItem>
              </Select>
            </FormControl>
            
            <Box sx={{ mb: 3 }}>
              <Typography gutterBottom>Number of Rounds: {newDiscussion.num_rounds}</Typography>
              <Slider
                value={newDiscussion.num_rounds}
                onChange={handleRoundsChange}
                min={1}
                max={10}
                step={1}
                marks
                valueLabelDisplay="auto"
                sx={{
                  '& .MuiSlider-thumb': {
                    backgroundColor: solarizedDark.magenta,
                  },
                  '& .MuiSlider-track': {
                    backgroundColor: solarizedDark.magenta,
                  },
                }}
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCreateDialogClose}>Cancel</Button>
          <Button 
            onClick={handleCreateDiscussion} 
            variant="contained" 
            color="primary"
            disabled={creatingDiscussion}
          >
            {creatingDiscussion ? 'Creating...' : 'Create Discussion'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
      >
        <DialogTitle>Delete Discussion</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this discussion? This action cannot be undone.
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

export default DiscussionsPage; 