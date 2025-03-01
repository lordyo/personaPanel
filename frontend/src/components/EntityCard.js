import React from 'react';

/**
 * Component for displaying an entity instance in a card format.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.entity - The entity instance to display
 * @param {boolean} props.isSelected - Whether the entity is selected
 * @param {Function} props.onSelect - Function to call when the card is selected
 * @param {Function} props.onEdit - Function to call when the edit button is clicked
 * @returns {JSX.Element} - Rendered component
 */
const EntityCard = ({ entity, isSelected, onSelect, onEdit }) => {
  // Get a few key attributes to display in the card
  const getDisplayAttributes = () => {
    const attributes = entity.attributes || {};
    const attributeEntries = Object.entries(attributes);
    
    // Return at most 3 attributes
    return attributeEntries.slice(0, 3).map(([key, value]) => (
      <div key={key} className="text-sm">
        <span className="font-medium text-gray-400">{key}: </span>
        <span className="text-gray-300">{typeof value === 'object' ? JSON.stringify(value) : String(value)}</span>
      </div>
    ));
  };
  
  return (
    <div 
      className={`border rounded-lg p-4 mb-3 cursor-pointer transition-colors bg-gray-800 border-gray-700 ${
        isSelected ? 'border-blue-400 ring-1 ring-blue-400' : 'hover:border-gray-600 hover:bg-gray-750'
      }`}
      onClick={() => onSelect(entity.id)}
    >
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-semibold text-blue-300">{entity.name}</h3>
        <button 
          className="text-blue-400 hover:text-blue-300 text-sm"
          onClick={(e) => {
            e.stopPropagation(); // Prevent card selection
            onEdit(entity.id);
          }}
        >
          Edit
        </button>
      </div>
      
      <p className="text-gray-300 text-sm mb-2">Type: {entity.entity_type_name}</p>
      
      <div className="mt-2 space-y-1">
        {getDisplayAttributes()}
        {Object.keys(entity.attributes || {}).length > 3 && (
          <div className="text-sm text-gray-500">
            + {Object.keys(entity.attributes || {}).length - 3} more attributes
          </div>
        )}
      </div>
    </div>
  );
};

export default EntityCard; 