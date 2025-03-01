import React from 'react';

/**
 * Component for displaying an entity type in a card format.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.entityType - The entity type to display
 * @param {Function} props.onSelect - Function to call when the card is selected
 * @returns {JSX.Element} - Rendered component
 */
const EntityTypeCard = ({ entityType, onSelect }) => {
  const dimensionCount = entityType.dimensions ? entityType.dimensions.length : 0;
  
  return (
    <div 
      className="border rounded p-4 mb-3 cursor-pointer hover:bg-gray-50"
      onClick={() => onSelect(entityType.id)}
    >
      <h3 className="text-lg font-semibold">{entityType.name}</h3>
      <p className="text-gray-600 mb-2">{entityType.description}</p>
      <div className="text-sm text-gray-500">
        {dimensionCount} dimension{dimensionCount !== 1 ? 's' : ''}
      </div>
    </div>
  );
};

export default EntityTypeCard; 