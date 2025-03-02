import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { entityTypeApi } from '../services/api';
import DimensionForm from '../components/DimensionForm';

/**
 * Page component for creating a new entity type from scratch.
 * 
 * @returns {JSX.Element} - Rendered component
 */
const EntityTypeCreate = () => {
  const navigate = useNavigate();
  
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [dimensions, setDimensions] = useState([
    {
      name: '',
      description: '',
      type: ''
    }
  ]);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  
  const handleUpdateDimension = (index, updatedDimension) => {
    const newDimensions = [...dimensions];
    newDimensions[index] = updatedDimension;
    setDimensions(newDimensions);
  };
  
  const handleRemoveDimension = (index) => {
    if (dimensions.length > 1) {
      setDimensions(dimensions.filter((_, i) => i !== index));
    } else {
      setError('Entity types must have at least one dimension');
    }
  };
  
  const handleAddDimension = () => {
    setDimensions([
      ...dimensions,
      {
        name: '',
        description: '',
        type: ''
      }
    ]);
  };
  
  const validateForm = () => {
    if (!name.trim()) {
      setError('Entity type name is required');
      return false;
    }
    
    if (dimensions.length === 0) {
      setError('At least one dimension is required');
      return false;
    }
    
    for (let i = 0; i < dimensions.length; i++) {
      const dim = dimensions[i];
      if (!dim.name || !dim.type) {
        setError(`Dimension ${i + 1} is missing required fields`);
        return false;
      }
      
      if (dim.type === 'categorical' && (!dim.options || dim.options.length === 0)) {
        setError(`Dimension "${dim.name}" needs at least one option`);
        return false;
      }
      
      if (dim.type === 'int' || dim.type === 'float') {
        if (dim.min_value === undefined || dim.max_value === undefined) {
          setError(`Dimension "${dim.name}" needs min and max values`);
          return false;
        }
        
        if (dim.min_value >= dim.max_value) {
          setError(`Dimension "${dim.name}" min value must be less than max value`);
          return false;
        }
        
        if (dim.distribution === 'normal') {
          // Check for either spread_factor (new) or std_deviation (legacy)
          if (dim.spread_factor !== undefined) {
            if (dim.spread_factor <= 0 || dim.spread_factor > 1) {
              setError(`Dimension "${dim.name}" spread factor must be between 0 and 1`);
              return false;
            }
          } else if (dim.std_deviation !== undefined) {
            if (dim.std_deviation <= 0) {
              setError(`Dimension "${dim.name}" needs a positive standard deviation for normal distribution`);
              return false;
            }
          } else {
            setError(`Dimension "${dim.name}" needs a spread factor for normal distribution`);
            return false;
          }
        }
      }
      
      // Legacy validation for 'numerical' type
      if (dim.type === 'numerical') {
        if (dim.min_value === undefined || dim.max_value === undefined) {
          setError(`Dimension "${dim.name}" needs min and max values`);
          return false;
        }
        
        if (dim.min_value >= dim.max_value) {
          setError(`Dimension "${dim.name}" min value must be less than max value`);
          return false;
        }
      }
      
      if (dim.type === 'boolean' && dim.true_percentage !== undefined) {
        if (dim.true_percentage < 0 || dim.true_percentage > 1) {
          setError(`Dimension "${dim.name}" true percentage must be between 0 and 1`);
          return false;
        }
      }
      
      if (dim.type === 'categorical' && dim.distribution_values) {
        const totalPercentage = Object.values(dim.distribution_values).reduce((sum, val) => sum + val, 0);
        if (Math.abs(totalPercentage - 1) > 0.01) {
          // Auto-normalize instead of showing error
          const normalizedValues = {};
          Object.keys(dim.distribution_values).forEach(key => {
            normalizedValues[key] = dim.distribution_values[key] / totalPercentage;
          });
          dim.distribution_values = normalizedValues;
        }
      }
    }
    
    return true;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setSaving(true);
    try {
      const response = await entityTypeApi.create({
        name,
        description,
        dimensions: dimensions.map(d => ({
          name: d.name,
          description: d.description,
          type: d.type,
          options: d.options,
          min_value: d.min_value,
          max_value: d.max_value,
          distribution: d.distribution
        }))
      });
      
      if (response.status === 'success') {
        navigate('/entity-types');
      } else {
        setError(response.message || 'Failed to create entity type');
      }
    } catch (err) {
      setError('Error creating entity type. Please try again.');
      console.error('Error creating entity type:', err);
    } finally {
      setSaving(false);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center mb-6">
        <button
          className="flex items-center text-blue-400 hover:text-blue-300"
          onClick={() => navigate('/entity-types')}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
          </svg>
          Back to Entity Types
        </button>
      </div>
      
      {error && (
        <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
          <p>{error}</p>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 p-6 mb-6">
          <h2 className="text-xl font-semibold text-blue-300 mb-4">Basic Information</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-400 mb-1">
              Entity Type Name <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              className="w-full bg-gray-750 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter a name for this entity type"
              required
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-400 mb-1">
              Description
            </label>
            <textarea
              className="w-full bg-gray-750 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
              rows="3"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe this entity type"
            />
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-blue-300">Dimensions</h2>
            <button
              type="button"
              className="flex items-center px-3 py-1 text-sm rounded border border-blue-400 text-blue-400 hover:bg-blue-400 hover:bg-opacity-10"
              onClick={handleAddDimension}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Add Dimension
            </button>
          </div>
          
          <div className="mb-4">
            <p className="text-gray-400 text-sm">
              Define the dimensions (attributes) for this entity type. Each dimension represents a characteristic 
              that entities of this type will have.
            </p>
          </div>
          
          {dimensions.map((dimension, index) => (
            <DimensionForm
              key={index}
              dimension={dimension}
              onChange={(updatedDimension) => handleUpdateDimension(index, updatedDimension)}
              onRemove={() => handleRemoveDimension(index)}
            />
          ))}
        </div>
        
        <div className="bg-gray-850 px-6 py-4 border-t border-gray-700 flex justify-end">
          <div className="flex space-x-3">
            <button
              type="button"
              className="px-4 py-2 border border-gray-600 rounded text-gray-300 hover:border-gray-500 hover:text-gray-200"
              onClick={() => navigate('/entity-types')}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`px-6 py-2 rounded font-medium ${
                saving 
                  ? 'bg-blue-400 cursor-not-allowed' 
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
              disabled={saving}
            >
              {saving ? 'Creating...' : 'Create Entity Type'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default EntityTypeCreate; 