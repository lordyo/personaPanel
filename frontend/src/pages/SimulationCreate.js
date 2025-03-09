import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { entityTypeApi, entityApi, unifiedSimulationApi } from '../services/api';
import LoadingIndicator from '../components/LoadingIndicator';

/**
 * Page for creating and running simulations
 */
const SimulationCreate = () => {
  const location = useLocation();
  const continuationData = location.state?.continuationData;

  // States for form data and UI control
  const [entityTypes, setEntityTypes] = useState([]);
  const [entities, setEntities] = useState({});  // Map of entity type ID to entities array
  const [loading, setLoading] = useState(true);
  const [loadingEntities, setLoadingEntities] = useState(false);
  const [error, setError] = useState(null);
  
  // Form state
  const [simulationName, setSimulationName] = useState('');
  const [simulationContext, setSimulationContext] = useState('');
  const [selectedEntityTypeId, setSelectedEntityTypeId] = useState('');
  const [selectedEntityIds, setSelectedEntityIds] = useState([]);
  const [nTurns, setNTurns] = useState(3);
  const [simulationRounds, setSimulationRounds] = useState(1);
  const [isContinuation, setIsContinuation] = useState(false);
  const [lastTurnNumber, setLastTurnNumber] = useState(0);
  const [previousInteraction, setPreviousInteraction] = useState('');
  const [interactionType, setInteractionType] = useState('discussion');
  const [language, setLanguage] = useState('English');
  
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  // Set form values from continuation data if available
  useEffect(() => {
    if (continuationData) {
      setSimulationContext(continuationData.context || '');
      setNTurns(continuationData.n_turns || 3);
      setSimulationRounds(continuationData.simulation_rounds || 1);
      setLastTurnNumber(continuationData.final_turn_number || 0);
      setPreviousInteraction(continuationData.content || '');
      setIsContinuation(true);
      setSimulationName(`Continuation ${new Date().toLocaleString()}`);
      
      // Try to get interaction_type and language from continuationData or its metadata
      // First check if they exist at the top level
      if (continuationData.interaction_type) {
        setInteractionType(continuationData.interaction_type);
      }
      
      if (continuationData.language) {
        setLanguage(continuationData.language);
      }
      
      // Then check if they're in metadata as a fallback
      else if (continuationData.metadata) {
        setInteractionType(continuationData.metadata.interaction_type || interactionType);
        setLanguage(continuationData.metadata.language || language);
      }
      
      if (continuationData.entity_ids && continuationData.entity_ids.length > 0) {
        setSelectedEntityIds(continuationData.entity_ids);
      }
    }
  }, [continuationData]);

  // Fetch entity types on component mount
  useEffect(() => {
    const fetchEntityTypes = async () => {
      try {
        console.log("Fetching entity types...");
        const response = await entityTypeApi.getAll();
        console.log("Entity types response:", response);
        
        if (response && response.status === 'success') {
          setEntityTypes(response.data || []);
          
          // If there's at least one entity type, select it by default
          if (response.data && response.data.length > 0) {
            setSelectedEntityTypeId(response.data[0].id);
          }
          
          setError(null);
        } else {
          console.error('Error fetching entity types:', response?.message || 'Unknown error');
          setError(`Failed to load entity types: ${response?.message || 'Unknown error'}`);
          setEntityTypes([]);
        }
        setLoading(false);
      } catch (err) {
        console.error("Error fetching entity types:", err);
        setError(`Failed to load entity types: ${err.message || 'Please try again later.'}`);
        setEntityTypes([]);
        setLoading(false);
      }
    };

    fetchEntityTypes();
  }, []);

  // Fetch entities when entity type is selected
  useEffect(() => {
    const fetchEntitiesForType = async (entityTypeId) => {
      if (!entityTypeId) return;
      
      // Skip if we already loaded this entity type's entities
      if (entities[entityTypeId]) return;
      
      setLoadingEntities(true);
      try {
        console.log(`Fetching entities for type ${entityTypeId}...`);
        const response = await entityApi.getByType(entityTypeId);
        console.log("Entities response:", response);
        
        // Handle both array response and {status, data} response formats
        if (Array.isArray(response)) {
          // Response is already an array of entities
          setEntities(prev => ({
            ...prev,
            [entityTypeId]: response
          }));
          setError(null);
        } else if (response && response.status === 'success') {
          // Response is in {status, data} format
          setEntities(prev => ({
            ...prev,
            [entityTypeId]: response.data || []
          }));
          setError(null);
        } else {
          console.error('Error fetching entities:', response?.message || 'Unknown error');
          setError(`Failed to load entities: ${response?.message || 'Unknown error'}`);
        }
      } catch (err) {
        console.error("Error fetching entities:", err);
        setError(`Failed to load entities: ${err.message || 'Please try again later.'}`);
      } finally {
        setLoadingEntities(false);
      }
    };

    if (selectedEntityTypeId) {
      fetchEntitiesForType(selectedEntityTypeId);
    }
  }, [selectedEntityTypeId, entities]);

  // Handle entity type selection
  const handleEntityTypeChange = (event) => {
    setSelectedEntityTypeId(event.target.value);
  };
  
  // Handle entity selection/deselection
  const handleEntityToggle = (entityId) => {
    const currentIndex = selectedEntityIds.indexOf(entityId);
    const newSelectedEntityIds = [...selectedEntityIds];
    
    if (currentIndex === -1) {
      // Add entity
      newSelectedEntityIds.push(entityId);
    } else {
      // Remove entity
      newSelectedEntityIds.splice(currentIndex, 1);
    }
    
    setSelectedEntityIds(newSelectedEntityIds);
  };

  // Handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    
    try {
      // Validate entity selection
      if (selectedEntityIds.length === 0) {
        setError("Please select at least one entity");
        setSubmitting(false);
        return;
      }
      
      // Validate turns and rounds
      if (nTurns < 1 || simulationRounds < 1) {
        setError("Number of turns and rounds must be at least 1");
        setSubmitting(false);
        return;
      }
      
      let response;
      
      if (isContinuation && continuationData) {
        // Create continuation data
        const continuationOptions = {
          n_turns: nTurns,
          simulation_rounds: simulationRounds,
          interaction_type: interactionType,
          language: language
        };
        
        console.log("Continuing simulation with options:", continuationOptions);
        response = await unifiedSimulationApi.continue(continuationData.id, continuationOptions);
      } else {
        // Create unified simulation data
        const simulationData = {
          name: simulationName,
          context: simulationContext,
          entities: selectedEntityIds,
          n_turns: nTurns,
          simulation_rounds: simulationRounds,
          interaction_type: interactionType,
          language: language,
          metadata: {
            created_at: new Date().toISOString()
          }
        };
        
        console.log("Creating unified simulation with data:", simulationData);
        response = await unifiedSimulationApi.create(simulationData);
      }
      
      console.log('Simulation response:', response);
      
      if (response && response.status === 'success') {
        navigate(`/simulations/${response.data.id}`);
      } else {
        throw new Error(response?.message || 'Unknown error occurred');
      }
    } catch (err) {
      console.error("Error creating simulation:", err);
      setError(`Failed to create simulation: ${err.message || 'Please check your inputs and try again.'}`);
      setSubmitting(false);
    }
  };

  // Find entity by ID across all entity types
  const findEntityById = (entityId) => {
    for (const typeId in entities) {
      const entity = entities[typeId].find(e => e.id === entityId);
      if (entity) return entity;
    }
    return null;
  };

  // Render selected entities
  const renderSelectedEntities = () => {
    return (
      <div className="mt-6">
        <h3 className="text-xl font-semibold text-blue-300 mb-3">
          Selected Entities ({selectedEntityIds.length})
        </h3>
        
        {selectedEntityIds.length === 0 ? (
          <p className="text-gray-400 italic">
            No entities selected
          </p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {selectedEntityIds.map((entityId) => {
              const entity = findEntityById(entityId);
              if (!entity) return null;
              
              return (
                <div 
                  key={entityId}
                  className="bg-gray-700 rounded-lg p-3 relative"
                >
                  <h4 className="text-white font-medium mb-1">{entity.name}</h4>
                  <p className="text-gray-300 text-sm line-clamp-2">{entity.description}</p>
                  <button 
                    className="absolute top-2 right-2 text-red-400 hover:text-red-300 transition-colors"
                    onClick={() => handleEntityToggle(entityId)}
                    aria-label="Remove entity"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingIndicator />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-blue-300">
          {isContinuation ? 'Continue Simulation' : 'Create New Simulation'}
        </h1>
        <button 
          className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-2 px-4 rounded-md transition-colors"
          onClick={() => navigate('/simulations')}
        >
          Back to Simulations
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-gray-800 border border-gray-700 rounded-lg p-6">
        <div className="mb-6">
          <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="simulationName">
            Simulation Name
          </label>
          <input
            id="simulationName"
            type="text"
            value={simulationName}
            onChange={(e) => setSimulationName(e.target.value)}
            className="bg-gray-700 text-white border border-gray-600 rounded-md p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter a name for this simulation"
          />
        </div>

        <div className="mb-6">
          <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="simulationContext">
            Context
          </label>
          <textarea
            id="simulationContext"
            value={simulationContext}
            onChange={(e) => setSimulationContext(e.target.value)}
            rows={5}
            className="bg-gray-700 text-white border border-gray-600 rounded-md p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Describe the situation or environment for the entities"
            disabled={isContinuation}
          />
          {isContinuation && (
            <p className="mt-1 text-gray-400 text-sm">Context cannot be changed for continuations</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
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
            <p className="mt-1 text-gray-400 text-sm">Number of dialogue turns per round (1-10)</p>
          </div>

          <div>
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
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="interactionType">
              Interaction Type
            </label>
            <input
              id="interactionType"
              type="text"
              value={interactionType}
              onChange={(e) => setInteractionType(e.target.value)}
              className="bg-gray-700 text-white border border-gray-600 rounded-md p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="discussion"
            />
            <p className="mt-1 text-gray-400 text-sm">
              How entities interact (e.g., discussion, debate, trade, fight)
              {isContinuation && " - You can change this for the continuation"}
            </p>
          </div>

          <div>
            <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="language">
              Language
            </label>
            <input
              id="language"
              type="text"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-gray-700 text-white border border-gray-600 rounded-md p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="English"
            />
            <p className="mt-1 text-gray-400 text-sm">
              Output language for the interaction
              {isContinuation && " - You can change this for the continuation"}
            </p>
          </div>
        </div>

        {!isContinuation && (
          <div className="mb-6">
            <label className="block text-gray-300 text-sm font-medium mb-2" htmlFor="entityType">
              Entity Type
            </label>
            <select
              id="entityType"
              value={selectedEntityTypeId}
              onChange={handleEntityTypeChange}
              className="bg-gray-700 text-white border border-gray-600 rounded-md p-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="" disabled>Select Entity Type</option>
              {entityTypes.map((type) => (
                <option key={type.id} value={type.id}>{type.name}</option>
              ))}
            </select>
          </div>
        )}

        {!isContinuation && selectedEntityTypeId && (
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-blue-300 mb-3">
              Available Entities
            </h3>
            
            {loadingEntities ? (
              <div className="text-center py-4">
                <div className="animate-spin h-8 w-8 text-blue-500 mx-auto">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
                <p className="text-gray-300 mt-2">Loading entities...</p>
              </div>
            ) : !entities[selectedEntityTypeId] || entities[selectedEntityTypeId].length === 0 ? (
              <p className="text-gray-400 italic">No entities available for this type</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {entities[selectedEntityTypeId].map((entity) => (
                  <div 
                    key={entity.id}
                    className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                      selectedEntityIds.includes(entity.id) 
                        ? 'border-blue-400 bg-blue-900 bg-opacity-20' 
                        : 'border-gray-700 bg-gray-800 hover:bg-gray-750'
                    }`}
                    onClick={() => handleEntityToggle(entity.id)}
                  >
                    <div className="flex items-center mb-2">
                      <input
                        type="checkbox"
                        checked={selectedEntityIds.includes(entity.id)}
                        onChange={() => {}}
                        className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-offset-gray-800"
                      />
                      <h3 className="ml-2 text-white font-medium">{entity.name}</h3>
                    </div>
                    <p className="text-gray-300 text-sm line-clamp-2">{entity.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {renderSelectedEntities()}

        <div className="mt-8 flex justify-end">
          <button 
            type="button" 
            className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-2 px-4 rounded-md transition-colors mr-4"
            onClick={() => navigate('/simulations')}
            disabled={submitting}
          >
            Cancel
          </button>
          <button 
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-6 rounded-md transition-colors flex items-center"
            disabled={submitting}
          >
            {submitting ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </>
            ) : (
              isContinuation ? 'Continue Simulation' : 'Create Simulation'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SimulationCreate; 