import React, { useState, useEffect } from 'react';

/**
 * Form for generating new entities based on entity types.
 * 
 * @param {Object} props - Component props
 * @param {Array} props.entityTypes - Available entity types
 * @param {Function} props.onSubmit - Function to call when form is submitted
 * @param {boolean} props.disabled - Whether the form is disabled
 * @param {string} props.preselectedEntityTypeId - Optional entity type ID to preselect
 * @returns {JSX.Element} - Rendered component
 */
const EntityGenerationForm = ({ 
  entityTypes, 
  onSubmit, 
  disabled = false,
  preselectedEntityTypeId = ''
}) => {
  const [entityTypeId, setEntityTypeId] = useState(preselectedEntityTypeId || '');
  const [entityDescription, setEntityDescription] = useState('');
  const [count, setCount] = useState(1);
  const [variability, setVariability] = useState(0.5);
  const [error, setError] = useState(null);
  
  // Update entity type and description when preselectedEntityTypeId changes
  useEffect(() => {
    if (preselectedEntityTypeId && entityTypes.some(type => type.id === preselectedEntityTypeId)) {
      setEntityTypeId(preselectedEntityTypeId);
      
      // Also set the description based on this type
      const selectedType = entityTypes.find(type => type.id === preselectedEntityTypeId);
      if (selectedType && selectedType.description) {
        setEntityDescription(selectedType.description);
      }
    }
  }, [preselectedEntityTypeId, entityTypes]);
  
  // Load saved settings from localStorage when component mounts
  useEffect(() => {
    // Only load saved settings if no preselectedEntityTypeId is provided
    if (!preselectedEntityTypeId) {
      // Load entityTypeId if saved
      const savedEntityTypeId = localStorage.getItem('entityGenerationSettings.entityTypeId');
      // Load count if saved
      const savedCount = localStorage.getItem('entityGenerationSettings.count');
      // Load variability if saved
      const savedVariability = localStorage.getItem('entityGenerationSettings.variability');
      
      // Apply saved settings if they exist
      if (savedEntityTypeId) {
        // Only set if it's a valid entity type id
        if (entityTypes.some(type => type.id === savedEntityTypeId)) {
          setEntityTypeId(savedEntityTypeId);
          
          // Also set the description based on this type
          const selectedType = entityTypes.find(type => type.id === savedEntityTypeId);
          if (selectedType && selectedType.description) {
            setEntityDescription(selectedType.description);
          }
        }
      } else if (entityTypes.length > 0) {
        // Default to first entity type if no saved type
        setEntityTypeId(entityTypes[0].id);
        
        // Initialize the description with the entity type description
        if (entityTypes[0].description) {
          setEntityDescription(entityTypes[0].description);
        }
      }
      
      if (savedCount) {
        setCount(parseInt(savedCount));
      }
      
      if (savedVariability) {
        setVariability(parseFloat(savedVariability));
      }
    }
  }, [entityTypes, preselectedEntityTypeId]);
  
  // Update description when entity type changes
  const handleEntityTypeChange = (e) => {
    const newTypeId = e.target.value;
    setEntityTypeId(newTypeId);
    
    // Update description with the entity type description
    const selectedType = entityTypes.find(type => type.id === newTypeId);
    if (selectedType && selectedType.description) {
      setEntityDescription(selectedType.description);
    } else {
      setEntityDescription('');
    }
    
    // Save entityTypeId to localStorage
    localStorage.setItem('entityGenerationSettings.entityTypeId', newTypeId);
  };
  
  // Save count to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('entityGenerationSettings.count', count.toString());
  }, [count]);
  
  // Save variability to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('entityGenerationSettings.variability', variability.toString());
  }, [variability]);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    setError(null);
    
    if (!entityTypeId) {
      setError("Please select an entity type");
      return;
    }
    
    if (count < 1 || count > 50) {
      setError("Count must be between 1 and 50");
      return;
    }
    
    if (variability < 0 || variability > 1) {
      setError("Variability must be between 0 and 1");
      return;
    }
    
    onSubmit({
      entityTypeId,
      entityDescription,
      count,
      variability
    });
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Generation in progress indicator */}
      {disabled && (
        <div className="bg-blue-900 bg-opacity-30 p-4 rounded mb-4 flex items-center">
          <div className="animate-spin rounded-full h-6 w-6 border-2 border-b-0 border-blue-500 mr-3"></div>
          <div className="text-blue-300">Generating entities... This may take several seconds per entity.</div>
        </div>
      )}
    
      {error && (
        <div className="bg-red-900 p-4 rounded mb-4">
          <p className="text-red-300">{error}</p>
        </div>
      )}
      
      <div className="mb-4">
        <label className="block text-gray-400 text-sm font-medium mb-2" htmlFor="entityType">
          Entity Type (Required)
        </label>
        <select
          id="entityType"
          value={entityTypeId}
          onChange={handleEntityTypeChange}
          className="w-full bg-gray-750 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
          disabled={disabled}
        >
          <option value="">Select an entity type</option>
          {entityTypes.map(type => (
            <option key={type.id} value={type.id}>
              {type.name}
            </option>
          ))}
        </select>
      </div>
      
      <div className="mb-4">
        <label className="block text-gray-400 text-sm font-medium mb-2" htmlFor="entityDescription">
          Entity Description (Optional)
        </label>
        <textarea
          id="entityDescription"
          placeholder="Describe this entity to guide generation (optional)"
          value={entityDescription}
          onChange={(e) => setEntityDescription(e.target.value)}
          className="w-full bg-gray-750 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500 min-h-[80px]"
          disabled={disabled}
        />
        <p className="text-xs text-gray-500 mt-1">
          Prepopulated with the entity type description. You can modify it to further guide generation.
        </p>
      </div>
      
      <div className="mb-4">
        <label className="block text-gray-400 text-sm font-medium mb-2" htmlFor="count">
          Number of Entities to Generate
        </label>
        <input
          id="count"
          type="number"
          min="1"
          max="50"
          value={count}
          onChange={(e) => setCount(parseInt(e.target.value))}
          className="w-full bg-gray-750 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
          disabled={disabled}
        />
        <p className="text-xs text-gray-500 mt-1">
          Generate up to 50 entities at once. Higher numbers will take longer.
        </p>
      </div>
      
      <div className="mb-4">
        <label className="block text-gray-400 text-sm font-medium mb-2" htmlFor="variability">
          Variability: {variability}
        </label>
        <input
          id="variability"
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={variability}
          onChange={(e) => setVariability(parseFloat(e.target.value))}
          className="w-full"
          disabled={disabled}
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>Low</span>
          <span>Medium</span>
          <span>High</span>
        </div>
      </div>
      
      <button
        type="submit"
        className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors disabled:bg-gray-600 disabled:text-gray-400 disabled:cursor-not-allowed"
        disabled={disabled}
      >
        {disabled ? (
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-b-0 border-white mr-2"></div>
            <span>Generating...</span>
          </div>
        ) : 'Generate Entities'}
      </button>
    </form>
  );
};

export default EntityGenerationForm; 