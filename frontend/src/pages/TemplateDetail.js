import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { templateApi } from '../services/api';
import DimensionForm from '../components/DimensionForm';
import LoadingIndicator from '../components/LoadingIndicator';

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
    return <LoadingIndicator message="Loading template details..." fullPage />;
  }
  
  if (error && !template) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
          <p>{error}</p>
        </div>
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
    );
  }
  
  if (!template) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-gray-800 p-8 text-center rounded-lg border border-gray-700">
          <h2 className="text-xl font-semibold text-blue-300 mb-2">Template not found</h2>
          <p className="text-gray-400 mb-6">The requested template could not be loaded.</p>
          <button
            className="flex items-center text-blue-400 hover:text-blue-300 mx-auto"
            onClick={() => navigate('/entity-types')}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            Back to Entity Types
          </button>
        </div>
      </div>
    );
  }
  
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
      
      <h1 className="text-2xl font-bold text-blue-300 mb-6">Customize Template: {template.name}</h1>
      
      {error && (
        <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
          <p>{error}</p>
        </div>
      )}
      
      <div className="bg-blue-400 bg-opacity-10 border border-blue-400 rounded-lg p-4 mb-6 text-blue-300">
        <p>
          You're creating a new entity type based on the {template.name} template. 
          Customize the properties below to suit your needs.
        </p>
      </div>
      
      <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 p-6 mb-6">
        <h2 className="text-xl font-semibold text-blue-300 mb-4">Basic Information</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-400 mb-1">
            Entity Type Name
          </label>
          <input
            type="text"
            className="w-full bg-gray-750 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
            value={customName}
            onChange={(e) => setCustomName(e.target.value)}
            placeholder="Enter a name for this entity type"
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-400 mb-1">
            Description
          </label>
          <textarea
            className="w-full bg-gray-750 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
            rows="3"
            value={customDescription}
            onChange={(e) => setCustomDescription(e.target.value)}
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
            type="button"
            className={`px-6 py-2 rounded font-medium ${
              saving 
                ? 'bg-blue-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
            onClick={handleCreateEntityType}
            disabled={saving}
          >
            {saving ? 'Creating...' : 'Create Entity Type'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default TemplateDetail; 