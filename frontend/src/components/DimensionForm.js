import React from 'react';

/**
 * Component for rendering a form to edit a single dimension.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.dimension - The dimension to edit
 * @param {Function} props.onChange - Function to call when the dimension changes
 * @param {Function} props.onRemove - Function to call to remove this dimension
 * @returns {JSX.Element} - Rendered component
 */
const DimensionForm = ({ dimension, onChange, onRemove }) => {
  const handleFieldChange = (field, value) => {
    onChange({ ...dimension, [field]: value });
  };

  // Render different controls based on dimension type
  const renderTypeSpecificControls = () => {
    switch (dimension.type) {
      case 'boolean':
        return (
          <div className="mt-2">
            <label className="block text-sm font-medium text-gray-400">Default Value</label>
            <select
              className="mt-1 block w-full bg-gray-750 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
              value={dimension.defaultValue ? 'true' : 'false'}
              onChange={(e) => handleFieldChange('defaultValue', e.target.value === 'true')}
            >
              <option value="true">True</option>
              <option value="false">False</option>
            </select>
          </div>
        );
      
      case 'categorical':
        return (
          <div className="mt-2">
            <label className="block text-sm font-medium text-gray-400">Options (one per line)</label>
            <textarea
              className="mt-1 block w-full bg-gray-750 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
              rows="4"
              value={(dimension.options || []).join('\n')}
              onChange={(e) => handleFieldChange('options', e.target.value.split('\n').filter(Boolean))}
            />
          </div>
        );
      
      case 'numerical':
        return (
          <>
            <div className="grid grid-cols-2 gap-4 mt-2">
              <div>
                <label className="block text-sm font-medium text-gray-400">Min Value</label>
                <input
                  type="number"
                  className="mt-1 block w-full bg-gray-750 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
                  value={dimension.min_value || ''}
                  onChange={(e) => handleFieldChange('min_value', parseFloat(e.target.value))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Max Value</label>
                <input
                  type="number"
                  className="mt-1 block w-full bg-gray-750 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
                  value={dimension.max_value || ''}
                  onChange={(e) => handleFieldChange('max_value', parseFloat(e.target.value))}
                />
              </div>
            </div>
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-400">Distribution</label>
              <select
                className="mt-1 block w-full bg-gray-750 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
                value={dimension.distribution || 'uniform'}
                onChange={(e) => handleFieldChange('distribution', e.target.value)}
              >
                <option value="uniform">Uniform</option>
                <option value="normal">Normal</option>
                <option value="exponential">Exponential</option>
              </select>
            </div>
          </>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="border border-gray-700 rounded-md p-4 mb-4 bg-gray-750">
      <div className="flex justify-between">
        <h3 className="text-md font-medium text-blue-300">{dimension.name || 'New Dimension'}</h3>
        <button 
          type="button"
          className="text-red-400 hover:text-red-300"
          onClick={onRemove}
        >
          Remove
        </button>
      </div>
      
      <div className="mt-2">
        <label className="block text-sm font-medium text-gray-400">Name</label>
        <input
          type="text"
          className="mt-1 block w-full bg-gray-800 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
          value={dimension.name || ''}
          onChange={(e) => handleFieldChange('name', e.target.value)}
        />
      </div>
      
      <div className="mt-2">
        <label className="block text-sm font-medium text-gray-400">Description</label>
        <input
          type="text"
          className="mt-1 block w-full bg-gray-800 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
          value={dimension.description || ''}
          onChange={(e) => handleFieldChange('description', e.target.value)}
        />
      </div>
      
      <div className="mt-2">
        <label className="block text-sm font-medium text-gray-400">Type</label>
        <select
          className="mt-1 block w-full bg-gray-800 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
          value={dimension.type || ''}
          onChange={(e) => handleFieldChange('type', e.target.value)}
        >
          <option value="">Select a type</option>
          <option value="boolean">Boolean</option>
          <option value="categorical">Categorical</option>
          <option value="numerical">Numerical</option>
          <option value="text">Text</option>
        </select>
      </div>
      
      {renderTypeSpecificControls()}
    </div>
  );
};

export default DimensionForm; 