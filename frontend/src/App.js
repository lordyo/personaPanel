import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import './App.css';

// Import our pages
import EntityTypeList from './pages/EntityTypeList';
import EntityTypeCreate from './pages/EntityTypeCreate';
import EntityTypeDetail from './pages/EntityTypeDetail';
import EntityTypeEdit from './pages/EntityTypeEdit';
import TemplateDetail from './pages/TemplateDetail';
import EntityList from './pages/EntityList';
import SimulationCreate from './pages/SimulationCreate';
import SimulationList from './pages/SimulationList';
import SimulationDetail from './pages/SimulationDetail';

// Navigation Component with Tailwind
const Navigation = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  
  const navItems = [
    { name: 'Entity Types', path: '/entity-types' },
    { name: 'Entities', path: '/entities' },
    { name: 'Simulations', path: '/simulations' }
  ];
  
  const isActive = (path) => {
    return location.pathname.startsWith(path);
  };
  
  return (
    <header className="bg-gray-800 border-b border-gray-700">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-3">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-blue-300">
              PersonaPanel
            </Link>
          </div>
          
          {/* Mobile menu button */}
          <div className="md:hidden">
            <button 
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-gray-300 hover:text-white focus:outline-none"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
          
          {/* Desktop navigation */}
          <nav className="hidden md:flex space-x-6">
            {navItems.map((item) => (
              <Link
                key={item.name}
                to={item.path}
                className={`text-sm font-medium transition-colors duration-200 relative nav-link ${
                  isActive(item.path) 
                    ? 'text-blue-300 border-b-2 border-blue-400' 
                    : 'text-gray-300 hover:text-blue-300'
                }`}
              >
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>
      
      {/* Mobile menu */}
      <div className={`md:hidden ${mobileMenuOpen ? 'block' : 'hidden'}`}>
        <div className="px-2 pt-2 pb-3 space-y-1 bg-gray-800 border-t border-gray-700">
          {navItems.map((item) => (
            <Link
              key={item.name}
              to={item.path}
              className={`block px-3 py-2 rounded-md text-base font-medium ${
                isActive(item.path)
                  ? 'bg-gray-700 text-blue-300'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-blue-300'
              }`}
              onClick={() => setMobileMenuOpen(false)}
            >
              {item.name}
            </Link>
          ))}
        </div>
      </div>
    </header>
  );
};

// Home Page Component with Tailwind
const Home = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold text-blue-300 mb-4">
      Entity Simulation Framework
    </h1>
    <h2 className="text-xl text-gray-300 mb-8">
      Simulate interactions between diverse virtual entities.
    </h2>
    
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="border border-gray-700 rounded-lg bg-gray-800 overflow-hidden shadow-lg">
        <div className="p-5">
          <h3 className="text-xl font-semibold text-blue-300 mb-2">Entity Types</h3>
          <p className="text-gray-300 mb-4">
            Define and manage entity types with custom dimensions.
          </p>
          <Link 
            to="/entity-types" 
            className="inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Manage Entity Types
          </Link>
        </div>
      </div>
      
      <div className="border border-gray-700 rounded-lg bg-gray-800 overflow-hidden shadow-lg">
        <div className="p-5">
          <h3 className="text-xl font-semibold text-blue-300 mb-2">Entities</h3>
          <p className="text-gray-300 mb-4">
            Create and explore entities with rich dimensional characteristics.
          </p>
          <Link 
            to="/entities" 
            className="inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            View Entities
          </Link>
        </div>
      </div>
      
      <div className="border border-gray-700 rounded-lg bg-gray-800 overflow-hidden shadow-lg">
        <div className="p-5">
          <h3 className="text-xl font-semibold text-blue-300 mb-2">Simulations</h3>
          <p className="text-gray-300 mb-4">
            Run simulations to see how entities interact and evolve.
          </p>
          <Link 
            to="/simulations" 
            className="inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Explore Simulations
          </Link>
        </div>
      </div>
    </div>
  </div>
);

// Main App component with Tailwind
function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen bg-gray-900">
        <Navigation />
        <main className="flex-grow bg-gray-900">
          <Routes>
            <Route path="/" element={<Home />} />
            {/* Entity Type Management Routes */}
            <Route path="/entity-types" element={<EntityTypeList />} />
            <Route path="/entity-types/create" element={<EntityTypeCreate />} />
            <Route path="/entity-types/:id" element={<EntityTypeDetail />} />
            <Route path="/entity-types/:id/edit" element={<EntityTypeEdit />} />
            <Route path="/templates/:templateId" element={<TemplateDetail />} />
            {/* Entity Management Routes */}
            <Route path="/entities" element={<EntityList />} />
            {/* Simulation Routes */}
            <Route path="/simulations" element={<SimulationList />} />
            <Route path="/simulations/create" element={<SimulationCreate />} />
            <Route path="/simulations/:id" element={<SimulationDetail />} />
          </Routes>
        </main>
        <footer className="py-4 px-6 bg-gray-800 border-t border-gray-700 text-center text-gray-400">
          <p>&copy; {new Date().getFullYear()} Entity Simulation Framework</p>
        </footer>
      </div>
    </Router>
  );
}

export default App; 