import React, { useState, useEffect } from 'react';

/**
 * Component for displaying and editing entity details.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.entity - The entity to display/edit
 * @param {Object} props.entityType - The entity type data (needed for editing)
 * @param {Function} props.onClose - Function to call when the modal is closed
 * @param {Function} props.onSave - Function to call when saving changes
 * @returns {JSX.Element} - Rendered component
 */
const EntityDetail = ({ entity, entityType, onClose, onSave }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedAttributes, setEditedAttributes] = useState({});
  const [editedName, setEditedName] = useState('');
  const [editedDescription, setEditedDescription] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  
  useEffect(() => {
    if (entity) {
      // Initialize edited values with current entity values
      setEditedName(entity.name || '');
      setEditedDescription(entity.description || '');
      setEditedAttributes(entity.attributes || {});
    }
  }, [entity]);

  if (!entity) return null;

  const formatAttributeValue = (value) => {
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No';
    } else if (value === null || value === undefined) {
      return 'N/A';
    } else if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    return String(value);
  };
  
  // Organize attributes by type
  const categorizeAttributes = () => {
    if (!entity.attributes) return { textAttrs: [], otherAttrs: [] };
    
    const textAttrs = [];
    const otherAttrs = [];
    
    Object.entries(entity.attributes).forEach(([key, value]) => {
      // Skip backstory as it's redundant with description
      if (key === 'backstory') return;
      
      // If it's a string and longer than 50 characters, treat as text
      if (typeof value === 'string' && value.length > 50) {
        textAttrs.push([key, value]);
      } else {
        otherAttrs.push([key, value]);
      }
    });
    
    return { textAttrs, otherAttrs };
  };
  
  const { textAttrs, otherAttrs } = categorizeAttributes();
  
  const handleToggleEdit = () => {
    setIsEditing(!isEditing);
  };
  
  const handleAttributeChange = (key, value) => {
    setEditedAttributes(prev => ({
      ...prev,
      [key]: value
    }));
  };
  
  const handleSave = () => {
    setIsSaving(true);
    
    const updatedEntity = {
      ...entity,
      name: editedName,
      description: editedDescription,
      attributes: editedAttributes
    };
    
    onSave(updatedEntity)
      .then(() => {
        setIsEditing(false);
        setIsSaving(false);
      })
      .catch(err => {
        console.error("Error saving entity:", err);
        setIsSaving(false);
      });
  };

  // Helper to render attribute in edit mode
  const renderEditableAttribute = (key, value) => {
    const attrType = typeof value;
    
    if (attrType === 'boolean') {
      return (
        <select
          value={editedAttributes[key] ? "true" : "false"}
          onChange={(e) => handleAttributeChange(key, e.target.value === "true")}
          className="w-full bg-gray-750 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
        >
          <option value="true">Yes</option>
          <option value="false">No</option>
        </select>
      );
    } else if (attrType === 'number') {
      return (
        <input
          type="number"
          value={editedAttributes[key]}
          onChange={(e) => handleAttributeChange(key, parseFloat(e.target.value))}
          className="w-full bg-gray-750 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
        />
      );
    } else if (attrType === 'string' && value.length > 50) {
      return (
        <textarea
          value={editedAttributes[key]}
          onChange={(e) => handleAttributeChange(key, e.target.value)}
          className="w-full bg-gray-750 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500 min-h-[100px]"
        />
      );
    } else {
      return (
        <input
          type="text"
          value={editedAttributes[key]}
          onChange={(e) => handleAttributeChange(key, e.target.value)}
          className="w-full bg-gray-750 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500"
        />
      );
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-70">
      <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-4">
          {isEditing ? (
            <input
              type="text"
              value={editedName}
              onChange={(e) => setEditedName(e.target.value)}
              className="text-2xl font-bold text-blue-300 bg-gray-750 border border-gray-700 rounded p-2 w-full"
            />
          ) : (
            <h2 className="text-2xl font-bold text-blue-300">{entity.name}</h2>
          )}
          <div className="flex space-x-2">
            {!isEditing && (
              <button 
                onClick={handleToggleEdit}
                className="text-blue-400 hover:text-blue-300"
              >
                Edit
              </button>
            )}
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="mb-4">
          <span className="text-gray-400 text-sm font-medium">Entity Type: </span>
          <span className="text-gray-300">{entity.entity_type_name || "Unknown"}</span>
        </div>

        {/* Description section */}
        <div className="mb-6">
          <h3 className="text-blue-400 text-lg font-medium mb-2">Description</h3>
          {isEditing ? (
            <textarea
              value={editedDescription}
              onChange={(e) => setEditedDescription(e.target.value)}
              className="w-full bg-gray-750 border border-gray-700 rounded p-2 text-gray-300 focus:outline-none focus:border-blue-500 min-h-[120px]"
            />
          ) : (
            <p className="text-gray-300 whitespace-pre-line">{entity.description}</p>
          )}
        </div>

        {/* Text attributes - full width */}
        {textAttrs.length > 0 && (
          <div className="mb-6">
            <h3 className="text-blue-400 text-lg font-medium mb-2">Details</h3>
            <div className="grid grid-cols-1 gap-4">
              {textAttrs.map(([key, value]) => (
                <div key={key} className="bg-gray-750 p-3 rounded border border-gray-700">
                  <div className="text-sm font-medium text-gray-400 mb-1">{key}</div>
                  {isEditing ? (
                    renderEditableAttribute(key, value)
                  ) : (
                    <div className="text-gray-300 break-words whitespace-pre-line">{formatAttributeValue(value)}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Other attributes - half width on medium+ screens */}
        {otherAttrs.length > 0 && (
          <div className="mb-6">
            <h3 className="text-blue-400 text-lg font-medium mb-2">Attributes</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {otherAttrs.map(([key, value]) => (
                <div key={key} className="bg-gray-750 p-3 rounded border border-gray-700">
                  <div className="text-sm font-medium text-gray-400 mb-1">{key}</div>
                  {isEditing ? (
                    renderEditableAttribute(key, value)
                  ) : (
                    <div className="text-gray-300 break-words">{formatAttributeValue(value)}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex justify-end mt-4 space-x-3">
          {isEditing && (
            <>
              <button
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 border border-gray-600 text-gray-300 rounded hover:bg-gray-700"
                disabled={isSaving}
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center"
                disabled={isSaving}
              >
                {isSaving ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Saving...
                  </>
                ) : 'Save Changes'}
              </button>
            </>
          )}
          {!isEditing && (
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors"
            >
              Close
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default EntityDetail; 