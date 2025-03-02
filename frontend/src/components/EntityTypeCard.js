import React from 'react';

/**
 * Component for displaying an entity type in a card format.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.entityType - The entity type to display
 * @param {Function} props.onView - Function to call when the card is selected
 * @param {Function} props.onDelete - Function to call when the delete button is clicked
 * @returns {JSX.Element} - Rendered component
 */
const EntityTypeCard = ({ entityType, onView, onDelete }) => {
  const dimensionCount = entityType.dimensions ? entityType.dimensions.length : 0;
  
  const handleDeleteClick = (e) => {
    e.stopPropagation();
    onDelete && onDelete(entityType.id);
  };
  
  return (
    <div 
      className="border border-gray-700 rounded-lg overflow-hidden bg-gray-800 hover:bg-gray-750 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
      onClick={() => onView(entityType.id)}
    >
      <div className="p-5">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xl font-semibold text-blue-300">{entityType.name}</h3>
          {onDelete && (
            <button
              className="text-red-400 hover:text-red-300 transition-colors p-1 rounded hover:bg-red-900/30"
              onClick={handleDeleteClick}
              title="Delete entity type"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}
        </div>
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