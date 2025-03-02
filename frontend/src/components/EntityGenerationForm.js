import React, { useState, useEffect } from 'react';

/**
 * Form component for generating entities.
 * 
 * @param {Object} props - Component props
 * @param {Array} props.entityTypes - Available entity types 
 * @param {Function} props.onSubmit - Function to call to generate entities
 * @param {boolean} props.disabled - Whether the form is disabled
 * @returns {JSX.Element} - Rendered component
 */
const EntityGenerationForm = ({ entityTypes, onSubmit, disabled = false }) => {
  const [entityTypeId, setEntityTypeId] = useState('');
  const [entityDescription, setEntityDescription] = useState('');
  const [count, setCount] = useState(1);
  const [variability, setVariability] = useState(0.5);
  const [error, setError] = useState('');
  
  // Load saved settings from localStorage when component mounts
  useEffect(() => {
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
      }
    } else if (entityTypes.length > 0) {
      // Default to first entity type if no saved type
      setEntityTypeId(entityTypes[0].id);
    }
    
    if (savedCount) {
      const parsedCount = parseInt(savedCount);
      if (!isNaN(parsedCount) && parsedCount >= 1 && parsedCount <= 20) {
        setCount(parsedCount);
      }
    }
    
    if (savedVariability) {
      const parsedVariability = parseFloat(savedVariability);
      if (!isNaN(parsedVariability) && parsedVariability >= 0 && parsedVariability <= 1) {
        setVariability(parsedVariability);
      }
    }
  }, [entityTypes]);
  
  // Update description when entity type changes
  useEffect(() => {
    if (entityTypeId) {
      const selectedType = entityTypes.find(type => type.id === entityTypeId);
      if (selectedType && selectedType.description) {
        setEntityDescription(selectedType.description);
      }
      
      // Save entityTypeId to localStorage
      localStorage.setItem('entityGenerationSettings.entityTypeId', entityTypeId);
    }
  }, [entityTypeId, entityTypes]);
  
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
    
    if (!entityTypeId) {
      setError('Please select an entity type.');
      return;
    }
    
    if (count < 1 || count > 20) {
      setError('Count must be between 1 and 20.');
      return;
    }
    
    if (variability < 0 || variability > 1) {
      setError('Variability must be between 0 and 1.');
      return;
    }
    
    setError('');
    onSubmit({
      entityTypeId,
      entityDescription,
      count,
      variability
    });
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div className="mb-4 p-3 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}
      
      <div className="mb-4">
        <label className="block text-gray-400 text-sm font-medium mb-2" htmlFor="entityType">
          Entity Type
        </label>
        <select
          id="entityType"
          value={entityTypeId}
          onChange={(e) => setEntityTypeId(e.target.value)}
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
          Count ({count})
        </label>
        <input
          id="count"
          type="range"
          min="1"
          max="20"
          value={count}
          onChange={(e) => setCount(parseInt(e.target.value))}
          className="w-full"
          disabled={disabled}
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>1</span>
          <span>10</span>
          <span>20</span>
        </div>
      </div>
      
      <div className="mb-6">
        <label className="block text-gray-400 text-sm font-medium mb-2" htmlFor="variability">
          Variability ({variability < 0.33 ? 'Low' : variability < 0.67 ? 'Medium' : 'High'})
        </label>
        <input
          id="variability"
          type="range"
          min="0"
          max="1"
          step="0.05"
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
        {disabled ? 'Generating...' : 'Generate Entities'}
      </button>
    </form>
  );
};

export default EntityGenerationForm; 