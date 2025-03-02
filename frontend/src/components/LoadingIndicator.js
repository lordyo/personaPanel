import React from 'react';

/**
 * Component for displaying a loading indicator with an optional message.
 * 
 * @param {Object} props - Component props
 * @param {string} props.message - Optional message to display with the spinner
 * @param {boolean} props.fullPage - Whether the loader should take up the full page
 * @param {boolean} props.inline - Whether the loader should be displayed inline (horizontally)
 * @param {string} props.size - Size of the spinner: 'small', 'medium', or 'large'
 * @returns {JSX.Element} - Rendered component
 */
const LoadingIndicator = ({ 
  message = 'Loading...', 
  fullPage = false,
  inline = false,
  size = 'medium'
}) => {
  // Determine container classes based on props
  const containerClass = fullPage 
    ? 'fixed inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75 z-50'
    : inline
      ? 'flex items-center'
      : 'flex items-center justify-center py-8';
  
  // Determine spinner size
  const spinnerSize = {
    small: 'h-4 w-4 border-2',
    medium: 'h-8 w-8 border-2',
    large: 'h-12 w-12 border-3'
  }[size] || 'h-8 w-8 border-2';
  
  // Determine text size
  const textSize = {
    small: 'text-xs',
    medium: 'text-sm',
    large: 'text-base'
  }[size] || 'text-sm';
    
  return (
    <div className={containerClass}>
      <div className={inline ? "flex items-center" : "text-center"}>
        <div className={`animate-spin rounded-full ${spinnerSize} border-b-2 border-blue-500 ${inline ? "mr-3" : "mx-auto"}`}></div>
        {message && <p className={`${inline ? "" : "mt-2"} ${textSize} text-gray-300`}>{message}</p>}
      </div>
    </div>
  );
};

export default LoadingIndicator; 