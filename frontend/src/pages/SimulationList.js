import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { unifiedSimulationApi } from '../services/api';
import LoadingIndicator from '../components/LoadingIndicator';

/**
 * Page for viewing saved simulations
 */
const SimulationList = () => {
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteInProgress, setDeleteInProgress] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  // Pagination
  const [limit, setLimit] = useState(20);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    // Check for notification message from location state
    if (location.state?.message) {
      const timer = setTimeout(() => {
        navigate(location.pathname, { replace: true, state: {} });
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [location, navigate]);

  useEffect(() => {
    const fetchSimulations = async () => {
      try {
        setLoading(true);
        
        // Build query parameters
        const params = { limit, offset };
        
        const response = await unifiedSimulationApi.getAll(params);
        if (response && response.status === 'success') {
          setSimulations(response.data || []);
          // Check if there are more results
          setHasMore(response.data?.length === limit);
          setError(null);
        } else {
          console.error('Error fetching simulations:', response?.message || 'Unknown error');
          setError(response?.message || 'Failed to load simulations');
          setSimulations([]);
        }
        setLoading(false);
      } catch (err) {
        console.error("Error fetching simulations:", err);
        setError("Failed to load simulations. Please try again later.");
        setSimulations([]);
        setLoading(false);
      }
    };

    fetchSimulations();
  }, [limit, offset]);

  const handleViewSimulation = (id) => {
    navigate(`/simulations/${id}`);
  };
  
  const handleCreateSimulation = () => {
    navigate('/simulations/create');
  };
  
  const handleContinueSimulation = (simulation) => {
    navigate('/simulations/create', { 
      state: { 
        continuationData: {
          id: simulation.id,
          context: simulation.context,
          entity_ids: simulation.entity_ids,
          content: simulation.result || simulation.content,
          final_turn_number: simulation.final_turn_number || 0
        } 
      } 
    });
  };
  
  const handleDeleteSimulation = async (id) => {
    if (window.confirm('Are you sure you want to delete this simulation? This action cannot be undone.')) {
      try {
        setDeleteInProgress(true);
        const response = await unifiedSimulationApi.delete(id);
        
        if (response && response.status === 'success') {
          // Remove the deleted simulation from the list
          setSimulations(simulations.filter(sim => sim.id !== id));
          
          // Show success message
          navigate(location.pathname, { 
            replace: true, 
            state: { message: 'Simulation deleted successfully' } 
          });
        } else {
          console.error('Error deleting simulation:', response?.message || 'Unknown error');
          setError(response?.message || 'Failed to delete simulation');
        }
        setDeleteInProgress(false);
      } catch (err) {
        console.error("Error deleting simulation:", err);
        setError("Failed to delete simulation. Please try again later.");
        setDeleteInProgress(false);
      }
    }
  };
  
  const loadMore = () => {
    setOffset(prev => prev + limit);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    try {
      return new Date(dateString).toLocaleString();
    } catch (error) {
      console.error('Error formatting date:', error, 'Date string was:', dateString);
      return 'Invalid date format';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-blue-300">
          Simulations
        </h1>
        <button 
          className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
          onClick={handleCreateSimulation}
        >
          Create New Simulation
        </button>
      </div>
      
      {location.state?.message && (
        <div className="mb-6 p-4 bg-green-600 bg-opacity-10 border border-green-500 rounded-lg text-green-400">
          {location.state.message}
        </div>
      )}
      
      {error && (
        <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
          {error}
        </div>
      )}
      
      {loading ? (
        <div className="flex justify-center items-center py-8">
          <LoadingIndicator />
        </div>
      ) : simulations.length === 0 ? (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-blue-300 mb-2">
            No Simulations Found
          </h2>
          <p className="text-gray-300 mb-4">
            You haven't created any simulations yet. Create your first simulation to get started.
          </p>
          <button 
            className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
            onClick={handleCreateSimulation}
          >
            Create New Simulation
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {simulations.map((simulation) => (
              <div 
                key={simulation.id}
                className="border border-gray-700 rounded-lg overflow-hidden bg-gray-800 hover:bg-gray-750 transition-all duration-300 shadow-lg hover:shadow-xl flex flex-col h-full"
              >
                <div className="p-5 flex-grow">
                  <h3 className="text-xl font-semibold text-blue-300 mb-1 truncate">
                    {simulation.name || `Simulation ${simulation.id.slice(0, 8)}`}
                  </h3>
                  
                  <p className="text-gray-400 text-sm mb-3">
                    Created: {formatDate(simulation.created_at || simulation.timestamp)}
                  </p>
                  
                  <div className="flex mb-3 gap-2 flex-wrap">
                    <span className="bg-gray-700 text-gray-300 text-xs font-medium px-2.5 py-1 rounded-full">
                      {simulation.entity_ids?.length || 0} entities
                    </span>
                    
                    {simulation.final_turn_number && (
                      <span className="bg-gray-700 text-gray-300 text-xs font-medium px-2.5 py-1 rounded-full">
                        Turn {simulation.final_turn_number}
                      </span>
                    )}
                  </div>
                  
                  <p className="text-gray-300 mb-4 line-clamp-2 min-h-[3em]">
                    {simulation.context || "No context available"}
                  </p>
                </div>
                
                <div className="border-t border-gray-700 p-3 flex justify-between items-center">
                  <div className="flex gap-2">
                    <button 
                      className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
                      onClick={() => handleViewSimulation(simulation.id)}
                    >
                      View
                    </button>
                    
                    <button 
                      className="text-red-400 hover:text-red-300 font-medium transition-colors"
                      onClick={() => handleDeleteSimulation(simulation.id)}
                      disabled={deleteInProgress}
                    >
                      Delete
                    </button>
                  </div>
                  
                  <button 
                    className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-1 px-3 rounded-md text-sm transition-colors"
                    onClick={() => handleContinueSimulation(simulation)}
                  >
                    Continue
                  </button>
                </div>
              </div>
            ))}
          </div>
          
          {hasMore && (
            <div className="mt-8 text-center">
              <button 
                className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-2 px-4 rounded-md transition-colors"
                onClick={loadMore}
              >
                Load More
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default SimulationList; 