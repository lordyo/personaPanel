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
  const [generationMode, setGenerationMode] = useState('fuel'); // Default to fuel method (previously multi-step)
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
    // Load generation mode if saved
    const savedGenerationMode = localStorage.getItem('entityGenerationSettings.generationMode');
    
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
    
    if (savedGenerationMode) {
      setGenerationMode(savedGenerationMode);
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
  
  // Handle generation mode changes
  const handleGenerationModeChange = (e) => {
    const mode = e.target.value;
    setGenerationMode(mode);
    // Save to localStorage
    localStorage.setItem('entityGenerationSettings.generationMode', mode);
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
    
    // Convert generation mode to the parameters expected by the API
    let useBatchGeneration = false;
    let generationMethod = 'batch';
    
    if (generationMode === 'simple') {
      useBatchGeneration = false;
    } else if (generationMode === 'batch') {
      useBatchGeneration = true;
      generationMethod = 'batch';
    } else if (generationMode === 'fuel') {
      useBatchGeneration = true;
      generationMethod = 'multi-step';
    }
    
    // Submit form
    onSubmit({
      entityTypeId,
      entityDescription,
      count,
      variability,
      useBatchGeneration,
      generationMethod
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
          <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">
            Generation Mode
          </label>
          <div className="space-y-3 mt-2">
            <label className="flex items-start">
              <input
                type="radio"
                className="form-radio mt-1"
                name="generationMode"
                value="simple"
                checked={generationMode === "simple"}
                onChange={handleGenerationModeChange}
                disabled={disabled}
              />
              <div className="ml-2">
                <span className="text-gray-700 dark:text-gray-300">Simple Mode</span>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Generates each entity individually. Best for 1-3 entities when consistency is more important than diversity.
                </p>
              </div>
            </label>
            
            <label className="flex items-start">
              <input
                type="radio"
                className="form-radio mt-1"
                name="generationMode"
                value="batch"
                checked={generationMode === "batch"}
                onChange={handleGenerationModeChange}
                disabled={disabled}
              />
              <div className="ml-2">
                <span className="text-gray-700 dark:text-gray-300">Batch Mode</span>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Generates up to 10 entities in a single request for better efficiency.
                  Provides moderate diversity between entities.
                </p>
              </div>
            </label>
            
            <label className="flex items-start">
              <input
                type="radio"
                className="form-radio mt-1"
                name="generationMode"
                value="fuel"
                checked={generationMode === "fuel"}
                onChange={handleGenerationModeChange}
                disabled={disabled}
              />
              <div className="ml-2">
                <span className="text-gray-700 dark:text-gray-300">Bisociative Fuel Mode (Recommended)</span>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Uses a two-step approach with "bisociative fueling" (random inspiring words) to boost creativity.
                  Produces highly varied names, backstories, and characteristics.
                  Recommended for creating diverse entities.
                </p>
              </div>
            </label>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <button
            type="submit"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline flex items-center"
            disabled={disabled}
          >
            Generate
            {generationMode === 'fuel' && (
              <span className="ml-2 bg-blue-700 text-xs px-2 py-1 rounded-full">Bisociative</span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EntityGenerationForm; 