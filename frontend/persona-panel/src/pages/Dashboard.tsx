import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  Box, 
  Chip,
  CircularProgress,
  Button,
  Stack
} from '@mui/material';
import { 
  Person as PersonIcon, 
  Category as CategoryIcon, 
  Forum as ForumIcon,
  Add as AddIcon,
  AutoAwesome as GenerateIcon
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { personasApi, dimensionsApi, discussionsApi } from '../services/api';
import { solarizedDark } from '../theme/solarizedDarkTheme';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    personaCount: 0,
    dimensionCount: 0,
    discussionCount: 0
  });

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [personasResponse, dimensionsResponse, discussionsResponse] = await Promise.all([
          personasApi.getAll(),
          dimensionsApi.getAll(),
          discussionsApi.getAll()
        ]);

        if (personasResponse.success && dimensionsResponse.success && discussionsResponse.success) {
          setStats({
            personaCount: Object.keys(personasResponse.data || {}).length,
            dimensionCount: (dimensionsResponse.data || []).length,
            discussionCount: Object.keys(discussionsResponse.data || {}).length
          });
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const recentPersonas = Object.values(personasApi.getAll().then(res => res.data || {})).slice(0, 3);

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1" sx={{ color: solarizedDark.base2 }}>
          Dashboard
        </Typography>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <PersonIcon sx={{ mr: 1, color: solarizedDark.blue }} />
                    <Typography variant="h6" component="h2">
                      Personas
                    </Typography>
                  </Box>
                  <Typography variant="h3" component="p" sx={{ mb: 2, color: solarizedDark.base2 }}>
                    {stats.personaCount}
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    <Button 
                      component={Link} 
                      to="/personas/new" 
                      variant="outlined" 
                      color="primary" 
                      startIcon={<AddIcon />}
                      size="small"
                    >
                      Create New
                    </Button>
                    <Button 
                      component={Link} 
                      to="/personas/generate" 
                      variant="outlined" 
                      color="secondary" 
                      startIcon={<GenerateIcon />}
                      size="small"
                    >
                      Generate
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CategoryIcon sx={{ mr: 1, color: solarizedDark.cyan }} />
                    <Typography variant="h6" component="h2">
                      Dimensions
                    </Typography>
                  </Box>
                  <Typography variant="h3" component="p" sx={{ mb: 2, color: solarizedDark.base2 }}>
                    {stats.dimensionCount}
                  </Typography>
                  <Button 
                    component={Link} 
                    to="/dimensions" 
                    variant="outlined" 
                    color="info" 
                    startIcon={<AddIcon />}
                  >
                    Create New
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <ForumIcon sx={{ mr: 1, color: solarizedDark.magenta }} />
                    <Typography variant="h6" component="h2">
                      Discussions
                    </Typography>
                  </Box>
                  <Typography variant="h3" component="p" sx={{ mb: 2, color: solarizedDark.base2 }}>
                    {stats.discussionCount}
                  </Typography>
                  <Button 
                    component={Link} 
                    to="/discussions" 
                    variant="outlined" 
                    color="secondary" 
                    startIcon={<AddIcon />}
                  >
                    Create New
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Box sx={{ mb: 4 }}>
            <Typography variant="h5" component="h2" sx={{ mb: 2, color: solarizedDark.base2 }}>
              Recent Personas
            </Typography>
            <Grid container spacing={3}>
              {Object.values(personasApi.getAll().then(res => res.data || {})).slice(0, 3).map((persona: any) => (
                <Grid item xs={12} md={4} key={persona?.id || 'loading'}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" component="h3" sx={{ mb: 1 }}>
                        {persona?.name || 'Loading...'}
                      </Typography>
                      <Box sx={{ mb: 2 }}>
                        {persona?.traits?.slice(0, 3).map((trait: any) => (
                          <Chip 
                            key={trait.dimension} 
                            label={`${trait.dimension}: ${trait.value}`} 
                            size="small" 
                            sx={{ mr: 1, mb: 1 }}
                          />
                        ))}
                      </Box>
                      <Button 
                        component={Link} 
                        to={`/personas/${persona?.id}`} 
                        variant="text" 
                        color="primary"
                        size="small"
                      >
                        View Details
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        </>
      )}
    </Box>
  );
};

export default Dashboard; 