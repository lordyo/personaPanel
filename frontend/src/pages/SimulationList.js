import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { simulationApi } from '../services/api';
import LoadingIndicator from '../components/LoadingIndicator';

/**
 * Page for viewing saved simulations
 */
const SimulationList = () => {
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSimulations = async () => {
      try {
        const response = await simulationApi.getAll();
        if (response && response.status === 'success') {
          setSimulations(response.data || []);
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
  }, []);

  const handleViewSimulation = (id) => {
    navigate(`/simulations/${id}`);
  };

  const handleCreateSimulation = () => {
    navigate('/simulations/create');
  };

  // Format date to a more readable format
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    try {
      // Some systems return ISO timestamps without the 'T' separator
      const normalizedDate = dateString.includes('T') ? 
        dateString : 
        dateString.replace(/(\d{4}-\d{2}-\d{2})[ ]?(\d{2}:\d{2}:\d{2})/, '$1T$2');
      
      const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      };
      return new Date(normalizedDate).toLocaleDateString(undefined, options);
    } catch (error) {
      console.error('Error formatting date:', error, 'Date string was:', dateString);
      return 'Invalid date format';
    }
  };

  if (loading) {
    return <LoadingIndicator message="Loading simulations..." fullPage />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-blue-300">Simulations</h1>
        <button
          onClick={handleCreateSimulation}
          className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
          Create Simulation
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
          {error}
        </div>
      )}

      {simulations.length === 0 ? (
        <div className="bg-gray-800 p-8 text-center rounded-lg border border-gray-700 shadow-lg">
          <h2 className="text-xl font-semibold text-blue-300 mb-2">No simulations found</h2>
          <p className="text-gray-400 mb-6">Create your first simulation to get started</p>
          <button
            onClick={handleCreateSimulation}
            className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors mx-auto"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
            </svg>
            Create Simulation
          </button>
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg border border-gray-700 shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="bg-gray-750">
                  <th className="py-3 px-4 text-left text-sm font-medium text-gray-300">Name</th>
                  <th className="py-3 px-4 text-left text-sm font-medium text-gray-300">Created</th>
                  <th className="py-3 px-4 text-left text-sm font-medium text-gray-300">Context</th>
                  <th className="py-3 px-4 text-left text-sm font-medium text-gray-300">Entities</th>
                  <th className="py-3 px-4 text-left text-sm font-medium text-gray-300">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {simulations.map((simulation) => (
                  <tr 
                    key={simulation?.id || `sim-${Math.random()}`}
                    className="hover:bg-gray-750 transition-colors"
                  >
                    <td className="py-3 px-4 text-gray-300">{simulation?.name || 'Unnamed Simulation'}</td>
                    <td className="py-3 px-4 text-gray-300">{formatDate(simulation?.created_at)}</td>
                    <td className="py-3 px-4 text-gray-300">
                      {simulation?.context ? (
                        simulation?.context.length > 70 
                          ? `${simulation?.context.substring(0, 70)}...` 
                          : simulation?.context
                      ) : (
                        <span className="text-gray-500 italic">No context available</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {simulation?.entities && simulation?.entities.length > 0 ? (
                        <div className="flex flex-wrap gap-1">
                          {simulation?.entities.slice(0, 3).map((entity, index) => (
                            <span 
                              key={index} 
                              className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded-full"
                            >
                              {entity?.name || 'Unnamed Entity'}
                            </span>
                          ))}
                          {simulation?.entities.length > 3 && (
                            <span className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded-full">
                              +{simulation?.entities.length - 3} more
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-gray-500 italic">No entities</span>
                      )}
                    </td>
                    <td className="py-3 px-4 flex justify-end space-x-2">
                      <button
                        className="p-2 rounded bg-blue-700 text-white hover:bg-blue-600 transition-colors"
                        onClick={() => handleViewSimulation(simulation?.id)}
                        title="View Details"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                          <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimulationList; 