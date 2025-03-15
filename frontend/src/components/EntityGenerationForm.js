import React, { useState, useEffect } from 'react';

/**
 * Form for generating new entities based on entity types.
 * 
 * @param {Object} props - Component props
 * @param {Array} props.entityTypes - Available entity types
 * @param {Function} props.onSubmit - Function to call when form is submitted
 * @param {boolean} props.disabled - Whether the form is disabled
 * @param {string} props.defaultEntityTypeId - Optional entity type ID to select by default
 * @returns {JSX.Element} - Rendered component
 */
const EntityGenerationForm = ({ entityTypes, onSubmit, disabled = false, defaultEntityTypeId = '' }) => {
  const [entityTypeId, setEntityTypeId] = useState('');
  const [entityDescription, setEntityDescription] = useState('');
  const [count, setCount] = useState(1);
  const [variability, setVariability] = useState(0.5);
  const [useBatchGeneration, setUseBatchGeneration] = useState(true);
  const [error, setError] = useState(null);
  
  // Load saved settings from localStorage when component mounts
  useEffect(() => {
    // First check if we have a default entity type ID from props
    if (defaultEntityTypeId && entityTypes.some(type => type.id === defaultEntityTypeId)) {
      setEntityTypeId(defaultEntityTypeId);
      
      // Set the description based on this type
      const selectedType = entityTypes.find(type => type.id === defaultEntityTypeId);
      if (selectedType && selectedType.description) {
        setEntityDescription(selectedType.description);
      }
      
      // Save to localStorage
      localStorage.setItem('entityGenerationSettings.entityTypeId', defaultEntityTypeId);
      return;
    }
    
    // If no default entity type ID is provided, load from localStorage
    const savedEntityTypeId = localStorage.getItem('entityGenerationSettings.entityTypeId');
    // Load count if saved
    const savedCount = localStorage.getItem('entityGenerationSettings.count');
    // Load variability if saved
    const savedVariability = localStorage.getItem('entityGenerationSettings.variability');
    // Load batch generation preference if saved
    const savedUseBatch = localStorage.getItem('entityGenerationSettings.useBatchGeneration');
    
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
      const parsedCount = parseInt(savedCount);
      if (!isNaN(parsedCount) && parsedCount >= 1 && parsedCount <= 50) {
        setCount(parsedCount);
      }
    }
    
    if (savedVariability) {
      const parsedVariability = parseFloat(savedVariability);
      if (!isNaN(parsedVariability) && parsedVariability >= 0 && parsedVariability <= 1) {
        setVariability(parsedVariability);
      }
    }
    
    if (savedUseBatch) {
      setUseBatchGeneration(savedUseBatch === 'true');
    }
  }, [entityTypes]);
  
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
    
    // Save to localStorage
    localStorage.setItem('entityGenerationSettings.entityTypeId', newTypeId);
  };
  
  // Handle count input change
  const handleCountChange = (e) => {
    const newCount = parseInt(e.target.value);
    if (!isNaN(newCount) && newCount >= 1 && newCount <= 50) {
      setCount(newCount);
      
      // Save to localStorage
      localStorage.setItem('entityGenerationSettings.count', newCount);
    }
  };
  
  // Handle variability slider change
  const handleVariabilityChange = (e) => {
    const newVariability = parseFloat(e.target.value);
    if (!isNaN(newVariability) && newVariability >= 0 && newVariability <= 1) {
      setVariability(newVariability);
      
      // Save to localStorage
      localStorage.setItem('entityGenerationSettings.variability', newVariability);
    }
  };
  
  // Handle batch generation toggle
  const handleBatchGenerationChange = (e) => {
    const useBatch = e.target.checked;
    setUseBatchGeneration(useBatch);
    
    // Save to localStorage
    localStorage.setItem('entityGenerationSettings.useBatchGeneration', useBatch);
    
    // If batch generation is enabled, increase variability for better diversity
    if (useBatch) {
      setVariability(Math.max(variability, 0.7));
    }
  };
  
  // Form submission handler
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate the form
    if (!entityTypeId) {
      setError('Please select an entity type');
      return;
    }
    
    // Check if count is valid
    const countInt = parseInt(count);
    if (isNaN(countInt) || countInt < 1 || countInt > 50) {
      setError('Count must be between 1 and 50');
      return;
    }
    
    // Check if variability is valid
    const variabilityFloat = parseFloat(variability);
    if (isNaN(variabilityFloat) || variabilityFloat < 0 || variabilityFloat > 1) {
      setError('Variability must be between 0 and 1');
      return;
    }
    
    // Prepare form data to submit
    const formData = {
      entityTypeId,
      entityDescription,
      count: countInt,
      variability: variabilityFloat,
      useBatchGeneration // Include the batch generation preference
    };
    
    // Submit the form
    onSubmit(formData);
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Generate Entities</h2>
      
      {error && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4" role="alert">
          <p>{error}</p>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="entityType">
            Entity Type
          </label>
          <select
            id="entityType"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-gray-300 dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={entityTypeId}
            onChange={handleEntityTypeChange}
            disabled={disabled}
          >
            {entityTypes.map(type => (
              <option key={type.id} value={type.id}>
                {type.name}
              </option>
            ))}
          </select>
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="entityDescription">
            Entity Description (Optional)
          </label>
          <textarea
            id="entityDescription"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-gray-300 dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="Additional description to guide entity generation"
            value={entityDescription}
            onChange={(e) => setEntityDescription(e.target.value)}
            disabled={disabled}
            rows="3"
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="count">
            Count (1-50)
          </label>
          <input
            id="count"
            type="number"
            min="1"
            max="50"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-gray-300 dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={count}
            onChange={handleCountChange}
            disabled={disabled}
          />
        </div>
        
        <div className="mb-6">
          <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="variability">
            Variability: {variability.toFixed(1)}
          </label>
          <input
            id="variability"
            type="range"
            min="0"
            max="1"
            step="0.1"
            className="w-full"
            value={variability}
            onChange={handleVariabilityChange}
            disabled={disabled}
          />
          <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400">
            <span>Typical</span>
            <span>Distinct</span>
            <span>Unique</span>
          </div>
        </div>
        
        <div className="mb-6">
          <label className="flex items-center">
            <input
              type="checkbox"
              className="form-checkbox h-5 w-5 text-blue-600"
              checked={useBatchGeneration}
              onChange={handleBatchGenerationChange}
              disabled={disabled}
            />
            <span className="ml-2 text-gray-700 dark:text-gray-300">Use batch generation for more diverse entities</span>
          </label>
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 ml-7">
            Batch generation creates multiple entities at once, resulting in greater diversity between them.
            The AI will ensure each entity has a distinct name, appearance, and characteristics.
            <strong>Highly recommended</strong> when generating multiple entities.
          </p>
        </div>
        
        <div className="flex items-center justify-between">
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            disabled={disabled}
          >
            Generate
          </button>
        </div>
      </form>
    </div>
  );
};

export default EntityGenerationForm; 