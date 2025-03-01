import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { entityTypeApi } from '../services/api';
import LoadingIndicator from '../components/LoadingIndicator';

/**
 * Page component for editing an existing entity type.
 * 
 * @returns {JSX.Element} - Rendered component
 */
const EntityTypeEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [dimensions, setDimensions] = useState([]);
  
  // Form validation
  const [nameError, setNameError] = useState('');
  const [dimensionsError, setDimensionsError] = useState('');

  // Store raw option input for categorical dimensions
  const [rawOptions, setRawOptions] = useState({});

  useEffect(() => {
    const fetchEntityType = async () => {
      try {
        const response = await entityTypeApi.getById(id);
        if (response && response.status === 'success') {
          const entityType = response.data;
          setName(entityType.name);
          setDescription(entityType.description || '');
          setDimensions(entityType.dimensions || []);
          setError(null);
        } else {
          console.error('Error fetching entity type:', response?.message || 'Unknown error');
          setError(`Failed to load entity type: ${response?.message || 'Unknown error'}`);
        }
      } catch (err) {
        console.error('Error fetching entity type:', err);
        setError('Failed to load entity type. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchEntityType();
  }, [id]);

  const handleBack = () => {
    navigate(`/entity-types/${id}`);
  };

  const validateForm = () => {
    let isValid = true;
    
    // Validate name
    if (!name.trim()) {
      setNameError('Name is required');
      isValid = false;
    } else {
      setNameError('');
    }
    
    // Validate dimensions
    const dimensionErrors = [];
    dimensions.forEach((dimension, idx) => {
      if (!dimension.name.trim()) {
        dimensionErrors.push(`Dimension ${idx + 1} needs a name`);
        isValid = false;
      }
      
      if (dimension.type === 'categorical' && (!dimension.options || dimension.options.length === 0)) {
        dimensionErrors.push(`Dimension "${dimension.name || idx + 1}" needs at least one option`);
        isValid = false;
      }
    });
    
    if (dimensionErrors.length > 0) {
      setDimensionsError(dimensionErrors.join('; '));
    } else {
      setDimensionsError('');
    }
    
    return isValid;
  };

  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }
    
    setSaving(true);
    setSuccess(false);
    
    try {
      const entityTypeData = {
        name,
        description,
        dimensions
      };
      
      const response = await entityTypeApi.update(id, entityTypeData);
      
      if (response && response.status === 'success') {
        setSuccess(true);
        setError(null);
        
        // Reset validation errors
        setNameError('');
        setDimensionsError('');
        
        setTimeout(() => {
          navigate(`/entity-types/${id}`);
        }, 1500);
      } else {
        console.error('Error updating entity type:', response?.message || 'Unknown error');
        setError(`Failed to update entity type: ${response?.message || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error updating entity type:', err);
      setError('Failed to update entity type. Please try again later.');
    } finally {
      setSaving(false);
    }
  };

  const handleAddDimension = () => {
    setDimensions([
      ...dimensions, 
      { 
        name: '', 
        type: 'categorical', 
        description: '',
        options: []
      }
    ]);
  };

  const handleRemoveDimension = (index) => {
    setDimensions(dimensions.filter((_, i) => i !== index));
  };

  const handleDimensionChange = (index, field, value) => {
    const newDimensions = [...dimensions];
    newDimensions[index] = {
      ...newDimensions[index],
      [field]: value
    };
    setDimensions(newDimensions);
  };

  // Helper function to handle categorical options input
  const handleOptionsChange = (index, value) => {
    // Update raw options state
    setRawOptions({
      ...rawOptions,
      [index]: value
    });
    
    // Process the options and update dimension
    const options = value.split(',').map(item => item.trim()).filter(Boolean);
    handleDimensionChange(index, 'options', options);
  };

  if (loading) {
    return <LoadingIndicator message="Loading entity type..." fullPage />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <button 
          onClick={handleBack}
          className="flex items-center text-blue-400 hover:text-blue-300"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
          </svg>
          Back to Details
        </button>
        
        <button 
          onClick={handleSave}
          disabled={saving}
          className={`flex items-center px-4 py-2 rounded font-medium ${
            saving 
              ? 'bg-blue-400 cursor-not-allowed' 
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          {saving ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Saving...
            </>
          ) : 'Save Changes'}
        </button>
      </div>
      
      {error && (
        <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
          {error}
        </div>
      )}
      
      {success && (
        <div className="mb-6 p-4 bg-green-400 bg-opacity-10 border border-green-400 rounded-lg text-green-400">
          Entity type updated successfully!
        </div>
      )}
      
      <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 overflow-hidden">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-blue-300 mb-6">Edit Entity Type</h1>
          
          <div className="mb-6">
            <label className="block text-gray-400 text-sm font-medium mb-2" htmlFor="name">
              Name *
            </label>
            <input 
              id="name" 
              type="text" 
              value={name}
              onChange={(e) => setName(e.target.value)}
              className={`w-full bg-gray-750 border ${nameError ? 'border-red-400' : 'border-gray-700'} rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500`}
              placeholder="Entity Type Name"
            />
            {nameError && <p className="mt-1 text-red-400 text-sm">{nameError}</p>}
          </div>
          
          <div className="mb-8">
            <label className="block text-gray-400 text-sm font-medium mb-2" htmlFor="description">
              Description
            </label>
            <textarea 
              id="description" 
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-gray-750 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
              rows="3"
              placeholder="Optional description"
            />
          </div>
          
          <div className="border-t border-gray-700 pt-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-blue-300">Dimensions</h2>
              <button 
                onClick={handleAddDimension}
                className="flex items-center px-3 py-1 text-sm rounded border border-blue-400 text-blue-400 hover:bg-blue-400 hover:bg-opacity-10"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Add Dimension
              </button>
            </div>
            
            {dimensionsError && (
              <div className="mb-4 p-3 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400 text-sm">
                {dimensionsError}
              </div>
            )}
            
            {dimensions.length === 0 ? (
              <p className="text-gray-400 italic mb-4">No dimensions defined yet. Add a dimension to get started.</p>
            ) : (
              <div className="space-y-6">
                {dimensions.map((dimension, index) => (
                  <div key={index} className="bg-gray-750 rounded-lg p-5 border border-gray-700">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-medium text-blue-300">Dimension {index + 1}</h3>
                      <button 
                        onClick={() => handleRemoveDimension(index)}
                        className="p-1 rounded text-red-400 hover:bg-red-400 hover:bg-opacity-10"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-gray-400 text-sm font-medium mb-2">
                          Name *
                        </label>
                        <input 
                          type="text" 
                          value={dimension.name}
                          onChange={(e) => handleDimensionChange(index, 'name', e.target.value)}
                          className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
                          placeholder="Dimension Name"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-gray-400 text-sm font-medium mb-2">
                          Type *
                        </label>
                        <select 
                          value={dimension.type}
                          onChange={(e) => handleDimensionChange(index, 'type', e.target.value)}
                          className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
                        >
                          <option value="categorical">Categorical</option>
                          <option value="numerical">Numerical</option>
                          <option value="boolean">Boolean</option>
                          <option value="text">Text</option>
                        </select>
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <label className="block text-gray-400 text-sm font-medium mb-2">
                        Description
                      </label>
                      <input 
                        type="text" 
                        value={dimension.description || ''}
                        onChange={(e) => handleDimensionChange(index, 'description', e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
                        placeholder="Optional description"
                      />
                    </div>
                    
                    {dimension.type === 'categorical' && (
                      <div>
                        <label className="block text-gray-400 text-sm font-medium mb-2">
                          Options * (separate with commas)
                        </label>
                        <textarea 
                          value={rawOptions[index] || (dimension.options || []).join(', ')}
                          onChange={(e) => handleOptionsChange(index, e.target.value)}
                          className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
                          rows="4"
                          placeholder="Enter options separated by commas (e.g. Red, Green, Blue)"
                        />
                      </div>
                    )}
                    
                    {dimension.type === 'numerical' && (
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-gray-400 text-sm font-medium mb-2">
                            Min Value
                          </label>
                          <input 
                            type="number" 
                            value={dimension.min !== undefined ? dimension.min : ''}
                            onChange={(e) => handleDimensionChange(index, 'min', parseFloat(e.target.value))}
                            className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
                            placeholder="Minimum value"
                          />
                        </div>
                        <div>
                          <label className="block text-gray-400 text-sm font-medium mb-2">
                            Max Value
                          </label>
                          <input 
                            type="number" 
                            value={dimension.max !== undefined ? dimension.max : ''}
                            onChange={(e) => handleDimensionChange(index, 'max', parseFloat(e.target.value))}
                            className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
                            placeholder="Maximum value"
                          />
                        </div>
                      </div>
                    )}
                    
                    {dimension.type === 'boolean' && (
                      <div>
                        <label className="block text-gray-400 text-sm font-medium mb-2">
                          Default Value
                        </label>
                        <select 
                          value={dimension.defaultValue ? 'true' : 'false'}
                          onChange={(e) => handleDimensionChange(index, 'defaultValue', e.target.value === 'true')}
                          className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
                        >
                          <option value="true">True</option>
                          <option value="false">False</option>
                        </select>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
            
            {dimensions.length > 0 && (
              <div className="mt-4">
                <button 
                  onClick={handleAddDimension}
                  className="flex items-center justify-center w-full py-2 text-blue-400 hover:bg-blue-400 hover:bg-opacity-10 rounded border border-dashed border-blue-400"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add Another Dimension
                </button>
              </div>
            )}
          </div>
        </div>
        
        <div className="bg-gray-850 px-6 py-4 border-t border-gray-700 flex justify-end">
          <div className="flex space-x-3">
            <button 
              onClick={handleBack}
              className="px-4 py-2 border border-gray-600 rounded text-gray-300 hover:border-gray-500 hover:text-gray-200"
            >
              Cancel
            </button>
            <button 
              onClick={handleSave}
              disabled={saving}
              className={`px-6 py-2 rounded font-medium ${
                saving 
                  ? 'bg-blue-400 cursor-not-allowed' 
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EntityTypeEdit; 