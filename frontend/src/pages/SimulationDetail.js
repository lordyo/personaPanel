import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { unifiedSimulationApi } from '../services/api';
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
  
  // Continue simulation dialog
  const [continueDialogOpen, setContinueDialogOpen] = useState(false);
  const [nTurns, setNTurns] = useState(1);
  const [simulationRounds, setSimulationRounds] = useState(1);
  const [continuing, setContinuing] = useState(false);
  const [continueError, setContinueError] = useState(null);

  useEffect(() => {
    const fetchSimulation = async () => {
      try {
        const response = await unifiedSimulationApi.getById(id);
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
  
  const handleOpenContinueDialog = () => {
    setContinueDialogOpen(true);
  };
  
  const handleCloseContinueDialog = () => {
    setContinueDialogOpen(false);
    setContinueError(null);
  };
  
  const handleContinueSimulation = async () => {
    if (nTurns < 1 || simulationRounds < 1) {
      setContinueError("Number of turns and rounds must be at least 1");
      return;
    }
    
    setContinuing(true);
    setContinueError(null);
    
    try {
      const continuationOptions = {
        n_turns: nTurns,
        simulation_rounds: simulationRounds
      };
      
      const response = await unifiedSimulationApi.continue(id, continuationOptions);
      
      if (response && response.status === 'success') {
        // Reload the simulation to get the updated content
        const updatedSimulation = await unifiedSimulationApi.getById(id);
        if (updatedSimulation && updatedSimulation.status === 'success') {
          setSimulation(updatedSimulation.data);
        }
        handleCloseContinueDialog();
      } else {
        setContinueError(response?.message || 'Failed to continue simulation');
      }
    } catch (err) {
      console.error('Error continuing simulation:', err);
      setContinueError(`Error: ${err.message || 'Failed to continue simulation'}`);
    } finally {
      setContinuing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingIndicator />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
          {error}
        </div>
        <button 
          onClick={handleBack}
          className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-2 px-4 rounded-md transition-colors"
        >
          Back to Simulations
        </button>
      </div>
    );
  }

  if (!simulation) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6 p-4 bg-orange-400 bg-opacity-10 border border-orange-400 rounded-lg text-orange-300">
          Simulation not found
        </div>
        <button 
          onClick={handleBack}
          className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-2 px-4 rounded-md transition-colors"
        >
          Back to Simulations
        </button>
      </div>
    );
  }

  // Format the simulation content for display
  const formatContent = (content) => {
    if (!content) return <p className="text-gray-400 italic">No content available</p>;
    
    // Process the content based on the structure (assuming it's plain text with TURN markers)
    return (
      <div className="whitespace-pre-wrap text-gray-300">
        {content.split(/\n\n(?=(?:TURN|Turn) \d+:)/).map((turnContent, index) => {
          // Extract turn number from the heading
          const turnMatch = turnContent.match(/^(?:TURN|Turn) (\d+):/i);
          const turnNumber = turnMatch ? turnMatch[1] : index + 1;
          
          return (
            <div 
              key={index} 
              className="mb-6 p-4 bg-gray-700 border border-gray-600 rounded-lg"
            >
              <div className="font-semibold text-blue-300 mb-2 pb-2 border-b border-gray-600">
                {turnMatch ? turnContent.split('\n')[0] : `Turn ${turnNumber}`}
              </div>
              <div className="whitespace-pre-wrap text-gray-300">
                {turnMatch ? 
                  turnContent.split('\n').slice(1).join('\n') : 
                  turnContent
                }
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-bold text-blue-300">
            {simulation.name || `Simulation ${simulation.id.slice(0, 8)}`}
          </h1>
          <p className="text-gray-400">
            Created: {new Date(simulation.created_at).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={handleBack}
            className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-2 px-4 rounded-md transition-colors"
          >
            Back
          </button>
          <button 
            onClick={handleOpenContinueDialog}
            className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
          >
            Continue Simulation
          </button>
        </div>
      </div>
      
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <h2 className="text-xl font-semibold text-blue-300 mb-3">
              Context
            </h2>
            <div className="bg-gray-700 border border-gray-600 rounded-lg p-4 text-gray-300">
              {simulation.context || "No context available"}
            </div>
          </div>
          
          <div>
            <h2 className="text-xl font-semibold text-blue-300 mb-3">
              Details
            </h2>
            <div className="bg-gray-700 border border-gray-600 rounded-lg p-4">
              <div className="mb-4">
                <h3 className="text-gray-300 font-medium mb-1">Entity Count</h3>
                <p className="text-blue-300">{simulation.entity_ids?.length || 0} entities</p>
              </div>
              
              <div className="mb-4">
                <h3 className="text-gray-300 font-medium mb-1">Simulation ID</h3>
                <p className="text-blue-300 text-sm font-mono">{simulation.id}</p>
              </div>
              
              <div>
                <h3 className="text-gray-300 font-medium mb-1">Entities</h3>
                <div className="flex flex-wrap gap-2 mt-1">
                  {simulation.entities && simulation.entities.map((entity) => (
                    <span 
                      key={entity.id}
                      className="bg-gray-600 text-gray-300 text-xs font-medium px-2.5 py-1 rounded-full"
                    >
                      {entity.name}
                    </span>
                  ))}
                  
                  {(!simulation.entities || simulation.entities.length === 0) && (
                    <p className="text-gray-400 text-sm italic">No entity details available</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-blue-300 mb-4">
          Simulation Content
        </h2>
        {formatContent(simulation.result || simulation.content)}
      </div>
      
      {/* Continue Simulation Dialog */}
      {continueDialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 border border-gray-700 rounded-lg w-full max-w-md p-6">
            <h3 className="text-xl font-semibold text-blue-300 mb-4">
              Continue Simulation
            </h3>
            
            {continueError && (
              <div className="mb-4 p-3 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400 text-sm">
                {continueError}
              </div>
            )}
            
            <div className="mb-4">
              <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="nTurns">
                Number of Turns
              </label>
              <input
                id="nTurns"
                type="number"
                value={nTurns}
                onChange={(e) => setNTurns(parseInt(e.target.value, 10))}
                min={1}
                max={10}
                className="bg-gray-700 text-white border border-gray-600 rounded-md p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="mt-1 text-gray-400 text-sm">Number of dialogue turns (1-10)</p>
            </div>
            
            <div className="mb-6">
              <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="simulationRounds">
                Simulation Rounds
              </label>
              <input
                id="simulationRounds"
                type="number"
                value={simulationRounds}
                onChange={(e) => setSimulationRounds(parseInt(e.target.value, 10))}
                min={1}
                max={5}
                className="bg-gray-700 text-white border border-gray-600 rounded-md p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="mt-1 text-gray-400 text-sm">Number of sequential LLM calls (1-5)</p>
            </div>
            
            <div className="flex justify-end gap-3">
              <button 
                onClick={handleCloseContinueDialog}
                className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-2 px-4 rounded-md transition-colors"
                disabled={continuing}
              >
                Cancel
              </button>
              <button 
                onClick={handleContinueSimulation}
                className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors flex items-center"
                disabled={continuing}
              >
                {continuing ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                  </>
                ) : (
                  'Continue'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimulationDetail; 