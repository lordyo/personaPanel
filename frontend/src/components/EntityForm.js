import React, { useState, useEffect } from 'react';

/**
 * Form component for editing entity properties.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.entity - The entity to edit
 * @param {Object} props.entityType - The entity type
 * @param {Function} props.onSave - Function to call when saving changes
 * @param {boolean} props.isUpdating - Whether the entity is currently being updated
 * @returns {JSX.Element} - Rendered component
 */
const EntityForm = ({ entity, entityType, onSave, isUpdating }) => {
  const [formData, setFormData] = useState({});
  const [error, setError] = useState('');

  useEffect(() => {
    if (entity && entity.properties) {
      setFormData(entity.properties);
    }
  }, [entity]);

  const handleChange = (dimensionKey, value) => {
    setFormData(prev => ({
      ...prev,
      [dimensionKey]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!entityType || !entity) {
      setError('Missing required entity data');
      return;
    }
    
    onSave({
      ...entity,
      properties: formData
    });
  };

  if (!entityType || !entity) {
    return (
      <div className="p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
        Missing required entity data
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div className="mb-4 p-3 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}
      
      <div className="mb-4">
        <h3 className="text-lg font-medium text-blue-300 mb-2">Entity Properties</h3>
        <p className="text-sm text-gray-400 mb-4">
          Edit the properties for this {entityType.name}
        </p>
      </div>
      
      <div className="space-y-4 mb-6">
        {entityType.dimensions.map((dimension) => (
          <div key={dimension.key} className="mb-4">
            <label className="block text-gray-400 text-sm font-medium mb-2" htmlFor={dimension.key}>
              {dimension.name}
            </label>
            <input
              id={dimension.key}
              type="text"
              value={formData[dimension.key] || ''}
              onChange={(e) => handleChange(dimension.key, e.target.value)}
              className="w-full bg-gray-750 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
            />
            {dimension.description && (
              <p className="text-xs text-gray-500 mt-1">{dimension.description}</p>
            )}
          </div>
        ))}
      </div>
      
      <button
        type="submit"
        disabled={isUpdating}
        className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isUpdating ? 'Saving...' : 'Save Changes'}
      </button>
    </form>
  );
};

export default EntityForm; 