import React, { useState } from 'react';

/**
 * Component that provides information about the multi-step entity generation approach
 * @returns {JSX.Element} Rendered component
 */
const MultiStepInfo = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div className="bg-indigo-900 border border-indigo-800 rounded-lg p-4 mb-6 relative">
      <div className="flex items-start">
        <div className="flex-shrink-0 mt-0.5">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-indigo-300" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <h3 className="text-md font-medium text-indigo-200">
            New: Multi-Step Entity Generation
          </h3>
          <div className="mt-2 text-sm text-indigo-300">
            <p>
              We now use a two-step approach with "bisociative fueling" for more creative and diverse entities.
              {!isOpen && (
                <button 
                  onClick={() => setIsOpen(true)}
                  className="inline-flex ml-1 text-indigo-200 hover:text-white underline focus:outline-none"
                >
                  Learn more
                </button>
              )}
            </p>
            {isOpen && (
              <div className="mt-2 space-y-2">
                <p>
                  The multi-step method works in two phases:
                </p>
                <ol className="list-decimal pl-5 space-y-1">
                  <li>First, we generate basic attributes for the entity based on its type and dimensions</li>
                  <li>Then, we use random inspiring words (bisociative fuel) to enhance creativity when generating names and backstories</li>
                </ol>
                <p>
                  This approach results in much more diverse entities with unique characteristics, names, and stories - 
                  especially when generating multiple entities at once.
                </p>
                <button 
                  onClick={() => setIsOpen(false)}
                  className="text-indigo-200 hover:text-white underline focus:outline-none"
                >
                  Show less
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="absolute top-2 right-2 text-indigo-300 hover:text-white focus:outline-none"
        aria-label={isOpen ? "Close information" : "Open information"}
      >
        {isOpen ? (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
          </svg>
        )}
      </button>
    </div>
  );
};

export default MultiStepInfo; 