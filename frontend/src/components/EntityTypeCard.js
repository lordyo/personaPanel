import React from 'react';

/**
 * Component for displaying an entity type in a card format.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.entityType - The entity type to display
 * @param {Function} props.onView - Function to call when the card is selected
 * @returns {JSX.Element} - Rendered component
 */
const EntityTypeCard = ({ entityType, onView }) => {
  const dimensionCount = entityType.dimensions ? entityType.dimensions.length : 0;
  
  return (
    <div 
      className="border border-gray-700 rounded-lg overflow-hidden bg-gray-800 hover:bg-gray-750 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
      onClick={() => onView(entityType.id)}
    >
      <div className="p-5">
        <h3 className="text-xl font-semibold text-blue-300 mb-2">{entityType.name}</h3>
        <p className="text-gray-300 mb-4 line-clamp-2 min-h-[3rem]">{entityType.description || "No description provided"}</p>
        
        <div className="mt-4 flex items-center justify-between">
          <div className="flex items-center">
            <span className="bg-gray-700 text-gray-300 text-xs font-medium px-2.5 py-1 rounded-full">
              {dimensionCount} dimension{dimensionCount !== 1 ? 's' : ''}
            </span>
          </div>
          <button className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors">
            View Details →
          </button>
        </div>
      </div>
    </div>
  );
};

export default EntityTypeCard; 