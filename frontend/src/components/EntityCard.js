import React, { useEffect } from 'react';

/**
 * Component for displaying an entity instance in a card format.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.entity - The entity instance to display
 * @param {boolean} props.isSelected - Whether the entity is selected
 * @param {Function} props.onSelect - Function to call when the card is selected
 * @param {Function} props.onEdit - Function to call when the edit button is clicked
 * @param {Function} props.onDelete - Function to call when the delete button is clicked
 * @returns {JSX.Element} - Rendered component
 */
const EntityCard = ({ entity, isSelected, onSelect, onEdit, onDelete }) => {
  // Log entity data for debugging
  useEffect(() => {
    if (entity && entity.id) {
      console.log(`Entity ${entity.id} data:`, entity);
      console.log(`Entity ${entity.id} attributes:`, entity.attributes);
    } else if (entity) {
      console.warn("Entity missing ID:", entity);
    }
  }, [entity]);

  // Return null if entity is undefined or missing critical properties
  if (!entity || !entity.id) {
    console.error("Received invalid entity data:", entity);
    return null;
  }

  // Get a few key attributes to display in the card
  const getDisplayAttributes = () => {
    if (!entity.attributes) {
      return [];
    }

    // Make sure we're working with an object
    const attributes = entity.attributes;
    if (typeof attributes !== 'object') {
      console.error('Attributes is not an object:', attributes);
      return [];
    }
    
    // Direct approach - just get the entries and display them
    return Object.entries(attributes)
      .slice(0, 3)
      .map(([key, value]) => (
        <div key={`${entity.id}-${key}`} className="text-sm">
          <span className="font-medium text-gray-400">{key}: </span>
          <span className="text-gray-300">
            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
          </span>
        </div>
      ));
  };
  
  // Count actual attributes
  const getAttributeCount = () => {
    if (!entity.attributes) {
      return 0;
    }
    
    return Object.keys(entity.attributes).length;
  };
  
  return (
    <div 
      className={`border rounded-lg p-4 mb-3 cursor-pointer transition-colors bg-gray-800 border-gray-700 ${
        isSelected ? 'border-blue-400 ring-1 ring-blue-400' : 'hover:border-gray-600 hover:bg-gray-750'
      }`}
      onClick={() => onSelect(entity.id)}
    >
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-semibold text-blue-300">{entity.name || 'Unnamed Entity'}</h3>
        <div className="flex space-x-2">
          <button 
            className="text-blue-400 hover:text-blue-300 text-sm"
            onClick={(e) => {
              e.stopPropagation(); // Prevent card selection
              onEdit(entity.id);
            }}
          >
            Edit
          </button>
          <button 
            className="text-red-400 hover:text-red-300 text-sm"
            onClick={(e) => {
              e.stopPropagation(); // Prevent card selection
              onDelete(entity.id);
            }}
          >
            Delete
          </button>
        </div>
      </div>
      
      <p className="text-gray-300 text-sm mb-2">Type: {entity.entity_type_name || 'Unknown Type'}</p>
      
      {entity.description && (
        <p className="text-gray-400 text-sm mb-2 line-clamp-2 overflow-hidden">
          {entity.description.substring(0, 150)}{entity.description.length > 150 ? '...' : ''}
        </p>
      )}
      
      <div className="mt-2 space-y-1">
        {getDisplayAttributes()}
        {getAttributeCount() > 3 && (
          <div className="text-sm text-gray-500">
            + {getAttributeCount() - 3} more attributes
          </div>
        )}
      </div>
    </div>
  );
};

export default EntityCard; 