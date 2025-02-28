import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import solarizedDarkTheme from './theme/solarizedDarkTheme';
import Layout from './components/common/Layout';

// Import pages
import Dashboard from './pages/Dashboard';
import DimensionsPage from './pages/DimensionsPage';
import PersonasPage from './pages/PersonasPage';
import DiscussionsPage from './pages/DiscussionsPage';
import SettingsPage from './pages/SettingsPage';
import PersonaDetail from './pages/PersonaDetail';
import CreatePersonaPage from './pages/CreatePersonaPage';
import GeneratePersonasPage from './pages/GeneratePersonasPage';
import PersonaPreviewPage from './pages/PersonaPreviewPage';
import DiscussionDetail from './pages/DiscussionDetail';
import NotFound from './pages/NotFound';

function App() {
  return (
    <ThemeProvider theme={solarizedDarkTheme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dimensions" element={<DimensionsPage />} />
            <Route path="/personas" element={<PersonasPage />} />
            <Route path="/personas/new" element={<CreatePersonaPage />} />
            <Route path="/personas/generate" element={<GeneratePersonasPage />} />
            <Route path="/personas/preview/:id" element={<PersonaPreviewPage />} />
            <Route path="/personas/:id" element={<PersonaDetail />} />
            <Route path="/discussions" element={<DiscussionsPage />} />
            <Route path="/discussions/:id" element={<DiscussionDetail />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
