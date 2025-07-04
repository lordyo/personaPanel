import React from 'react';

/**
 * Component for displaying an entity instance in a card format
 * 
 * @param {Object} props - Component props
 * @param {Object} props.entity - Entity data to display
 * @param {boolean} props.isSelected - Whether this entity is selected
 * @param {Function} props.onSelect - Function to call when this entity is selected
 * @param {Function} props.onViewDetails - Function to call when viewing details
 * @param {Function} props.onDelete - Function to call when deleting this entity
 * @returns {JSX.Element} - Rendered component
 */
const EntityCard = ({ 
  entity, 
  isSelected, 
  onSelect, 
  onViewDetails,
  onDelete 
}) => {
  if (!entity) return null;
  
  const handleCheckboxClick = (e) => {
    // Stop event propagation to prevent card click
    e.stopPropagation();
    onSelect(entity.id);
  };
  
  const handleDeleteClick = (e) => {
    e.stopPropagation();
    if (window.confirm(`Are you sure you want to delete "${entity.name}"?`)) {
      onDelete(entity.id);
    }
  };
  
  const handleViewDetailsClick = (e) => {
    e.stopPropagation();
    onViewDetails(entity);
  };

  // Function to truncate description to first 100 words
  const truncateToWords = (text, wordCount) => {
    if (!text) return '';
    
    const words = text.split(/\s+/);
    if (words.length <= wordCount) return text;
    
    return words.slice(0, wordCount).join(' ') + '...';
  };

  // Handle click on the card itself
  const handleCardClick = () => {
    onViewDetails(entity);
  };

  return (
    <div 
      className={`bg-gray-800 border rounded-lg overflow-hidden transition-all duration-200 ${
        isSelected ? 'border-blue-500 shadow-lg shadow-blue-500/20' : 'border-gray-700 hover:border-gray-600'
      } cursor-pointer`}
      onClick={handleCardClick}
    >
      {/* Card header with selection checkbox */}
      <div className="p-4 flex items-start justify-between">
        <div className="flex items-center">
          <div 
            className="mr-3 flex-shrink-0"
            onClick={handleCheckboxClick}
          >
            <div className={`w-5 h-5 border rounded flex items-center justify-center cursor-pointer ${
              isSelected ? 'bg-blue-500 border-blue-500' : 'border-gray-600 hover:border-gray-500'
            }`}>
              {isSelected && (
                <svg 
                  className="w-3 h-3 text-white" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth="2" 
                    d="M5 13l4 4L19 7" 
                  />
                </svg>
              )}
            </div>
          </div>
          <div>
            <h3 className="text-blue-300 font-medium text-lg">{entity.name}</h3>
            <div className="text-gray-400 text-sm">
              {entity.entity_type_name || "Unknown Type"}
            </div>
          </div>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={handleViewDetailsClick}
            className="text-blue-400 hover:text-blue-300"
            title="View Details"
          >
            <svg 
              className="w-5 h-5" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth="2" 
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" 
              />
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth="2" 
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" 
              />
            </svg>
          </button>
          <button
            onClick={handleDeleteClick}
            className="text-red-400 hover:text-red-300"
            title="Delete Entity"
          >
            <svg 
              className="w-5 h-5" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth="2" 
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" 
              />
            </svg>
          </button>
        </div>
      </div>
      
      {/* Card body with entity description - only show first 100 words */}
      <div className="px-4 pb-4">
        {entity.description && (
          <p className="text-gray-300 text-sm">
            {truncateToWords(entity.description, 100)}
          </p>
        )}
      </div>
    </div>
  );
};

export default EntityCard; 