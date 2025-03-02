import React from 'react';

/**
 * Component for displaying an entity template in a card format.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.template - The template to display
 * @param {Function} props.onSelect - Function to call when the card is selected
 * @param {Function} props.onDelete - Function to call when the delete button is clicked
 * @returns {JSX.Element} - Rendered component
 */
const TemplateCard = ({ template, onSelect, onDelete }) => {
  const handleDeleteClick = (e) => {
    e.stopPropagation();
    onDelete && onDelete(template.id);
  };
  
  return (
    <div 
      className="border border-gray-700 rounded-lg overflow-hidden bg-gray-800 hover:bg-gray-750 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
      onClick={() => onSelect(template.id)}
      data-testid="template-card"
    >
      <div className="p-5">
        <div className="flex justify-between items-start mb-3">
          <h3 className="text-xl font-semibold text-blue-300">{template.name}</h3>
          <div className="flex items-center gap-2">
            <span className="bg-blue-900/70 text-blue-300 text-xs font-medium px-2.5 py-1 rounded-full">Template</span>
            {onDelete && (
              <button
                className="text-red-400 hover:text-red-300 transition-colors p-1 rounded hover:bg-red-900/30"
                onClick={handleDeleteClick}
                title="Delete template"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            )}
          </div>
        </div>
        
        <p className="text-gray-300 mb-4 line-clamp-2 min-h-[3rem]">{template.description || "No description provided"}</p>
        
        <div className="mt-4 text-right">
          <button 
            className="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors inline-flex items-center gap-1"
            onClick={(e) => {
              e.stopPropagation();
              onSelect(template.id);
            }}
            data-testid="use-template-button"
          >
            Use this template 
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TemplateCard; 