import React, { useState, useEffect } from 'react';

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
  // State to track raw options input for categorical dimensions
  const [rawOptionsInput, setRawOptionsInput] = useState(
    dimension.type === 'categorical' ? (dimension.options || []).join(', ') : ''
  );

  // State to track categorical distribution percentages
  const [categoryPercentages, setCategoryPercentages] = useState({});

  // Update raw options input when dimension.options changes externally
  useEffect(() => {
    if (dimension.type === 'categorical') {
      // Only update rawOptionsInput if it's empty - this allows user to type freely
      if (rawOptionsInput === '') {
        const optionsString = (dimension.options || []).join(', ');
        setRawOptionsInput(optionsString);
      }
      
      // Initialize percentages with equal distribution if not set
      if (dimension.options && dimension.options.length > 0 && 
          (!dimension.distribution_values || 
          Object.keys(dimension.distribution_values).length !== dimension.options.length)) {
        const equalShare = 1 / dimension.options.length;
        const newPercentages = {};
        dimension.options.forEach(option => {
          newPercentages[option] = equalShare;
        });
        setCategoryPercentages(newPercentages);
        handleFieldChange('distribution_values', {...newPercentages});
      } else if (dimension.distribution_values) {
        setCategoryPercentages(dimension.distribution_values);
      }
    }
  // Only depend on dimension.type to avoid unwanted re-renders
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dimension.type]);

  const handleFieldChange = (field, value) => {
    onChange({ ...dimension, [field]: value });
  };

  // Handle change in dimension type
  const handleTypeChange = (type) => {
    // Create new dimension with the appropriate default values based on type
    const newDimension = {
      ...dimension,
      type,
    };
    
    // Set appropriate default values based on type
    if (type === 'boolean') {
      newDimension.distribution = 'percentage';
      newDimension.true_percentage = 0.5;
    } else if (type === 'int' || type === 'float') {
      newDimension.distribution = 'normal';
      newDimension.spread_factor = 0.5; // Default to medium spread instead of std_deviation
      newDimension.skew_factor = 0;
    } else if (type === 'categorical') {
      // Initialize with empty arrays and objects
      newDimension.options = []; // Ensure it's an empty array, not undefined
      newDimension.distribution_values = {};
      setRawOptionsInput('');
      // Reset the category percentages
      setCategoryPercentages({});
      
      console.log("Initialized categorical dimension:", newDimension);
    }
    
    onChange(newDimension);
  };

  // Helper function to parse options and update dimension
  const parseAndUpdateOptions = (inputText) => {
    // Process options - split by comma and clean up
    const options = inputText.split(',')
      .map(item => item.trim())
      .filter(item => item.length > 0);
    
    console.log("Final parsed options:", options);
    
    // First check if we already have distribution_values to incorporate
    const existingDistributionValues = dimension.distribution_values || {};
    
    // Start with existing percentages where possible
    const newPercentages = {...existingDistributionValues};
    
    // Add missing options with equal share of remaining percentage
    const missingOptions = options.filter(opt => !newPercentages[opt]);
    if (missingOptions.length > 0) {
      const existingTotal = Object.values(newPercentages).reduce((sum, val) => sum + val, 0);
      const remainingShare = Math.max(0, 1 - existingTotal);
      const sharePerMissing = missingOptions.length > 0 ? remainingShare / missingOptions.length : 0;
      
      missingOptions.forEach(option => {
        newPercentages[option] = sharePerMissing;
      });
    }
    
    // Remove percentages for options that no longer exist
    Object.keys(newPercentages).forEach(key => {
      if (!options.includes(key)) {
        delete newPercentages[key];
      }
    });
    
    // Normalize if needed
    const total = Object.values(newPercentages).reduce((sum, val) => sum + val, 0);
    if (Math.abs(total - 1) > 0.01 && total > 0) {
      Object.keys(newPercentages).forEach(key => {
        newPercentages[key] = newPercentages[key] / total;
      });
    }
    
    // IMPORTANT: Update both the options array and distribution_values at the same time
    // This ensures they stay in sync
    const updatedDimension = {
      ...dimension,
      options: [...options],
      distribution_values: {...newPercentages}
    };
    
    setCategoryPercentages(newPercentages);
    onChange(updatedDimension);  // Use onChange instead of handleFieldChange to update the whole dimension
  };

  // Handle change in categorical option percentages
  const handleCategoryPercentageChange = (option, value) => {
    const numericValue = parseFloat(value);
    if (isNaN(numericValue)) return;
    
    // Update percentages for this option
    const newPercentages = { ...categoryPercentages, [option]: numericValue };
    setCategoryPercentages(newPercentages);
    
    // Calculate total to check if we need to normalize
    const total = Object.values(newPercentages).reduce((sum, val) => sum + val, 0);
    
    // If total is significantly different from 1, normalize values
    if (Math.abs(total - 1) > 0.001) {
      const normalizedPercentages = {};
      Object.keys(newPercentages).forEach(key => {
        normalizedPercentages[key] = newPercentages[key] / total;
      });
      setCategoryPercentages(normalizedPercentages);
      
      // Make sure options array matches distribution_values keys
      const updatedDimension = {
        ...dimension,
        distribution_values: normalizedPercentages,
        options: Object.keys(normalizedPercentages)
      };
      onChange(updatedDimension);
    } else {
      // Make sure options array matches distribution_values keys
      const updatedDimension = {
        ...dimension,
        distribution_values: newPercentages,
        options: Object.keys(newPercentages)
      };
      onChange(updatedDimension);
    }
  };

  // Render different controls based on dimension type
  const renderTypeSpecificControls = () => {
    switch (dimension.type) {
      case 'boolean':
        return (
          <div className="mt-2">
            <label className="block text-sm font-medium text-gray-400">True Percentage</label>
            <div className="flex items-center mt-1">
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={dimension.true_percentage || 0.5}
                onChange={(e) => handleFieldChange('true_percentage', parseFloat(e.target.value))}
                className="w-2/3 mr-3"
              />
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={dimension.true_percentage || 0.5}
                onChange={(e) => handleFieldChange('true_percentage', parseFloat(e.target.value))}
                className="w-1/3 bg-gray-750 border border-gray-700 rounded-md shadow-sm py-1 px-2 text-gray-300 focus:outline-none focus:border-blue-500"
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Percentage chance of generating 'true' (default: 0.5 or 50%)
            </p>
          </div>
        );
      
      case 'categorical':
        return (
          <>
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-400">Options (separate with commas)</label>
              <textarea
                className="mt-1 block w-full bg-gray-750 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
                rows="3"
                value={rawOptionsInput}
                onChange={(e) => {
                  // Just update the raw input on keystroke without parsing
                  setRawOptionsInput(e.target.value);
                }}
                onKeyDown={(e) => {
                  // Also parse on Enter key (but don't submit the form)
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    parseAndUpdateOptions(e.target.value);
                  }
                }}
                onBlur={(e) => {
                  // Only parse and update options when the user has finished typing (on blur)
                  parseAndUpdateOptions(e.target.value);
                }}
                placeholder="Enter options separated by commas (e.g. Red, Green, Blue) and press Tab or click elsewhere when done"
              />
            </div>
            
            {(dimension.options || []).length > 0 && (
              <div className="mt-3">
                <label className="block text-sm font-medium text-gray-400 mb-2">Distribution Percentages</label>
                <div className="space-y-2 max-h-48 overflow-y-auto p-2 bg-gray-800 rounded-md">
                  {(dimension.options || []).map((option) => (
                    <div key={option} className="flex items-center">
                      <span className="w-1/3 text-sm text-gray-300">{option}:</span>
                      <input
                        type="range"
                        min="0.01"
                        max="1"
                        step="0.01"
                        value={categoryPercentages[option] || 0}
                        onChange={(e) => handleCategoryPercentageChange(option, e.target.value)}
                        className="w-1/3 mx-2"
                      />
                      <input
                        type="number"
                        min="0"
                        max="1"
                        step="0.01"
                        value={categoryPercentages[option] ? Math.round(categoryPercentages[option] * 100) / 100 : 0}
                        onChange={(e) => handleCategoryPercentageChange(option, e.target.value)}
                        className="w-1/4 bg-gray-750 border border-gray-700 rounded-md shadow-sm py-1 px-2 text-gray-300 focus:outline-none focus:border-blue-500"
                      />
                    </div>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Values are automatically normalized to sum to 1.0
                </p>
              </div>
            )}
          </>
        );
      
      case 'int':
      case 'float':
        return (
          <>
            <div className="grid grid-cols-2 gap-4 mt-2">
              <div>
                <label className="block text-sm font-medium text-gray-400">Min Value</label>
                <input
                  type={dimension.type === 'int' ? 'number' : 'number'}
                  step={dimension.type === 'int' ? "1" : "0.01"}
                  className="mt-1 block w-full bg-gray-750 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
                  value={dimension.min_value || ''}
                  onChange={(e) => handleFieldChange('min_value', dimension.type === 'int' ? parseInt(e.target.value) : parseFloat(e.target.value))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400">Max Value</label>
                <input
                  type={dimension.type === 'int' ? 'number' : 'number'}
                  step={dimension.type === 'int' ? "1" : "0.01"}
                  className="mt-1 block w-full bg-gray-750 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
                  value={dimension.max_value || ''}
                  onChange={(e) => handleFieldChange('max_value', dimension.type === 'int' ? parseInt(e.target.value) : parseFloat(e.target.value))}
                />
              </div>
            </div>
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-400">Distribution</label>
              <select
                className="mt-1 block w-full bg-gray-750 border border-gray-700 rounded-md shadow-sm py-2 px-3 text-gray-300 focus:outline-none focus:border-blue-500"
                value={dimension.distribution || 'normal'}
                onChange={(e) => handleFieldChange('distribution', e.target.value)}
              >
                <option value="uniform">Uniform</option>
                <option value="normal">Normal</option>
                <option value="skewed">Skewed</option>
              </select>
            </div>
            
            {dimension.distribution === 'normal' && (
              <div className="mt-2">
                <label className="block text-sm font-medium text-gray-400">Distribution Spread</label>
                <div className="flex items-center mt-1">
                  <input
                    type="range"
                    min="0.01"
                    max="1"
                    step="0.01"
                    value={dimension.spread_factor || 0.5}
                    onChange={(e) => handleFieldChange('spread_factor', parseFloat(e.target.value))}
                    className="w-2/3 mr-3"
                  />
                  <div className="w-1/3 text-sm text-gray-300">
                    {dimension.spread_factor < 0.3 ? "Concentrated" : 
                     dimension.spread_factor < 0.7 ? "Moderate" : "Spread out"}
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Controls how spread out values will be from the center
                </p>
              </div>
            )}
            
            {dimension.distribution === 'skewed' && (
              <div className="mt-2">
                <label className="block text-sm font-medium text-gray-400">Skew Factor</label>
                <div className="flex items-center mt-1">
                  <input
                    type="range"
                    min="-5"
                    max="5"
                    step="0.1"
                    value={dimension.skew_factor || 0}
                    onChange={(e) => handleFieldChange('skew_factor', parseFloat(e.target.value))}
                    className="w-2/3 mr-3"
                  />
                  <input
                    type="number"
                    min="-5"
                    max="5"
                    step="0.1"
                    value={dimension.skew_factor || 0}
                    onChange={(e) => handleFieldChange('skew_factor', parseFloat(e.target.value))}
                    className="w-1/3 bg-gray-750 border border-gray-700 rounded-md shadow-sm py-1 px-2 text-gray-300 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Negative values skew left, positive values skew right
                </p>
              </div>
            )}
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
          onChange={(e) => handleTypeChange(e.target.value)}
        >
          <option value="">Select a type</option>
          <option value="boolean">Boolean</option>
          <option value="categorical">Categorical</option>
          <option value="int">Integer</option>
          <option value="float">Float</option>
          <option value="text">Text</option>
        </select>
      </div>
      
      {renderTypeSpecificControls()}
    </div>
  );
};

export default DimensionForm; 