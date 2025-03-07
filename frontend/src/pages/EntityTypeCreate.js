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
  const [suggesting, setSuggesting] = useState(false);
  
  const handleUpdateDimension = (index, updatedDimension) => {
    // Create a deep copy to prevent reference issues
    const newDimensions = dimensions.map((dim, i) => {
      if (i === index) {
        // Ensure we're keeping all properties, especially distribution_values for categorical dimensions
        return {
          ...dim,
          ...updatedDimension
        };
      }
      return dim;
    });
    
    // Set dimensions with the updated array
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
  
  const handleSuggestDimensions = async () => {
    // Clear any previous errors
    setError(null);
    
    // Validate that we have a name
    if (!name.trim()) {
      setError('Please enter an entity type name before suggesting dimensions');
      return;
    }
    
    try {
      // Set suggesting state to true to show loading indicator
      setSuggesting(true);
      
      // Call the API to suggest dimensions
      const response = await entityTypeApi.suggestDimensions(name, description);
      
      // Check if the response was successful
      if (response.status === 'success' && response.data && response.data.dimensions) {
        // Replace existing dimensions with suggested ones
        setDimensions(response.data.dimensions);
      } else {
        // Handle error in the response
        setError(response.message || 'Failed to suggest dimensions. Please try again.');
      }
    } catch (error) {
      console.error('Error suggesting dimensions:', error);
      setError('An error occurred while suggesting dimensions. Please try again.');
    } finally {
      // Set suggesting state back to false
      setSuggesting(false);
    }
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
    
    // Process form data before validation
    const processedDimensions = [...dimensions];
    
    for (let i = 0; i < processedDimensions.length; i++) {
      const dim = processedDimensions[i];
      if (!dim.name || !dim.type) {
        setError(`Dimension ${i + 1} is missing required fields`);
        return false;
      }
      
      // Debug for categorical options
      if (dim.type === 'categorical') {
        console.log(`Validating categorical dimension "${dim.name}":`);
        console.log("Options:", dim.options);
        console.log("Distribution values:", dim.distribution_values);
        
        // Ensure options and distribution_values are in sync
        if (dim.distribution_values && Object.keys(dim.distribution_values).length > 0) {
          // Get all keys from distribution_values
          const distributionKeys = Object.keys(dim.distribution_values);
          
          // If options is empty or missing, use the keys from distribution_values
          if (!dim.options || dim.options.length === 0) {
            console.log("Fixing missing options array from distribution_values");
            dim.options = [...distributionKeys];
          }
          // If options has different entries than distribution_values, merge them
          else if (JSON.stringify(dim.options.sort()) !== JSON.stringify(distributionKeys.sort())) {
            console.log("Synchronizing options with distribution_values");
            
            // Add any missing options to distribution_values
            const missingInDistribution = dim.options.filter(opt => !distributionKeys.includes(opt));
            missingInDistribution.forEach(opt => {
              dim.distribution_values[opt] = 0;  // Initialize with 0
            });
            
            // Add any missing distribution keys to options
            const missingInOptions = distributionKeys.filter(key => !dim.options.includes(key));
            if (missingInOptions.length > 0) {
              dim.options = [...dim.options, ...missingInOptions];
            }
            
            // Normalize the distribution values
            const total = Object.values(dim.distribution_values).reduce((sum, val) => sum + val, 0);
            if (total > 0 && Math.abs(total - 1) > 0.01) {
              Object.keys(dim.distribution_values).forEach(key => {
                dim.distribution_values[key] /= total;
              });
            }
          }
        }
        // If we have options but no distribution_values, create them
        else if (dim.options && dim.options.length > 0 && 
                (!dim.distribution_values || Object.keys(dim.distribution_values).length === 0)) {
          console.log("Creating distribution_values from options");
          const equalShare = 1 / dim.options.length;
          dim.distribution_values = {};
          dim.options.forEach(option => {
            dim.distribution_values[option] = equalShare;
          });
        }
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
      
      if (dim.type === 'categorical' && (!dim.options || !Array.isArray(dim.options) || dim.options.length === 0)) {
        setError(`Dimension "${dim.name}" needs at least one option`);
        console.error(`Dimension "${dim.name}" missing options:`, dim.options);
        return false;
      }
    }
    
    // Update the dimensions state with the processed data
    setDimensions(processedDimensions);
    
    return true;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Blur any active elements to trigger onBlur handlers
    if (document.activeElement instanceof HTMLElement) {
      document.activeElement.blur();
    }
    
    // Small delay to ensure blur handlers have completed
    setTimeout(async () => {
      if (!validateForm()) {
        return;
      }
      
      // Add debug logging to see what we're submitting
      console.log("Submitting dimensions:", dimensions);
      
      // Prepare dimensions with all needed properties
      const preparedDimensions = dimensions.map(d => {
        const prepared = {
          name: d.name,
          description: d.description,
          type: d.type,
        };
        
        // Add type-specific properties
        if (d.type === 'categorical') {
          prepared.options = Array.isArray(d.options) ? [...d.options] : [];
          prepared.distribution_values = d.distribution_values ? {...d.distribution_values} : {};
        } else if (d.type === 'int' || d.type === 'float') {
          prepared.min_value = d.min_value;
          prepared.max_value = d.max_value;
          prepared.distribution = d.distribution;
          prepared.spread_factor = d.spread_factor;
          prepared.skew_factor = d.skew_factor;
        } else if (d.type === 'boolean') {
          prepared.true_percentage = d.true_percentage;
        }
        
        return prepared;
      });
      
      setSaving(true);
      try {
        const response = await entityTypeApi.create({
          name,
          description,
          dimensions: preparedDimensions
        });
        
        if (response.status === 'success') {
          navigate('/entity-types');
        } else {
          setError(response.message || 'Failed to create entity type');
          console.error("API error response:", response);
        }
      } catch (err) {
        setError('Error creating entity type. Please try again.');
        console.error('Error creating entity type:', err);
      } finally {
        setSaving(false);
      }
    }, 100);
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
          
          <div className="flex justify-end">
            <button
              type="button"
              className={`flex items-center px-4 py-2 rounded ${
                suggesting ? 'bg-blue-700 opacity-75 cursor-wait' : 'bg-blue-600 hover:bg-blue-700'
              } text-white transition`}
              onClick={handleSuggestDimensions}
              disabled={suggesting}
            >
              {suggesting ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating...
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                  </svg>
                  Suggest Dimensions with AI
                </>
              )}
            </button>
          </div>
          <div className="mt-2 text-sm text-gray-500 italic">
            Click "Suggest Dimensions" to use AI to automatically generate relevant dimensions based on the entity type name and description you provided. This will replace any existing dimensions.
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