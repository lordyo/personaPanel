import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { entityTypeApi } from '../services/api';
import LoadingIndicator from '../components/LoadingIndicator';
import DimensionForm from '../components/DimensionForm';

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

  useEffect(() => {
    const fetchEntityType = async () => {
      try {
        const response = await entityTypeApi.getById(id);
        if (response && response.status === 'success') {
          const entityType = response.data;
          setName(entityType.name);
          setDescription(entityType.description || '');
          
          // Convert legacy 'numerical' types to 'float' to ensure backward compatibility
          const updatedDimensions = (entityType.dimensions || []).map(dim => {
            if (dim.type === 'numerical') {
              return {
                ...dim,
                type: 'float',
                distribution: dim.distribution || 'normal',
                min_value: dim.min_value !== undefined ? dim.min_value : 0,
                max_value: dim.max_value !== undefined ? dim.max_value : 100,
                std_deviation: dim.std_deviation || (dim.max_value - dim.min_value) / 6
              };
            }
            // Add default true_percentage for boolean types
            if (dim.type === 'boolean' && dim.true_percentage === undefined) {
              return {
                ...dim,
                true_percentage: 0.5
              };
            }
            return dim;
          });
          
          setDimensions(updatedDimensions);
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
    
    // Process form data before validation
    const processedDimensions = [...dimensions];
    
    // Validate dimensions
    const dimensionErrors = [];
    processedDimensions.forEach((dimension, idx) => {
      if (!dimension.name.trim()) {
        dimensionErrors.push(`Dimension ${idx + 1} needs a name`);
        isValid = false;
      }
      
      // Debug for categorical options
      if (dimension.type === 'categorical') {
        console.log(`Validating categorical dimension "${dimension.name}":`);
        console.log("Options:", dimension.options);
        console.log("Distribution values:", dimension.distribution_values);
        
        // Ensure options and distribution_values are in sync
        if (dimension.distribution_values && Object.keys(dimension.distribution_values).length > 0) {
          // Get all keys from distribution_values
          const distributionKeys = Object.keys(dimension.distribution_values);
          
          // If options is empty or missing, use the keys from distribution_values
          if (!dimension.options || dimension.options.length === 0) {
            console.log("Fixing missing options array from distribution_values");
            dimension.options = [...distributionKeys];
          }
          // If options has different entries than distribution_values, merge them
          else if (JSON.stringify(dimension.options.sort()) !== JSON.stringify(distributionKeys.sort())) {
            console.log("Synchronizing options with distribution_values");
            
            // Add any missing options to distribution_values
            const missingInDistribution = dimension.options.filter(opt => !distributionKeys.includes(opt));
            missingInDistribution.forEach(opt => {
              dimension.distribution_values[opt] = 0;  // Initialize with 0
            });
            
            // Add any missing distribution keys to options
            const missingInOptions = distributionKeys.filter(key => !dimension.options.includes(key));
            if (missingInOptions.length > 0) {
              dimension.options = [...dimension.options, ...missingInOptions];
            }
            
            // Normalize the distribution values
            const total = Object.values(dimension.distribution_values).reduce((sum, val) => sum + val, 0);
            if (total > 0 && Math.abs(total - 1) > 0.01) {
              Object.keys(dimension.distribution_values).forEach(key => {
                dimension.distribution_values[key] /= total;
              });
            }
          }
        }
        // If we have options but no distribution_values, create them
        else if (dimension.options && dimension.options.length > 0 && 
                (!dimension.distribution_values || Object.keys(dimension.distribution_values).length === 0)) {
          console.log("Creating distribution_values from options");
          const equalShare = 1 / dimension.options.length;
          dimension.distribution_values = {};
          dimension.options.forEach(option => {
            dimension.distribution_values[option] = equalShare;
          });
        }
      }
      
      if (dimension.type === 'categorical' && (!dimension.options || !Array.isArray(dimension.options) || dimension.options.length === 0)) {
        dimensionErrors.push(`Dimension "${dimension.name || idx + 1}" needs at least one option`);
        console.error(`Dimension "${dimension.name}" missing options:`, dimension.options);
        isValid = false;
      }

      if (dimension.type === 'int' || dimension.type === 'float') {
        if (dimension.min_value === undefined || dimension.max_value === undefined) {
          dimensionErrors.push(`Dimension "${dimension.name || idx + 1}" needs min and max values`);
          isValid = false;
        }
        
        if (dimension.min_value >= dimension.max_value) {
          dimensionErrors.push(`Dimension "${dimension.name || idx + 1}" min value must be less than max value`);
          isValid = false;
        }
        
        if (dimension.distribution === 'normal') {
          // Check for either spread_factor (new) or std_deviation (legacy)
          if (dimension.spread_factor !== undefined) {
            if (dimension.spread_factor <= 0 || dimension.spread_factor > 1) {
              dimensionErrors.push(`Dimension "${dimension.name || idx + 1}" spread factor must be between 0 and 1`);
              isValid = false;
            }
          } else if (dimension.std_deviation !== undefined) {
            if (dimension.std_deviation <= 0) {
              dimensionErrors.push(`Dimension "${dimension.name || idx + 1}" needs a positive standard deviation for normal distribution`);
              isValid = false;
            }
          } else {
            dimensionErrors.push(`Dimension "${dimension.name || idx + 1}" needs a spread factor for normal distribution`);
            isValid = false;
          }
        }
      }
      
      // Legacy numerical type validation
      if (dimension.type === 'numerical') {
        if (dimension.min_value === undefined || dimension.max_value === undefined) {
          dimensionErrors.push(`Dimension "${dimension.name || idx + 1}" needs min and max values`);
          isValid = false;
        }
        
        if (dimension.min_value >= dimension.max_value) {
          dimensionErrors.push(`Dimension "${dimension.name || idx + 1}" min value must be less than max value`);
          isValid = false;
        }
      }
      
      if (dimension.type === 'boolean' && dimension.true_percentage !== undefined) {
        if (dimension.true_percentage < 0 || dimension.true_percentage > 1) {
          dimensionErrors.push(`Dimension "${dimension.name || idx + 1}" true percentage must be between 0 and 1`);
          isValid = false;
        }
      }
      
      if (dimension.type === 'categorical' && dimension.distribution_values) {
        // Check if all options have distribution values
        const allOptionsHaveValues = dimension.options.every(option => 
          dimension.distribution_values && dimension.distribution_values[option] !== undefined
        );
        
        if (!allOptionsHaveValues) {
          // Auto-fill missing values with equal distribution
          const totalOptions = dimension.options.length;
          const equalShare = 1 / totalOptions;
          const updatedValues = { ...dimension.distribution_values };
          
          dimension.options.forEach(option => {
            if (!updatedValues[option]) {
              updatedValues[option] = equalShare;
            }
          });
          
          dimension.distribution_values = updatedValues;
        }
        
        // Normalize values to ensure they sum to 1
        const totalPercentage = Object.values(dimension.distribution_values).reduce((sum, val) => sum + val, 0);
        if (Math.abs(totalPercentage - 1) > 0.01) {
          const normalizedValues = {};
          Object.keys(dimension.distribution_values).forEach(key => {
            normalizedValues[key] = dimension.distribution_values[key] / totalPercentage;
          });
          dimension.distribution_values = normalizedValues;
        }
      }
    });
    
    if (dimensionErrors.length > 0) {
      setDimensionsError(dimensionErrors.join('; '));
    } else {
      setDimensionsError('');
    }
    
    // Update the dimensions state with the processed data
    setDimensions(processedDimensions);
    
    return isValid;
  };

  const handleSave = async () => {
    // Blur any active elements to trigger onBlur handlers
    if (document.activeElement instanceof HTMLElement) {
      document.activeElement.blur();
    }
    
    // Small delay to ensure blur handlers have completed
    setTimeout(async () => {
      if (!validateForm()) {
        return;
      }
      
      setSaving(true);
      setSuccess(false);
      
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
          prepared.std_deviation = d.std_deviation; // For legacy support
        } else if (d.type === 'boolean') {
          prepared.true_percentage = d.true_percentage;
        }
        
        return prepared;
      });
      
      try {
        const entityTypeData = {
          name,
          description,
          dimensions: preparedDimensions
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
    }, 100);
  };

  const handleAddDimension = () => {
    setDimensions([
      ...dimensions, 
      { 
        name: '', 
        type: '', 
        description: ''
      }
    ]);
  };

  const handleRemoveDimension = (index) => {
    setDimensions(dimensions.filter((_, i) => i !== index));
  };

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
                  <DimensionForm
                    key={index}
                    dimension={dimension}
                    onChange={(updatedDimension) => handleUpdateDimension(index, updatedDimension)}
                    onRemove={() => handleRemoveDimension(index)}
                  />
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