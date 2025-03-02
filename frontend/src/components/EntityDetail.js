import React from 'react';

/**
 * Component for displaying detailed information about an entity.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.entity - The entity to display
 * @param {Function} props.onClose - Function to call when the modal is closed
 * @returns {JSX.Element} - Rendered component
 */
const EntityDetail = ({ entity, onClose }) => {
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

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-70">
      <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-2xl font-bold text-blue-300">{entity.name}</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="mb-4">
          <span className="text-gray-400 text-sm font-medium">Entity Type: </span>
          <span className="text-gray-300">{entity.entity_type_name}</span>
        </div>

        {entity.description && (
          <div className="mb-6">
            <h3 className="text-blue-400 text-lg font-medium mb-2">Description</h3>
            <p className="text-gray-300 whitespace-pre-line">{entity.description}</p>
          </div>
        )}

        <div className="mb-6">
          <h3 className="text-blue-400 text-lg font-medium mb-2">Attributes</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {entity.attributes && Object.entries(entity.attributes).map(([key, value]) => (
              <div key={key} className="bg-gray-750 p-3 rounded border border-gray-700">
                <div className="text-sm font-medium text-gray-400">{key}</div>
                <div className="text-gray-300 break-words">{formatAttributeValue(value)}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-end mt-4">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default EntityDetail; 