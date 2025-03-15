import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { unifiedSimulationApi, batchSimulationApi } from '../services/api';
import LoadingIndicator from '../components/LoadingIndicator';

/**
 * Page for viewing simulation details
 */
const SimulationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  // Get active tab from location state, default to individual
  const activeTab = location.state?.activeTab || 'individual';
  
  const [simulation, setSimulation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [batchData, setBatchData] = useState(null);
  
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
          console.log("Simulation data:", response.data);
          setSimulation(response.data);
          
          // If this simulation is part of a batch, fetch the batch details too
          if (response.data.metadata && response.data.metadata.batch_id) {
            try {
              const batchId = response.data.metadata.batch_id;
              const batchResponse = await batchSimulationApi.getById(batchId);
              if (batchResponse && batchResponse.status === 'success') {
                console.log("Batch data:", batchResponse.data);
                setBatchData(batchResponse.data);
                
                // Enhance simulation with batch data
                setSimulation(prevSim => {
                  // Create a new object that merges simulation data with relevant batch data
                  const enhancedSim = { ...prevSim };
                  
                  // If simulation has no context but batch does, use the batch context
                  if (!enhancedSim.context && batchResponse.data.context) {
                    enhancedSim.context = batchResponse.data.context;
                  }
                  
                  // Ensure metadata exists
                  if (!enhancedSim.metadata) {
                    enhancedSim.metadata = {};
                  }
                  
                  // Add batch context to metadata if not already there
                  if (!enhancedSim.metadata.batch_context && batchResponse.data.context) {
                    enhancedSim.metadata.batch_context = batchResponse.data.context;
                  }
                  
                  // Add batch name to metadata
                  if (!enhancedSim.metadata.batch_name && batchResponse.data.name) {
                    enhancedSim.metadata.batch_name = batchResponse.data.name;
                  }
                  
                  // Copy relevant fields from batch metadata to simulation metadata
                  if (batchResponse.data.metadata) {
                    // Fields that might be in batch metadata but not in simulation metadata
                    const relevantFields = [
                      'interaction_type', 'language', 'n_turns', 'simulation_rounds',
                      'interaction_size', 'num_simulations'
                    ];
                    
                    for (const field of relevantFields) {
                      if (batchResponse.data.metadata[field] && !enhancedSim.metadata[field]) {
                        enhancedSim.metadata[field] = batchResponse.data.metadata[field];
                      }
                    }
                  }
                  
                  return enhancedSim;
                });
              }
            } catch (batchErr) {
              console.error("Error fetching batch details:", batchErr);
              // This is non-critical, so we don't set an error state
            }
          }
          
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
    // Check if we navigated from a batch simulation page
    if (location.state?.fromBatch && location.state?.batchId) {
      // Navigate back to the batch simulation detail page
      navigate(`/batch-simulations/${location.state.batchId}`, {
        state: { 
          activeTab: 'batch'
        }
      });
    } else {
      // Navigate back to simulations list with active tab preserved
      navigate('/simulations', {
        state: { activeTab }
      });
    }
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
      <div className="container mx-auto px-4 py-8">
        <LoadingIndicator message="Loading simulation details..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-900 text-red-100 p-4 rounded-md mb-4">
          <h2 className="text-xl font-bold mb-2">Error</h2>
          <p>{error}</p>
        </div>
        <button 
          onClick={handleBack}
          className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md"
        >
          Go Back
        </button>
      </div>
    );
  }

  if (!simulation) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-900 text-yellow-100 p-4 rounded-md mb-4">
          <h2 className="text-xl font-bold mb-2">No Simulation Found</h2>
          <p>The requested simulation could not be found.</p>
        </div>
        <button 
          onClick={handleBack}
          className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md"
        >
          Go Back
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
          {/* Badge for batch simulation */}
          {simulation.metadata?.batch_id && (
            <div className="mt-2">
              <span className="bg-purple-900 text-purple-300 text-xs font-medium px-2.5 py-1 rounded-full">
                Part of batch: {simulation.metadata?.batch_name || simulation.metadata?.batch_id.substring(0, 8)}
              </span>
            </div>
          )}
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
      
      {/* Simulation Details */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-blue-300 mb-4">Simulation Details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-gray-400">Entity Count:</p>
            <p className="text-white">{simulation.entities?.length || simulation.entity_ids?.length || 0} entities</p>
          </div>
          
          {/* Show the new interaction_type from metadata (what kind of interaction happens between entities) */}
          {simulation.metadata?.interaction_type && (
            <div>
              <p className="text-gray-400">Interaction Type:</p>
              <p className="text-white">{simulation.metadata.interaction_type}</p>
            </div>
          )}
          
          {/* If there's no interaction_type in metadata, but the user is looking at an individual simulation with the old format */}
          {!simulation.metadata?.interaction_type && simulation.interaction_type && (
            <div>
              <p className="text-gray-400">Interaction Type:</p>
              <p className="text-white">discussion</p>
            </div>
          )}
          
          {simulation.metadata?.language && (
            <div>
              <p className="text-gray-400">Language:</p>
              <p className="text-white">{simulation.metadata.language}</p>
            </div>
          )}
          
          {(simulation.metadata?.n_turns || simulation.metadata?.num_turns) && (
            <div>
              <p className="text-gray-400">Number of Turns:</p>
              <p className="text-white">{simulation.metadata?.n_turns || simulation.metadata?.num_turns}</p>
            </div>
          )}
          
          {simulation.metadata?.simulation_rounds && (
            <div>
              <p className="text-gray-400">Simulation Rounds:</p>
              <p className="text-white">{simulation.metadata.simulation_rounds}</p>
            </div>
          )}
          
          <div>
            <p className="text-gray-400">Created:</p>
            <p className="text-white">{new Date(simulation.created_at).toLocaleString()}</p>
          </div>
          
          <div>
            <p className="text-gray-400">Simulation ID:</p>
            <p className="text-white font-mono text-sm">{simulation.id}</p>
          </div>
        </div>
      </div>
      
      {/* Context */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-blue-300 mb-4">Context</h2>
        <div className="whitespace-pre-wrap text-white bg-gray-700 p-4 rounded">
          {simulation.context || 
           (simulation.metadata && (
             simulation.metadata.context ||
             simulation.metadata.batch_context
           )) || 
           (batchData && batchData.context) ||
           "No context available"}
        </div>
      </div>
      
      {/* Entities */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-blue-300 mb-4">Entities</h2>
        <div className="flex flex-wrap gap-2 mt-1">
          {simulation.entities && simulation.entities.map((entity) => (
            <span 
              key={entity.id}
              className="bg-gray-700 text-white text-sm font-medium px-3 py-1.5 rounded-md"
            >
              {entity.name}
            </span>
          ))}
          
          {(!simulation.entities || simulation.entities.length === 0) && (
            <p className="text-gray-400 text-sm italic">No entity details available</p>
          )}
        </div>
      </div>
      
      {/* Simulation Content */}
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