import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';

// Import our new pages
import EntityTypeList from './pages/EntityTypeList';
import EntityTypeCreate from './pages/EntityTypeCreate';
import TemplateDetail from './pages/TemplateDetail';

// Placeholder components for the initial structure
const Home = () => (
  <div className="container">
    <h1>Entity Simulation Framework</h1>
    <p>Welcome to the Entity Simulation Framework, an LLM-powered system for simulating interactions between diverse virtual entities.</p>
    <div className="feature-grid">
      <div className="feature-card">
        <h3>Entity Types</h3>
        <p>Define and manage entity types with custom dimensions.</p>
        <Link to="/entity-types">Manage Entity Types</Link>
      </div>
      <div className="feature-card">
        <h3>Entities</h3>
        <p>Generate and customize entity instances.</p>
        <Link to="/entities">Manage Entities</Link>
      </div>
      <div className="feature-card">
        <h3>Simulations</h3>
        <p>Run simulations between entities in defined contexts.</p>
        <Link to="/simulations">Run Simulations</Link>
      </div>
    </div>
  </div>
);

// We're replacing the placeholder with our new implementation
// const EntityTypes = () => (
//   <div className="container">
//     <h1>Entity Types</h1>
//     <p>This page will allow you to create, view, and manage entity types.</p>
//     <p>Coming soon in a future sprint...</p>
//     <Link to="/">Back to Home</Link>
//   </div>
// );

const Entities = () => (
  <div className="container">
    <h1>Entities</h1>
    <p>This page will allow you to generate, view, and manage entities.</p>
    <p>Coming soon in a future sprint...</p>
    <Link to="/">Back to Home</Link>
  </div>
);

const Simulations = () => (
  <div className="container">
    <h1>Simulations</h1>
    <p>This page will allow you to run and view simulations between entities.</p>
    <p>Coming soon in a future sprint...</p>
    <Link to="/">Back to Home</Link>
  </div>
);

// Navigation component
const Navigation = () => (
  <nav className="navbar">
    <div className="navbar-brand">Entity Simulation</div>
    <ul className="navbar-nav">
      <li className="nav-item">
        <Link to="/" className="nav-link">Home</Link>
      </li>
      <li className="nav-item">
        <Link to="/entity-types" className="nav-link">Entity Types</Link>
      </li>
      <li className="nav-item">
        <Link to="/entities" className="nav-link">Entities</Link>
      </li>
      <li className="nav-item">
        <Link to="/simulations" className="nav-link">Simulations</Link>
      </li>
    </ul>
  </nav>
);

// Main App component
function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            {/* Entity Type Management Routes */}
            <Route path="/entity-types" element={<EntityTypeList />} />
            <Route path="/entity-types/create" element={<EntityTypeCreate />} />
            <Route path="/templates/:templateId" element={<TemplateDetail />} />
            {/* Placeholder routes */}
            <Route path="/entities" element={<Entities />} />
            <Route path="/simulations" element={<Simulations />} />
          </Routes>
        </main>
        <footer className="footer">
          <p>Entity Simulation Framework &copy; 2023</p>
        </footer>
      </div>
    </Router>
  );
}

export default App; 