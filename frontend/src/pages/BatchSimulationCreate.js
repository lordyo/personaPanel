import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { batchSimulationApi, entityApi, entityTypeApi } from '../services/api';
import LoadingIndicator from '../components/LoadingIndicator';

/**
 * Page component for creating new batch simulations
 */
const BatchSimulationCreate = () => {
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    context: '',
    entity_ids: [],
    interaction_size: 2,
    num_simulations: 3,
    n_turns: 1,
    simulation_rounds: 1,
    metadata: {
      tags: []
    }
  });
  
  // Entity selection
  const [entityTypes, setEntityTypes] = useState([]);
  const [selectedEntityType, setSelectedEntityType] = useState('');
  const [entities, setEntities] = useState([]);
  const [selectedEntities, setSelectedEntities] = useState([]);
  const [loadingEntities, setLoadingEntities] = useState(false);
  
  // Max simulations based on entity combinations
  const [maxSimulations, setMaxSimulations] = useState(0);
  
  // Form submission state
  const [loading, setLoading] = useState(false);
  const [loadingTypes, setLoadingTypes] = useState(true);
  const [error, setError] = useState(null);
  const [tagInput, setTagInput] = useState('');
  
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get the active tab from location state if available
  const activeTab = location.state?.activeTab || 'batch';
  
  // Load entity types
  useEffect(() => {
    const fetchEntityTypes = async () => {
      try {
        setLoadingTypes(true);
        const response = await entityTypeApi.getAll();
        if (response && response.status === 'success') {
          setEntityTypes(response.data || []);
        } else {
          console.error('Error fetching entity types:', response?.message || 'Unknown error');
          setError(`Failed to load entity types: ${response?.message || 'Please try again'}`);
        }
      } catch (err) {
        console.error('Error fetching entity types:', err);
        setError(`Failed to load entity types: ${err.message || 'Please try again'}`);
      } finally {
        setLoadingTypes(false);
      }
    };
    
    fetchEntityTypes();
  }, []);
  
  // Load entities when entity type is selected
  useEffect(() => {
    const fetchEntities = async () => {
      if (!selectedEntityType) return;
      
      try {
        setLoadingEntities(true);
        const entities = await entityApi.getByType(selectedEntityType);
        if (Array.isArray(entities)) {
          setEntities(entities);
        } else {
          console.error('Error fetching entities: Unexpected response format');
          setError('Failed to load entities: Unexpected response format');
          setEntities([]);
        }
      } catch (err) {
        console.error('Error fetching entities:', err);
        setError(`Failed to load entities: ${err.message || 'Please try again'}`);
        setEntities([]);
      } finally {
        setLoadingEntities(false);
      }
    };
    
    fetchEntities();
  }, [selectedEntityType]);
  
  // Calculate max simulations when selection changes
  useEffect(() => {
    const totalEntities = formData.entity_ids.length;
    const k = formData.interaction_size;
    
    if (totalEntities >= k && k > 0) {
      // Calculate maximum number of combinations: C(n,k) = n! / (k! * (n-k)!)
      const factorial = (num) => (num <= 1 ? 1 : num * factorial(num - 1));
      const maxCombinations = factorial(totalEntities) / (factorial(k) * factorial(totalEntities - k));
      setMaxSimulations(Math.floor(maxCombinations));
    } else {
      setMaxSimulations(0);
    }
  }, [formData.entity_ids, formData.interaction_size]);
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // Handle numeric fields
    if (['interaction_size', 'num_simulations', 'n_turns', 'simulation_rounds'].includes(name)) {
      const numValue = parseInt(value, 10);
      
      // Validate num_simulations against maxSimulations
      if (name === 'num_simulations' && numValue > maxSimulations) {
        setFormData({
          ...formData,
          [name]: maxSimulations
        });
        return;
      }
      
      setFormData({
        ...formData,
        [name]: isNaN(numValue) ? '' : numValue
      });
      return;
    }
    
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  const handleEntityTypeChange = (e) => {
    setSelectedEntityType(e.target.value);
    setSelectedEntities([]);
    setFormData({
      ...formData,
      entity_ids: []
    });
  };
  
  const handleEntitySelection = (entityId) => {
    // Add or remove from selected entities
    const isSelected = formData.entity_ids.includes(entityId);
    
    if (isSelected) {
      // Remove entity
      setFormData({
        ...formData,
        entity_ids: formData.entity_ids.filter(id => id !== entityId)
      });
    } else {
      // Add entity
      setFormData({
        ...formData,
        entity_ids: [...formData.entity_ids, entityId]
      });
    }
  };
  
  const handleSelectAllEntities = () => {
    const allEntityIds = entities.map(entity => entity.id);
    setFormData({
      ...formData,
      entity_ids: allEntityIds
    });
  };
  
  const handleDeselectAllEntities = () => {
    setFormData({
      ...formData,
      entity_ids: []
    });
  };
  
  const handleAddTag = (e) => {
    e.preventDefault();
    
    if (tagInput.trim() && !formData.metadata.tags.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        metadata: {
          ...formData.metadata,
          tags: [...formData.metadata.tags, tagInput.trim()]
        }
      });
      setTagInput('');
    }
  };
  
  const handleRemoveTag = (tagToRemove) => {
    setFormData({
      ...formData,
      metadata: {
        ...formData.metadata,
        tags: formData.metadata.tags.filter(tag => tag !== tagToRemove)
      }
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.name.trim()) {
      setError('Please provide a name for the batch simulation');
      return;
    }
    
    if (!formData.context.trim()) {
      setError('Please provide a context for the simulation');
      return;
    }
    
    if (formData.entity_ids.length < formData.interaction_size) {
      setError(`You need at least ${formData.interaction_size} entities for the selected interaction size`);
      return;
    }
    
    if (formData.num_simulations <= 0) {
      setError('Number of simulations must be greater than 0');
      return;
    }
    
    if (formData.num_simulations > maxSimulations) {
      setError(`Number of simulations cannot exceed ${maxSimulations} for the selected entities and interaction size`);
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Prepare request data
      const batchData = {
        name: formData.name,
        description: formData.description,
        context: formData.context,
        entity_ids: formData.entity_ids,
        interaction_size: formData.interaction_size,
        num_simulations: formData.num_simulations,
        n_turns: formData.n_turns,
        simulation_rounds: formData.simulation_rounds,
        metadata: formData.metadata
      };
      
      console.log('Submitting batch simulation data:', batchData);
      const response = await batchSimulationApi.create(batchData);
      console.log('Batch simulation creation response:', response);
      
      // Check for response.data which contains the created batch simulation if the API follows the format
      // Or check for direct success status
      if (response && (response.status === 'success' || response.id)) {
        // If we have an ID in the response, we know the batch was created
        const successMessage = 'Batch simulation created successfully! It may take some time to process all simulations.';
        console.log(successMessage, response);
        
        // Redirect to the simulations list with batch tab selected
        navigate('/simulations', { 
          state: { 
            message: successMessage,
            activeTab: 'batch'
          }
        });
      } else {
        console.error('Error creating batch simulation:', response?.message || 'Unknown error');
        setError(`Failed to create batch simulation: ${response?.message || 'Please try again'}`);
      }
    } catch (err) {
      console.error('Error creating batch simulation:', err);
      setError(`Failed to create batch simulation: ${err.message || 'Please try again'}`);
    } finally {
      setLoading(false);
    }
  };
  
  // Entity combinations info text
  const getCombinationsInfo = () => {
    const totalEntities = formData.entity_ids.length;
    const k = formData.interaction_size;
    
    if (totalEntities < k) {
      return `You need at least ${k} entities for interaction size of ${k}.`;
    }
    
    if (maxSimulations === 0) {
      return 'No valid combinations possible.';
    }
    
    return `Maximum ${maxSimulations} possible combinations with ${totalEntities} entities and interaction size of ${k}.`;
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-blue-300 mb-2">Create Batch Simulation</h1>
        <p className="text-gray-300">
          Batch simulations let you run multiple simulations in parallel with different entity combinations.
        </p>
      </div>
      
      {error && (
        <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-8">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-blue-300 mb-4">Basic Information</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Name */}
            <div>
              <label htmlFor="name" className="block text-gray-300 font-medium mb-2">
                Batch Name <span className="text-red-400">*</span>
              </label>
              <input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Enter a name for this batch"
                className="w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
            
            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-gray-300 font-medium mb-2">
                Description
              </label>
              <input
                id="description"
                name="description"
                type="text"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Optional description"
                className="w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          {/* Context */}
          <div className="mt-4">
            <label htmlFor="context" className="block text-gray-300 font-medium mb-2">
              Context <span className="text-red-400">*</span>
            </label>
            <textarea
              id="context"
              name="context"
              value={formData.context}
              onChange={handleInputChange}
              placeholder="Describe the situation or prompt for the simulations"
              rows={4}
              className="w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <p className="text-sm text-gray-400 mt-1">
              This context will be used for all simulations in the batch.
            </p>
          </div>
          
          {/* Tags */}
          <div className="mt-4">
            <label className="block text-gray-300 font-medium mb-2">
              Tags
            </label>
            <div className="flex flex-wrap gap-2 mb-2">
              {formData.metadata.tags.map(tag => (
                <span 
                  key={tag} 
                  className="bg-gray-700 text-blue-300 rounded-full px-3 py-1 text-sm flex items-center"
                >
                  {tag}
                  <button 
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="ml-2 text-gray-400 hover:text-gray-200"
                    aria-label="Remove tag"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <div className="flex">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                placeholder="Add tags..."
                className="flex-grow bg-gray-700 border border-gray-600 rounded-l-md py-2 px-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="button"
                onClick={handleAddTag}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-r-md transition-colors"
              >
                Add
              </button>
            </div>
          </div>
        </div>
        
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-blue-300 mb-4">Entity Selection</h2>
          
          {/* Entity Type Selector */}
          <div className="mb-4">
            <label htmlFor="entityType" className="block text-gray-300 font-medium mb-2">
              Entity Type
            </label>
            {loadingTypes ? (
              <div className="flex items-center text-gray-400">
                <LoadingIndicator size="small" />
                <span className="ml-2">Loading entity types...</span>
              </div>
            ) : (
              <select
                id="entityType"
                value={selectedEntityType}
                onChange={handleEntityTypeChange}
                className="w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select an entity type</option>
                {entityTypes.map(type => (
                  <option key={type.id} value={type.id}>
                    {type.name}
                  </option>
                ))}
              </select>
            )}
          </div>
          
          {/* Entities List */}
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <label className="block text-gray-300 font-medium">
                Available Entities
              </label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleSelectAllEntities}
                  className="text-sm text-blue-400 hover:text-blue-300"
                  disabled={loadingEntities || entities.length === 0}
                >
                  Select All
                </button>
                <button
                  type="button"
                  onClick={handleDeselectAllEntities}
                  className="text-sm text-blue-400 hover:text-blue-300"
                  disabled={loadingEntities || formData.entity_ids.length === 0}
                >
                  Deselect All
                </button>
              </div>
            </div>
            
            {loadingEntities ? (
              <div className="flex items-center justify-center h-24 bg-gray-700 rounded-md">
                <LoadingIndicator size="medium" />
              </div>
            ) : entities.length === 0 ? (
              <div className="text-center py-4 bg-gray-700 rounded-md text-gray-400">
                {selectedEntityType ? 'No entities found for this type' : 'Select an entity type to view entities'}
              </div>
            ) : (
              <div className="max-h-60 overflow-y-auto border border-gray-700 rounded-md">
                <ul className="divide-y divide-gray-700">
                  {entities.map(entity => (
                    <li key={entity.id} className="p-3 hover:bg-gray-700">
                      <label className="flex items-start cursor-pointer">
                        <input
                          type="checkbox"
                          checked={formData.entity_ids.includes(entity.id)}
                          onChange={() => handleEntitySelection(entity.id)}
                          className="mt-1 h-4 w-4 text-blue-600 rounded border-gray-600 focus:ring-blue-500 focus:ring-offset-gray-800"
                        />
                        <div className="ml-3">
                          <span className="block font-medium text-gray-200">{entity.name}</span>
                          <span className="block text-sm text-gray-400 line-clamp-2">{entity.description}</span>
                        </div>
                      </label>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <p className="text-sm text-gray-400 mt-2">
              Selected: {formData.entity_ids.length} entities
            </p>
          </div>
        </div>
        
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-blue-300 mb-4">Simulation Parameters</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Interaction Size */}
            <div>
              <label htmlFor="interaction_size" className="block text-gray-300 font-medium mb-2">
                Entities Per Simulation <span className="text-red-400">*</span>
              </label>
              <input
                id="interaction_size"
                name="interaction_size"
                type="number"
                min="1"
                max={formData.entity_ids.length}
                value={formData.interaction_size}
                onChange={handleInputChange}
                className="w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <p className="text-sm text-gray-400 mt-1">
                Number of entities to include in each simulation (1=solo, 2=dyadic, 3+=group)
              </p>
            </div>
            
            {/* Number of Simulations */}
            <div>
              <label htmlFor="num_simulations" className="block text-gray-300 font-medium mb-2">
                Number of Simulations <span className="text-red-400">*</span>
              </label>
              <input
                id="num_simulations"
                name="num_simulations"
                type="number"
                min="1"
                max={maxSimulations > 0 ? maxSimulations : 100}
                value={formData.num_simulations}
                onChange={handleInputChange}
                className="w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <p className="text-sm text-gray-400 mt-1">
                {getCombinationsInfo()}
              </p>
            </div>
            
            {/* Turns Per Round */}
            <div>
              <label htmlFor="n_turns" className="block text-gray-300 font-medium mb-2">
                Turns Per Round
              </label>
              <input
                id="n_turns"
                name="n_turns"
                type="number"
                min="1"
                max="5"
                value={formData.n_turns}
                onChange={handleInputChange}
                className="w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-sm text-gray-400 mt-1">
                Number of back-and-forth exchanges per round (default: 1)
              </p>
            </div>
            
            {/* Simulation Rounds */}
            <div>
              <label htmlFor="simulation_rounds" className="block text-gray-300 font-medium mb-2">
                Simulation Rounds
              </label>
              <input
                id="simulation_rounds"
                name="simulation_rounds"
                type="number"
                min="1"
                max="3"
                value={formData.simulation_rounds}
                onChange={handleInputChange}
                className="w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-sm text-gray-400 mt-1">
                Number of sequential LLM calls (default: 1)
              </p>
            </div>
          </div>
        </div>
        
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => navigate('/simulations', { state: { activeTab } })}
            className="px-4 py-2 text-gray-300 hover:text-white bg-gray-700 hover:bg-gray-600 rounded-md transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md shadow transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <LoadingIndicator size="small" />
                <span className="ml-2">Creating...</span>
              </>
            ) : (
              'Create Batch Simulation'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default BatchSimulationCreate; 