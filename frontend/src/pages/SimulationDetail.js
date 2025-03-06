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

  const handleDeleteSimulation = async () => {
    try {
      setLoading(true);
      const response = await simulationApi.delete(id);
      if (response && response.status === 'success') {
        navigate('/simulations', { state: { message: 'Simulation deleted successfully' } });
      } else {
        console.error('Error deleting simulation:', response?.message || 'Unknown error');
        setError(response?.message || 'Failed to delete simulation');
        setLoading(false);
      }
    } catch (err) {
      console.error("Error deleting simulation:", err);
      setError("Failed to delete simulation. Please try again later.");
      setLoading(false);
    }
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
          <h1 className="text-2xl font-bold text-blue-300 mb-2">{simulation?.name || 'Unnamed Simulation'}</h1>
          
          <div className="flex flex-wrap gap-6 mb-4 text-gray-400">
            <div className="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
              <span>{formatDate(simulation?.created_at)}</span>
            </div>
            
            <div className="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
              </svg>
              <span>{simulation?.entities?.length || 0} Entities</span>
            </div>
          </div>
          
          <div className="mb-6">
            <h2 className="text-lg font-medium text-blue-300 mb-2">Context</h2>
            <p className="text-gray-300 bg-gray-750 p-4 rounded-lg">
              {typeof simulation?.context === 'string' 
                ? simulation.context 
                : (simulation?.context?.description 
                  ? simulation.context.description 
                  : JSON.stringify(simulation?.context) || 'No context available')}
            </p>
          </div>

          {simulation?.content && (
            <div className="mt-8">
              <h2 className="text-lg font-medium text-blue-300 mb-2">Simulation Content</h2>
              <div className="bg-gray-750 p-4 rounded-lg text-gray-300 whitespace-pre-wrap">
                {(() => {
                  try {
                    const content = simulation.content;
                    
                    // Try to parse as JSON if it looks like JSON
                    if (typeof content === 'string' && 
                        (content.trim().startsWith('{') || content.trim().startsWith('['))) {
                      try {
                        const parsed = JSON.parse(content);
                        // If it's a dialogue array, format it nicely
                        if (Array.isArray(parsed)) {
                          return (
                            <div className="space-y-4">
                              {parsed.map((item, idx) => (
                                <div key={idx} className="border-b border-gray-700 pb-3 mb-3 last:border-0">
                                  <div className="flex justify-between mb-2">
                                    <span className="font-bold text-blue-400">{item.speaker || 'Unknown'}</span>
                                    <span className="text-gray-400 text-sm">{idx + 1}/{parsed.length}</span>
                                  </div>
                                  <div className="pl-4 border-l-2 border-gray-700">{item.text || item.content || item.message || JSON.stringify(item)}</div>
                                </div>
                              ))}
                            </div>
                          );
                        } else {
                          // Otherwise just stringify it with formatting
                          return <pre className="font-mono text-sm overflow-x-auto">{JSON.stringify(parsed, null, 2)}</pre>;
                        }
                      } catch (error) {
                        // Not valid JSON, continue to other formats
                        console.log('Not valid JSON, trying other formats');
                      }
                    }
                    
                    // Check for multi-round dialogue format with ROUND markers
                    if (content && content.includes('ROUND ')) {
                      // Split the content by ROUND markers
                      const roundMarkers = content.match(/ROUND \d+/g) || [];
                      let rounds = [];
                      
                      if (roundMarkers.length > 0) {
                        // First get all the round numbers
                        const roundNumbers = roundMarkers.map(marker => marker.replace('ROUND ', '').trim());
                        
                        // Split the content into rounds
                        let remainingContent = content;
                        roundMarkers.forEach((marker, index) => {
                          const markerPosition = remainingContent.indexOf(marker);
                          
                          if (markerPosition >= 0) {
                            // If not the first round, save the previous round content
                            if (index > 0) {
                              const roundContent = remainingContent.substring(0, markerPosition).trim();
                              rounds.push({ number: roundNumbers[index-1], content: roundContent });
                            }
                            
                            // Remove the processed part for the next iteration
                            remainingContent = remainingContent.substring(markerPosition + marker.length);
                          }
                        });
                        
                        // Add the last round
                        if (remainingContent.trim()) {
                          rounds.push({ number: roundNumbers[roundNumbers.length-1], content: remainingContent.trim() });
                        }
                        
                        // If we have rounds, render them
                        if (rounds.length > 0) {
                          return (
                            <div className="space-y-6">
                              {rounds.map((round, idx) => {
                                // Process speakers in this round
                                const speakers = round.content.split(/\n(?=[A-Za-z].*?:)/).filter(line => line.trim());
                                
                                return (
                                  <div key={idx} className="border border-gray-700 rounded-lg overflow-hidden mb-4">
                                    <div className="bg-gray-700 px-4 py-2 text-blue-300 font-medium">
                                      Round {round.number}
                                    </div>
                                    <div className="p-3 space-y-4">
                                      {speakers.map((speaker, speakerIdx) => {
                                        // Try to extract name and content
                                        const match = speaker.match(/^([^:]+):(.*)/s);
                                        if (match) {
                                          const [_, name, text] = match;
                                          // Extract thoughts (inside parentheses with asterisks)
                                          const thoughtsMatch = text.match(/\(thinks\)\s*\*(.*?)\*/s);
                                          const thoughts = thoughtsMatch ? thoughtsMatch[1].trim() : null;
                                          
                                          // Extract spoken dialogue (inside single quotes)
                                          // Use a more robust regex that matches the last occurrence of quoted text
                                          // This fixes issues with the dialogue extraction for the first speaker
                                          let dialogue = text.trim();
                                          
                                          // First remove the thoughts part if it exists
                                          if (thoughts) {
                                            dialogue = dialogue.replace(/\(thinks\)\s*\*(.*?)\*/s, '').trim();
                                          }
                                          
                                          // Then look for text in quotes
                                          const dialogueMatch = dialogue.match(/'([^']*)'(?!.*')/s) || dialogue.match(/'(.*?)'$/s);
                                          
                                          if (dialogueMatch) {
                                            dialogue = dialogueMatch[1].trim();
                                          } else if (thoughts) {
                                            // If no quoted text found but we have thoughts, assume the rest is dialogue
                                            // but check for additional markers that might indicate dialogue
                                            const postThoughtsText = text.split(/\(thinks\)\s*\*(.*?)\*/s).pop().trim();
                                            if (postThoughtsText) {
                                              dialogue = postThoughtsText;
                                            }
                                          }
                                          
                                          return (
                                            <div key={speakerIdx} className="border-l-2 border-gray-600 pl-3 pb-2">
                                              <div className="font-bold text-blue-400 mb-1">{name.trim()}</div>
                                              {thoughts && (
                                                <div className="italic text-gray-400 mb-2">
                                                  <span className="font-normal text-xs mr-1">thinks:</span>
                                                  {thoughts}
                                                </div>
                                              )}
                                              <div className="text-gray-300">{dialogue}</div>
                                            </div>
                                          );
                                        }
                                        return <div key={speakerIdx}>{speaker}</div>;
                                      })}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          );
                        }
                      }
                    }
                    
                    // If we reach here, just display the content as plain text
                    return content;
                    
                  } catch (error) {
                    console.error('Error rendering content:', error);
                    return <span className="text-red-400">Error displaying content: {error.message}</span>;
                  }
                })()}
              </div>
            </div>
          )}
          
          <div className="mt-8 flex justify-end">
            <button
              onClick={() => {
                if (window.confirm('Are you sure you want to delete this simulation?')) {
                  handleDeleteSimulation();
                }
              }}
              className="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-md transition-colors"
            >
              Delete Simulation
            </button>
          </div>
        </div>
      </div>

      {simulation?.entities && simulation?.entities.length > 0 && (
        <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 overflow-hidden">
          <div className="p-4 bg-gray-750 border-b border-gray-700">
            <h2 className="text-lg font-medium text-blue-300">Entity Details</h2>
          </div>
          
          <div className="divide-y divide-gray-700">
            {simulation?.entities.map((entity, index) => (
              <div key={index} className="p-4">
                <h3 className="text-md font-medium text-blue-300 mb-2">{entity?.name || 'Unnamed Entity'}</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-1">Type</h4>
                    <p className="text-gray-300">{entity?.entity_type_name || 'Unknown Type'}</p>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-1">ID</h4>
                    <p className="text-gray-300 font-mono text-sm">{entity?.id || 'No ID'}</p>
                  </div>
                </div>
                
                <div className="mt-3">
                  <h4 className="text-sm font-medium text-gray-400 mb-1">Description</h4>
                  <p className="text-gray-300 bg-gray-750 p-2 rounded">{entity?.description || 'No description available'}</p>
                </div>
                
                {entity?.attributes && Object.keys(entity?.attributes).length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-400 mb-2">Attributes</h4>
                    <div className="bg-gray-750 rounded-lg p-3">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2">
                        {Object.entries(entity.attributes).map(([key, value]) => (
                          <div key={key} className="flex justify-between py-1 border-b border-gray-700 last:border-0">
                            <span className="text-gray-400">{key}:</span>
                            <span className="text-gray-300 font-medium">
                              {value === null ? 'null' :
                               typeof value === 'object' ? JSON.stringify(value) : 
                               String(value)}
                            </span>
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