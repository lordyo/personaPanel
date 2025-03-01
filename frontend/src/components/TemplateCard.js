import React from 'react';

/**
 * Component for displaying an entity template in a card format.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.template - The template to display
 * @param {Function} props.onSelect - Function to call when the card is selected
 * @returns {JSX.Element} - Rendered component
 */
const TemplateCard = ({ template, onSelect }) => {
  return (
    <div 
      className="border rounded p-4 mb-3 cursor-pointer hover:bg-gray-50 transition"
      onClick={() => onSelect(template.id)}
      data-testid="template-card"
    >
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-semibold">{template.name}</h3>
        <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">Template</span>
      </div>
      <p className="text-gray-600 my-2">{template.description}</p>
      <button 
        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        onClick={(e) => {
          e.stopPropagation();
          onSelect(template.id);
        }}
        data-testid="use-template-button"
      >
        Use this template →
      </button>
    </div>
  );
};

export default TemplateCard; 