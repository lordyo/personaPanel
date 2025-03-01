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
          className="text-blue-600 hover:text-blue-800 mr-4"
          onClick={() => navigate('/entity-types')}
        >
          &larr; Back
        </button>
        <h1 className="text-2xl font-bold">Create New Entity Type</h1>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <p>{error}</p>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Basic Information</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Entity Type Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter a name for this entity type"
              required
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
              rows="3"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe this entity type"
            />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Dimensions</h2>
            <button
              type="button"
              className="bg-green-600 hover:bg-green-700 text-white font-medium py-1 px-3 rounded text-sm"
              onClick={handleAddDimension}
            >
              Add Dimension
            </button>
          </div>
          
          <div className="mb-4">
            <p className="text-gray-600 text-sm">
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
        
        <div className="flex justify-end">
          <button
            type="button"
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded mr-2"
            onClick={() => navigate('/entity-types')}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded"
            disabled={saving}
          >
            {saving ? 'Creating...' : 'Create Entity Type'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default EntityTypeCreate; 