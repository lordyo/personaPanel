import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { entityTypeApi } from '../services/api';
import LoadingIndicator from '../components/LoadingIndicator';

/**
 * Page component for displaying the details of a specific entity type.
 * 
 * @returns {JSX.Element} - Rendered component
 */
const EntityTypeDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [entityType, setEntityType] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchEntityType = async () => {
      try {
        const response = await entityTypeApi.getById(id);
        if (response && response.status === 'success') {
          setEntityType(response.data);
          setError(null);
        } else {
          console.error('Error fetching entity type:', response?.message || 'Unknown error');
          setError(`Failed to load entity type: ${response?.message || 'Unknown error'}`);
        }
      } catch (err) {
        console.error('Error fetching entity type:', err);
        setError('Failed to load entity type. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchEntityType();
  }, [id]);

  const handleBack = () => {
    navigate('/entity-types');
  };

  const handleCreateEntities = () => {
    navigate('/entities', { state: { entityTypeId: id } });
  };

  const handleEdit = () => {
    navigate(`/entity-types/${id}/edit`);
  };

  // Helper function to render dimension-specific details
  const renderDimensionDetails = (dimension) => {
    switch (dimension.type) {
      case 'categorical':
        return (
          <>
            {dimension.options && (
              <div className="mt-3">
                <div className="text-xs font-medium text-gray-500 mb-1">Options:</div>
                <div className="flex flex-wrap gap-1">
                  {dimension.options.map((option, i) => (
                    <span key={i} className="text-xs bg-gray-700 rounded px-2 py-1 text-gray-300">
                      {option}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {dimension.distribution_values && (
              <div className="mt-3">
                <div className="text-xs font-medium text-gray-500 mb-1">Distribution:</div>
                <div className="text-xs text-gray-300 space-y-1">
                  {dimension.options?.map(option => (
                    <div key={option} className="flex items-center justify-between">
                      <span>{option}:</span>
                      <div className="flex items-center">
                        <div className="w-24 h-2 bg-gray-700 rounded-full mr-2 overflow-hidden">
                          <div 
                            className="h-full bg-blue-500" 
                            style={{ width: `${(dimension.distribution_values[option] || 0) * 100}%` }}
                          ></div>
                        </div>
                        <span>{Math.round((dimension.distribution_values[option] || 0) * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        );
        
      case 'int':
      case 'float':
      case 'numerical': // Support legacy numerical type
        return (
          <>
            <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-xs font-medium text-gray-500">Min:</span>
                <span className="ml-1 text-gray-300">{dimension.min_value !== undefined ? dimension.min_value : (dimension.min !== undefined ? dimension.min : 'None')}</span>
              </div>
              <div>
                <span className="text-xs font-medium text-gray-500">Max:</span>
                <span className="ml-1 text-gray-300">{dimension.max_value !== undefined ? dimension.max_value : (dimension.max !== undefined ? dimension.max : 'None')}</span>
              </div>
            </div>
            
            {dimension.distribution && (
              <div className="mt-2">
                <span className="text-xs font-medium text-gray-500">Distribution:</span>
                <span className="ml-1 text-gray-300">{dimension.distribution}</span>
                
                {dimension.distribution === 'normal' && (
                  <div className="mt-1">
                    {dimension.spread_factor !== undefined ? (
                      <>
                        <span className="text-xs font-medium text-gray-500">Distribution Spread:</span>
                        <span className="ml-1 text-gray-300">
                          {dimension.spread_factor < 0.3 ? "Concentrated" : 
                           dimension.spread_factor < 0.7 ? "Moderate" : "Spread out"}
                          ({Math.round(dimension.spread_factor * 100)}%)
                        </span>
                      </>
                    ) : dimension.std_deviation !== undefined && (
                      <>
                        <span className="text-xs font-medium text-gray-500">Std Deviation:</span>
                        <span className="ml-1 text-gray-300">{dimension.std_deviation}</span>
                      </>
                    )}
                  </div>
                )}
                
                {dimension.distribution === 'skewed' && dimension.skew_factor !== undefined && (
                  <div className="mt-1">
                    <span className="text-xs font-medium text-gray-500">Skew Factor:</span>
                    <span className="ml-1 text-gray-300">{dimension.skew_factor}</span>
                  </div>
                )}
              </div>
            )}
          </>
        );
        
      case 'boolean':
        return (
          <div className="mt-3">
            {dimension.true_percentage !== undefined && (
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-xs font-medium text-gray-500">True:</span>
                  <span className="text-xs text-gray-300">{Math.round(dimension.true_percentage * 100)}%</span>
                </div>
                <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500" 
                    style={{ width: `${dimension.true_percentage * 100}%` }}
                  ></div>
                </div>
                <div className="flex justify-between">
                  <span className="text-xs font-medium text-gray-500">False:</span>
                  <span className="text-xs text-gray-300">{Math.round((1 - dimension.true_percentage) * 100)}%</span>
                </div>
              </div>
            )}
            
            {dimension.defaultValue !== undefined && (
              <div className="mt-1">
                <span className="text-xs font-medium text-gray-500">Default:</span>
                <span className="ml-1 text-gray-300">
                  {String(dimension.defaultValue)}
                </span>
              </div>
            )}
          </div>
        );
        
      default:
        return null;
    }
  };

  if (loading) {
    return <LoadingIndicator message="Loading entity type..." fullPage />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {error && (
        <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
          {error}
        </div>
      )}

      <div className="flex items-center mb-6">
        <button 
          onClick={handleBack}
          className="flex items-center text-blue-400 hover:text-blue-300"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
          </svg>
          Back to Entity Types
        </button>
      </div>

      {entityType && (
        <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 overflow-hidden">
          <div className="p-6">
            <div className="flex justify-between items-start mb-4">
              <h1 className="text-2xl font-bold text-blue-300">{entityType.name}</h1>
              <div className="flex space-x-2">
                <button 
                  onClick={handleEdit}
                  className="btn-primary px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
                >
                  Edit
                </button>
                <button 
                  onClick={handleCreateEntities}
                  className="btn-secondary px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded transition-colors"
                >
                  Create Entities
                </button>
              </div>
            </div>

            {entityType.description && (
              <div className="mb-6">
                <h2 className="text-lg text-blue-400 mb-2">Description</h2>
                <p className="text-gray-300">{entityType.description}</p>
              </div>
            )}

            <div className="mb-4">
              <h2 className="text-lg text-blue-400 mb-2">ID</h2>
              <p className="text-gray-300 font-mono text-sm bg-gray-750 p-2 rounded-md">{entityType.id}</p>
            </div>

            <div className="border-t border-gray-700 my-8"></div>

            <div>
              <h2 className="text-lg text-blue-400 mb-4">Dimensions ({entityType.dimensions?.length || 0})</h2>
              
              {(entityType.dimensions?.length > 0) ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {entityType.dimensions.map((dimension, index) => (
                    <div key={index} className="bg-gray-750 rounded-lg p-4 border border-gray-700">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="text-md font-semibold text-blue-300">{dimension.name}</h3>
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-700 text-gray-300">
                          {dimension.type}
                        </span>
                      </div>
                      
                      {dimension.description && (
                        <p className="text-sm text-gray-400 mb-2">{dimension.description}</p>
                      )}
                      
                      {renderDimensionDetails(dimension)}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400 italic">No dimensions defined</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EntityTypeDetail; 