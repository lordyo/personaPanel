import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { simulationApi } from '../services/api';
import LoadingIndicator from '../components/LoadingIndicator';

/**
 * Page for viewing simulation details
 */
const SimulationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [simulation, setSimulation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSimulation = async () => {
      try {
        const response = await simulationApi.getById(id);
        if (response && response.status === 'success') {
          setSimulation(response.data);
          setError(null);
        } else {
          console.error('Error fetching simulation:', response?.message || 'Unknown error');
          setError(response?.message || 'Failed to load simulation');
          setSimulation(null);
        }
        setLoading(false);
      } catch (err) {
        console.error("Error fetching simulation:", err);
        setError("Failed to load simulation. Please try again later.");
        setSimulation(null);
        setLoading(false);
      }
    };

    fetchSimulation();
  }, [id]);

  const handleBack = () => {
    navigate('/simulations');
  };

  // Format date to a more readable format
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  if (loading) {
    return <LoadingIndicator message="Loading simulation details..." fullPage />;
  }

  if (!simulation) {
    return (
      <div className="container mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
            {error}
          </div>
        )}
        <div className="flex items-center mb-6">
          <button 
            onClick={handleBack}
            className="flex items-center text-blue-400 hover:text-blue-300"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            Back to Simulations
          </button>
        </div>
        <div className="bg-gray-800 p-8 text-center rounded-lg border border-gray-700">
          <h2 className="text-xl font-semibold text-blue-300 mb-2">Simulation not found</h2>
          <p className="text-gray-400">The requested simulation could not be loaded.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {error && (
        <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
          {error}
        </div>
      )}

      <div className="flex items-center mb-6">
        <button 
          onClick={handleBack}
          className="flex items-center text-blue-400 hover:text-blue-300"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
          </svg>
          Back to Simulations
        </button>
      </div>

      <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 overflow-hidden mb-8">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-blue-300 mb-2">{simulation.name}</h1>
          
          <div className="flex flex-wrap gap-6 mb-4 text-gray-400">
            <div className="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
              <span>{formatDate(simulation.created_at)}</span>
            </div>
            
            <div className="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
              </svg>
              <span>{simulation.entities.length} Entities</span>
            </div>
          </div>
          
          <div className="mb-6">
            <h2 className="text-lg font-medium text-blue-300 mb-2">Context</h2>
            <p className="text-gray-300 bg-gray-750 p-4 rounded-lg">{simulation.context}</p>
          </div>
        </div>
      </div>

      {simulation.entities && simulation.entities.length > 0 && (
        <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 overflow-hidden">
          <div className="p-4 bg-gray-750 border-b border-gray-700">
            <h2 className="text-lg font-medium text-blue-300">Entity Details</h2>
          </div>
          
          <div className="divide-y divide-gray-700">
            {simulation.entities.map((entity, index) => (
              <div key={index} className="p-4">
                <h3 className="text-md font-medium text-blue-300 mb-2">{entity.name}</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-1">Type</h4>
                    <p className="text-gray-300">{entity.entity_type_name}</p>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-1">ID</h4>
                    <p className="text-gray-300 font-mono text-sm">{entity.id}</p>
                  </div>
                </div>
                
                {entity.properties && Object.keys(entity.properties).length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-400 mb-2">Properties</h4>
                    <div className="bg-gray-750 rounded-lg p-3">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2">
                        {Object.entries(entity.properties).map(([key, value]) => (
                          <div key={key} className="flex justify-between py-1 border-b border-gray-700 last:border-0">
                            <span className="text-gray-400">{key}:</span>
                            <span className="text-gray-300 font-medium">{typeof value === 'object' ? JSON.stringify(value) : value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SimulationDetail; 