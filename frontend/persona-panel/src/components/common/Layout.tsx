import React, { useState } from 'react';
import { 
  Box, 
  AppBar, 
  Toolbar, 
  Typography, 
  Drawer, 
  List, 
  ListItemButton,
  ListItemIcon, 
  ListItemText, 
  IconButton,
  Container,
  useMediaQuery,
  useTheme,
  Divider
} from '@mui/material';
import { 
  Menu as MenuIcon, 
  Dashboard as DashboardIcon,
  Category as CategoryIcon,
  Person as PersonIcon,
  Forum as ForumIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { Link, useLocation } from 'react-router-dom';
import { solarizedDark } from '../../theme/solarizedDarkTheme';

const drawerWidth = 240;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Dimensions', icon: <CategoryIcon />, path: '/dimensions' },
    { text: 'Personas', icon: <PersonIcon />, path: '/personas' },
    { text: 'Discussions', icon: <ForumIcon />, path: '/discussions' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  const drawer = (
    <Box>
      <Box sx={{ 
        p: 2, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: solarizedDark.base02,
        color: solarizedDark.base2
      }}>
        <Typography variant="h6" component="div">
          Persona Panel
        </Typography>
      </Box>
      <Divider sx={{ backgroundColor: solarizedDark.base01 }} />
      <List>
        {menuItems.map((item) => {
          const isSelected = location.pathname === item.path;
          
          return (
            <ListItemButton
              key={item.text}
              component={Link}
              to={item.path}
              selected={isSelected}
              onClick={isMobile ? handleDrawerToggle : undefined}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: solarizedDark.base02,
                  '&:hover': {
                    backgroundColor: solarizedDark.base02,
                  },
                },
                '&:hover': {
                  backgroundColor: `${solarizedDark.base02}80`,
                },
              }}
            >
              <ListItemIcon sx={{ 
                color: isSelected ? solarizedDark.blue : solarizedDark.base0 
              }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text} 
                primaryTypographyProps={{
                  color: isSelected ? solarizedDark.base2 : solarizedDark.base1
                }}
              />
            </ListItemButton>
          );
        })}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar 
        position="fixed" 
        sx={{ 
          width: { md: `calc(100% - ${drawerWidth}px)` }, 
          ml: { md: `${drawerWidth}px` },
          boxShadow: 'none',
          borderBottom: `1px solid ${solarizedDark.base01}`
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ color: solarizedDark.base2 }}>
            {menuItems.find(item => item.path === location.pathname)?.text || 'Persona Panel'}
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              backgroundColor: solarizedDark.base03,
              color: solarizedDark.base1
            },
          }}
        >
          {drawer}
        </Drawer>
        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              backgroundColor: solarizedDark.base03,
              color: solarizedDark.base1,
              borderRight: `1px solid ${solarizedDark.base01}`
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{ 
          flexGrow: 1, 
          p: 3, 
          width: { md: `calc(100% - ${drawerWidth}px)` },
          backgroundColor: solarizedDark.base03,
          color: solarizedDark.base1,
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <Toolbar /> {/* This is for spacing below the AppBar */}
        <Container maxWidth="xl" sx={{ flexGrow: 1, py: 2 }}>
          {children}
        </Container>
      </Box>
    </Box>
  );
};

export default Layout; 