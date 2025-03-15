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
  const [generationMethod, setGenerationMethod] = useState('multi-step'); // Default to multi-step method
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
    // Load generation method if saved
    const savedGenerationMethod = localStorage.getItem('entityGenerationSettings.generationMethod');
    
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

    if (savedGenerationMethod) {
      setGenerationMethod(savedGenerationMethod);
    }
  }, [entityTypes, defaultEntityTypeId]);
  
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
  
  // Handle count changes
  const handleCountChange = (e) => {
    const value = parseInt(e.target.value);
    if (!isNaN(value) && value >= 1 && value <= 50) {
      setCount(value);
      // Save to localStorage
      localStorage.setItem('entityGenerationSettings.count', value);
    }
  };
  
  // Handle variability changes
  const handleVariabilityChange = (e) => {
    const value = parseFloat(e.target.value);
    setVariability(value);
    // Save to localStorage
    localStorage.setItem('entityGenerationSettings.variability', value);
  };
  
  // Handle batch generation option changes
  const handleBatchGenerationChange = (e) => {
    const useBatch = e.target.checked;
    setUseBatchGeneration(useBatch);
    // Save to localStorage
    localStorage.setItem('entityGenerationSettings.useBatchGeneration', useBatch);
  };

  // Handle generation method changes
  const handleGenerationMethodChange = (e) => {
    const method = e.target.value;
    setGenerationMethod(method);
    // Save to localStorage
    localStorage.setItem('entityGenerationSettings.generationMethod', method);
  };
  
  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    setError(null);
    
    // Validate form
    if (!entityTypeId) {
      setError('Please select an entity type');
      return;
    }
    
    if (count < 1 || count > 50) {
      setError('Count must be between 1 and 50');
      return;
    }
    
    if (variability < 0 || variability > 1) {
      setError('Variability must be between 0 and 1');
      return;
    }
    
    // Submit form
    onSubmit({
      entityTypeId,
      entityDescription,
      count,
      variability,
      useBatchGeneration, // Include the batch generation preference
      generationMethod // Include the generation method
    });
  };
  
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Generate Entities</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
          {error}
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
            <option value="">Select an entity type</option>
            {entityTypes.map(type => (
              <option key={type.id} value={type.id}>
                {type.name}
              </option>
            ))}
          </select>
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2" htmlFor="entityDescription">
            Entity Description (optional)
          </label>
          <textarea
            id="entityDescription"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 dark:text-gray-300 dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={entityDescription}
            onChange={(e) => setEntityDescription(e.target.value)}
            placeholder="Optional custom description to guide entity generation"
            rows={3}
            disabled={disabled}
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
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
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
            Batch generation creates multiple entities in a single request, resulting in greater diversity.
            By default, we use the new multi-step approach with bisociative fueling for maximum creativity.
            <strong> Highly recommended</strong> when generating multiple entities.
          </p>
        </div>

        {useBatchGeneration && (
          <div className="mb-6">
            <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
              Generation Method
            </label>
            <div className="flex flex-col space-y-2">
              <label className="inline-flex items-center">
                <input
                  type="radio"
                  className="form-radio"
                  name="generationMethod"
                  value="multi-step"
                  checked={generationMethod === "multi-step"}
                  onChange={handleGenerationMethodChange}
                  disabled={disabled}
                />
                <span className="ml-2 text-gray-700 dark:text-gray-300">Multi-step (recommended)</span>
              </label>
              <p className="text-xs text-gray-600 dark:text-gray-400 ml-6 mb-2">
                Uses a two-step approach with "bisociative fueling" (random inspiring words) to boost creativity.
                This method generates each dimension separately and then combines them with creative elements
                to produce highly varied names, backstories, and characteristics.
              </p>
              
              <label className="inline-flex items-center">
                <input
                  type="radio"
                  className="form-radio"
                  name="generationMethod"
                  value="batch"
                  checked={generationMethod === "batch"}
                  onChange={handleGenerationMethodChange}
                  disabled={disabled}
                />
                <span className="ml-2 text-gray-700 dark:text-gray-300">Classic batch</span>
              </label>
              <p className="text-xs text-gray-600 dark:text-gray-400 ml-6">
                Uses the original batch generation method, which creates multiple entities in a single request.
              </p>
            </div>
          </div>
        )}
        
        <div className="flex items-center justify-between">
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline flex items-center"
            disabled={disabled}
          >
            Generate
            {useBatchGeneration && generationMethod === 'multi-step' && (
              <span className="ml-2 bg-blue-700 text-xs px-2 py-1 rounded-full">Multi-Step</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EntityGenerationForm; 