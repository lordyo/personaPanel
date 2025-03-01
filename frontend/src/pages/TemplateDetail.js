import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { templateApi } from '../services/api';
import DimensionForm from '../components/DimensionForm';

/**
 * Page component for viewing and customizing an entity template.
 * 
 * @returns {JSX.Element} - Rendered component
 */
const TemplateDetail = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();
  
  const [template, setTemplate] = useState(null);
  const [customName, setCustomName] = useState('');
  const [customDescription, setCustomDescription] = useState('');
  const [dimensions, setDimensions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  
  useEffect(() => {
    const fetchTemplate = async () => {
      setLoading(true);
      try {
        const response = await templateApi.getById(templateId);
        if (response.status === 'success') {
          setTemplate(response.data);
          setCustomName(response.data.name);
          setCustomDescription(response.data.description);
          setDimensions(response.data.dimensions);
        } else {
          setError(response.message || 'Failed to load template');
        }
      } catch (err) {
        setError('Error loading template. Please try again.');
        console.error('Error fetching template:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchTemplate();
  }, [templateId]);
  
  const handleUpdateDimension = (index, updatedDimension) => {
    const newDimensions = [...dimensions];
    newDimensions[index] = updatedDimension;
    setDimensions(newDimensions);
  };
  
  const handleRemoveDimension = (index) => {
    setDimensions(dimensions.filter((_, i) => i !== index));
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
  
  const handleCreateEntityType = async () => {
    if (!customName) {
      setError('Entity type name is required');
      return;
    }
    
    setSaving(true);
    try {
      const response = await templateApi.createEntityType(templateId, {
        name: customName,
        description: customDescription,
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
  
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <p>Loading template...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <p>{error}</p>
        </div>
        <button
          className="text-blue-600 hover:text-blue-800"
          onClick={() => navigate('/entity-types')}
        >
          &larr; Back to Entity Types
        </button>
      </div>
    );
  }
  
  if (!template) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <p>Template not found</p>
        <button
          className="text-blue-600 hover:text-blue-800 mt-4"
          onClick={() => navigate('/entity-types')}
        >
          &larr; Back to Entity Types
        </button>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center mb-6">
        <button
          className="text-blue-600 hover:text-blue-800 mr-4"
          onClick={() => navigate('/entity-types')}
        >
          &larr; Back
        </button>
        <h1 className="text-2xl font-bold">Customize Template: {template.name}</h1>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <p>{error}</p>
        </div>
      )}
      
      <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-6">
        <p className="text-blue-800">
          You're creating a new entity type based on the {template.name} template. 
          Customize the properties below to suit your needs.
        </p>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Basic Information</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Entity Type Name
          </label>
          <input
            type="text"
            className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
            value={customName}
            onChange={(e) => setCustomName(e.target.value)}
            placeholder="Enter a name for this entity type"
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            className="w-full border border-gray-300 rounded-md shadow-sm py-2 px-3"
            rows="3"
            value={customDescription}
            onChange={(e) => setCustomDescription(e.target.value)}
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
        
        {dimensions.length === 0 ? (
          <p className="text-gray-500 italic">No dimensions defined for this entity type.</p>
        ) : (
          <div>
            {dimensions.map((dimension, index) => (
              <DimensionForm
                key={index}
                dimension={dimension}
                onChange={(updatedDimension) => handleUpdateDimension(index, updatedDimension)}
                onRemove={() => handleRemoveDimension(index)}
              />
            ))}
          </div>
        )}
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
          type="button"
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded"
          onClick={handleCreateEntityType}
          disabled={saving}
        >
          {saving ? 'Creating...' : 'Create Entity Type'}
        </button>
      </div>
    </div>
  );
};

export default TemplateDetail; 