import React from 'react';

/**
 * Component for displaying a loading indicator with an optional message.
 * 
 * @param {Object} props - Component props
 * @param {string} props.message - Optional message to display with the spinner
 * @param {boolean} props.fullPage - Whether the loader should take up the full page
 * @returns {JSX.Element} - Rendered component
 */
const LoadingIndicator = ({ message = 'Loading...', fullPage = false }) => {
  const containerClass = fullPage 
    ? 'fixed inset-0 flex items-center justify-center bg-white bg-opacity-75 z-50'
    : 'flex items-center justify-center py-8';
    
  return (
    <div className={containerClass}>
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        {message && <p className="mt-2 text-gray-600">{message}</p>}
      </div>
    </div>
  );
};

export default LoadingIndicator; 