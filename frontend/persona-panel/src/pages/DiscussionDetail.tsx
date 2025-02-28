import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Card, 
  CardContent, 
  Chip,
  CircularProgress,
  Button,
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Alert,
  Paper
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { discussionsApi, personasApi } from '../services/api';
import { Discussion, Persona } from '../types';
import { solarizedDark } from '../theme/solarizedDarkTheme';
import ReactMarkdown from 'react-markdown';

// Note: You may need to install react-markdown with: npm install react-markdown
// If you don't have it installed, you can replace the ReactMarkdown component with
// a simple pre-formatted text display

const DiscussionDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [discussion, setDiscussion] = useState<Discussion | null>(null);
  const [personas, setPersonas] = useState<Record<string, Persona>>({});
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });

  useEffect(() => {
    if (id) {
      fetchData(id);
    }
  }, [id]);

  const fetchData = async (discussionId: string) => {
    setLoading(true);
    try {
      const [discussionResponse, personasResponse] = await Promise.all([
        discussionsApi.getById(discussionId),
        personasApi.getAll()
      ]);
      
      if (discussionResponse.success && discussionResponse.data) {
        setDiscussion(discussionResponse.data);
      } else {
        setSnackbar({
          open: true,
          message: discussionResponse.error || 'Failed to load discussion',
          severity: 'error',
        });
      }
      
      if (personasResponse.success && personasResponse.data) {
        setPersonas(personasResponse.data);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setSnackbar({
        open: true,
        message: 'An error occurred while loading the discussion',
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
        const response = await discussionsApi.delete(id);
        if (response.success) {
          setSnackbar({
            open: true,
            message: 'Discussion deleted successfully',
            severity: 'success',
          });
          
          // Navigate back to discussions list after a short delay
          setTimeout(() => {
            navigate('/discussions');
          }, 1500);
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
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleDownload = () => {
    if (!discussion) return;
    
    const filename = `${discussion.settings.topic.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.md`;
    const content = discussion.content;
    
    const element = document.createElement('a');
    const file = new Blob([content], {type: 'text/markdown'});
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton 
            onClick={() => navigate('/discussions')} 
            sx={{ mr: 2 }}
            aria-label="Back to discussions"
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" component="h1" sx={{ color: solarizedDark.base2 }}>
            {loading ? 'Loading Discussion...' : discussion?.settings.topic || 'Discussion Not Found'}
          </Typography>
        </Box>
        
        {!loading && discussion && (
          <Box>
            <Button 
              variant="outlined" 
              color="primary" 
              startIcon={<DownloadIcon />}
              onClick={handleDownload}
              sx={{ mr: 2 }}
            >
              Download
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
      ) : !discussion ? (
        <Box sx={{ textAlign: 'center', my: 4 }}>
          <Typography variant="h6">
            Discussion Not Found
          </Typography>
          <Typography variant="body1" sx={{ mt: 1 }}>
            The requested discussion could not be found.
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            component={Link}
            to="/discussions"
            sx={{ mt: 3 }}
          >
            Back to Discussions
          </Button>
        </Box>
      ) : (
        <>
          {/* Discussion Info */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" sx={{ color: solarizedDark.base01 }}>
                  Format
                </Typography>
                <Typography variant="body1" sx={{ mb: 1 }}>
                  {discussion.settings.format.charAt(0).toUpperCase() + discussion.settings.format.slice(1)}
                </Typography>
                
                <Typography variant="subtitle2" sx={{ color: solarizedDark.base01, mt: 2 }}>
                  Created
                </Typography>
                <Typography variant="body1" sx={{ mb: 1 }}>
                  {formatDate(discussion.created_at)}
                </Typography>
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle2" sx={{ color: solarizedDark.base01 }}>
                Participants
              </Typography>
              <Box sx={{ mt: 1 }}>
                {discussion.settings.personas.map(personaId => (
                  <Chip 
                    key={personaId}
                    label={personas[personaId]?.name || 'Unknown'}
                    component={Link}
                    to={`/personas/${personaId}`}
                    clickable
                    sx={{ mr: 1, mb: 1 }}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>

          {/* Discussion Content */}
          <Paper 
            elevation={1} 
            sx={{ 
              p: 3, 
              backgroundColor: solarizedDark.base02,
              color: solarizedDark.base1,
              borderRadius: 2
            }}
          >
            {/* If react-markdown is installed, use this: */}
            <ReactMarkdown>
              {discussion.content}
            </ReactMarkdown>
            
            {/* If react-markdown is not installed, use this instead:
            <Box component="pre" sx={{ 
              whiteSpace: 'pre-wrap',
              fontFamily: '"Roboto Mono", monospace',
              fontSize: '0.9rem',
              overflowX: 'auto'
            }}>
              {discussion.content}
            </Box>
            */}
          </Paper>
        </>
      )}

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

export default DiscussionDetail; 