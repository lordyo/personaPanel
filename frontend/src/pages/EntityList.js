import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import api from '../services/api';
import EntityCard from '../components/EntityCard';
import EntityForm from '../components/EntityForm';
import EntityGenerationForm from '../components/EntityGenerationForm';
import EntityDetail from '../components/EntityDetail';
import LoadingIndicator from '../components/LoadingIndicator';

/**
 * Page component for listing, generating, and managing entity instances.
 * 
 * @returns {JSX.Element} - Rendered component
 */
const EntityList = () => {
  const location = useLocation();
  
  const [entityTypes, setEntityTypes] = useState([]);
  const [entities, setEntities] = useState([]);
  const [filteredEntities, setFilteredEntities] = useState([]);
  const [selectedEntities, setSelectedEntities] = useState([]);
  const [viewingEntity, setViewingEntity] = useState(null);
  const [editingEntity, setEditingEntity] = useState(null);
  const [editingEntityType, setEditingEntityType] = useState(null);
  const [loading, setLoading] = useState(false);
  // Check if we should open generation panel automatically based on location state
  const [generatingEntities, setGeneratingEntities] = useState(
    location.state?.entityTypeId ? true : false
  );
  // Initialize filter with entityTypeId from location state if available
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTypeId, setFilterTypeId] = useState(location.state?.entityTypeId || '');
  const [error, setError] = useState(null);
  const [deleteConfirmation, setDeleteConfirmation] = useState(null);
  const [deleting, setDeleting] = useState(false);
  
  // Pre-select the entity type in the generation form if provided via location state
  const [preselectedEntityTypeId, setPreselectedEntityTypeId] = useState(
    location.state?.entityTypeId || ''
  );
  
  // Fetch entity types and entities on component mount
  useEffect(() => {
    fetchData();
    
    // Clear location state after using it to avoid persistence on refresh
    if (location.state?.entityTypeId) {
      window.history.replaceState({}, document.title);
    }
  }, []);
  
  // Define fetchData function in the component scope so it can be reused
  const fetchData = async () => {
    try {
      setLoading(true);
      const typesResponse = await api.getEntityTypes();
      // Handle both response formats
      const types = typesResponse.data || typesResponse;
      setEntityTypes(Array.isArray(types) ? types : []);
      
      // Fetch all entities 
      const entitiesPromises = (typesResponse.data || typesResponse).map(type => 
        api.getEntitiesByType(type.id)
      );
      
      const entitiesResponses = await Promise.all(entitiesPromises);
      const allEntities = entitiesResponses.flatMap((response, index) => {
        // Get the entity type for this response
        const entityType = types[index];
        // Get the entities from the response
        const entities = response.data || response || [];
        
        // Add entity_type_name to each entity for display
        return entities.map(entity => ({
          ...entity,
          entity_type_id: entityType.id,
          entity_type_name: entityType.name
        }));
      });
      
      setEntities(allEntities);
      setFilteredEntities(allEntities);
      setError(null);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError("Failed to load entity types and entities. " + (err.message || ""));
    } finally {
      setLoading(false);
    }
  };
  
  // Filter entities when search term or filter type changes
  useEffect(() => {
    // Filter out invalid entities first (those without ID or critical properties)
    let filtered = entities.filter(entity => entity && entity.id);
    
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(entity => 
        (entity.name && entity.name.toLowerCase().includes(term)) || 
        (entity.entity_type_name && entity.entity_type_name.toLowerCase().includes(term))
      );
    }
    
    if (filterTypeId) {
      filtered = filtered.filter(entity => entity.entity_type_id === filterTypeId);
    }
    
    setFilteredEntities(filtered);
  }, [entities, searchTerm, filterTypeId]);
  
  const handleSelectEntity = (entityId) => {
    setSelectedEntities(prev => {
      // If the entity is already selected, remove it from the selection
      if (prev.includes(entityId)) {
        return prev.filter(id => id !== entityId);
      }
      
      // Otherwise, add it to the selection
      return [...prev, entityId];
    });
  };
  
  // New function to select all filtered entities
  const selectAll = () => {
    // Get all the IDs from the filtered entities
    const allFilteredIds = filteredEntities.map(entity => entity.id);
    setSelectedEntities(allFilteredIds);
  };
  
  // New function to deselect all entities
  const selectNone = () => {
    setSelectedEntities([]);
  };
  
  const handleViewEntity = (entity) => {
    setViewingEntity(entity);
  };
  
  const handleEditEntity = async (entityId) => {
    try {
      setLoading(true);
      const entity = entities.find(e => e.id === entityId);
      
      if (!entity) {
        throw new Error('Entity not found');
      }
      
      // Find the entity type for this entity
      const entityTypeId = entity.entity_type_id;
      const entityType = entityTypes.find(et => et.id === entityTypeId);
      
      if (!entityType) {
        throw new Error('Entity type not found');
      }
      
      setEditingEntity(entity);
      setEditingEntityType(entityType);
    } catch (err) {
      setError('Failed to load entity for editing.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleUpdateEntity = async (updatedEntity) => {
    setLoading(true);
    
    try {
      const result = await api.updateEntity(updatedEntity.id, updatedEntity);
      
      // Update the entity in our local state
      setEntities(prev => 
        prev.map(entity => 
          entity.id === updatedEntity.id ? result : entity
        )
      );
      
      // Update viewing entity if this entity is being viewed
      if (viewingEntity && viewingEntity.id === updatedEntity.id) {
        setViewingEntity(result);
      }
      
      setError(null);
      return Promise.resolve(result);
    } catch (err) {
      console.error("Error updating entity:", err);
      setError("Failed to update entity. " + (err.message || ""));
      return Promise.reject(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleGenerateEntities = async (formData) => {
    try {
      setGeneratingEntities(false); // Hide the form
      setLoading(true); // Show loading indicator
      setError(null);
      
      // Find the entity type first to ensure we have the name
      const entityType = entityTypes.find(et => et.id === formData.entityTypeId);
      if (!entityType) {
        throw new Error("Entity type not found");
      }
      
      console.log("Generating entities with form data:", formData);
      
      const response = await api.generateEntities(
        formData.entityTypeId,
        formData.count,
        formData.variability,
        formData.entityDescription
      );
      
      console.log("Generation response:", response);
      
      if (response.status === 'success') {
        // Check if the response has entities directly in it
        if (response.data && response.data.entities && Array.isArray(response.data.entities)) {
          // Use the entities directly from the response
          const newEntities = response.data.entities;
          
          // Add entity_type_name to each entity for display purposes
          const processedEntities = newEntities.map(entity => ({
            ...entity,
            entity_type_id: formData.entityTypeId,
            entity_type_name: entityType.name || 'Unknown Type'
          }));
          
          console.log("Processed entities:", processedEntities);
          
          // Update the entities state
          setEntities(prev => {
            // Filter out any entities of this type that might have the same ID
            // This ensures we don't have duplicates
            const existingEntitiesFiltered = prev.filter(entity => 
              !processedEntities.some(newEntity => newEntity.id === entity.id)
            );
            return [...existingEntitiesFiltered, ...processedEntities];
          });
        } else {
          // Fallback - refetch all entities if we don't get them directly
          await fetchData();
        }
        
        // Clear any previous error
        setError(null);
      } else {
        console.error("Error response from generate entities:", response);
        setError(response.message || 'Failed to generate entities');
      }
    } catch (err) {
      console.error("Error generating entities:", err);
      setError("Failed to generate entities: " + (err.message || ""));
    } finally {
      setLoading(false);
    }
  };
  
  const handleClearFilters = () => {
    setSearchTerm('');
    setFilterTypeId('');
  };
  
  const handleDeleteEntity = (entityId) => {
    // Find the entity to get its name
    const entityToDelete = entities.find(e => e.id === entityId);
    if (entityToDelete) {
      setDeleteConfirmation({
        id: entityId,
        name: entityToDelete.name || 'Unnamed Entity'
      });
    }
  };
  
  const confirmDelete = async () => {
    if (!deleteConfirmation) return;
    
    try {
      setDeleting(true);
      
      if (deleteConfirmation.id) {
        // Single entity deletion
        await api.deleteEntity(deleteConfirmation.id);
        
        // Remove the entity from state
        setEntities(prev => prev.filter(e => e.id !== deleteConfirmation.id));
        
        // Also remove from selected entities if it's there
        if (selectedEntities.includes(deleteConfirmation.id)) {
          setSelectedEntities(prev => prev.filter(id => id !== deleteConfirmation.id));
        }
        
        // Close the entity detail view if this entity was being viewed
        if (viewingEntity && viewingEntity.id === deleteConfirmation.id) {
          setViewingEntity(null);
        }
      } else if (deleteConfirmation.typeId) {
        // Delete all entities of a type
        await api.deleteEntitiesByType(deleteConfirmation.typeId);
        
        // Remove entities of this type from state
        setEntities(prev => prev.filter(e => e.entity_type_id !== deleteConfirmation.typeId));
        
        // Also remove from selected entities
        setSelectedEntities(prev => 
          prev.filter(id => 
            !entities.find(e => e.id === id && e.entity_type_id === deleteConfirmation.typeId)
          )
        );
        
        // Close the entity detail view if an entity of this type was being viewed
        if (viewingEntity && viewingEntity.entity_type_id === deleteConfirmation.typeId) {
          setViewingEntity(null);
        }
      }
      
      // Clear error if any
      setError(null);
    } catch (err) {
      console.error("Error deleting entity:", err);
      setError("Failed to delete entity. " + (err.message || ""));
    } finally {
      setDeleting(false);
      setDeleteConfirmation(null);
    }
  };
  
  const cancelDelete = () => {
    setDeleteConfirmation(null);
  };
  
  // Handle batch delete for selected entities
  const handleDeleteSelected = () => {
    if (selectedEntities.length === 0) return;
    
    if (window.confirm(`Are you sure you want to delete ${selectedEntities.length} selected entities?`)) {
      // Delete each selected entity
      Promise.all(selectedEntities.map(id => api.deleteEntity(id)))
        .then(() => {
          // Update UI state after successful deletion
          setEntities(prev => prev.filter(entity => !selectedEntities.includes(entity.id)));
          setSelectedEntities([]);
          setError(null);
        })
        .catch(err => {
          console.error("Error deleting selected entities:", err);
          setError("Failed to delete some entities. Please try again.");
        });
    }
  };
  
  if (loading && !entities.length) {
    return <LoadingIndicator message="Loading entities..." />;
  }
  
  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <h1 className="text-3xl font-bold text-white mb-8">Entity Management</h1>
      
      {/* Controls and filters */}
      <div className="mb-6 bg-gray-800 p-4 rounded-lg border border-gray-700">
        <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-4 mb-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search entities..."
              className="w-full px-4 py-2 bg-gray-750 border border-gray-700 rounded text-gray-300 focus:outline-none focus:border-blue-500"
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="md:w-1/3">
            <select
              className="w-full px-4 py-2 bg-gray-750 border border-gray-700 rounded text-gray-300 focus:outline-none focus:border-blue-500"
              value={filterTypeId || ""}
              onChange={e => setFilterTypeId(e.target.value === "" ? null : e.target.value)}
            >
              <option value="">All Entity Types</option>
              {entityTypes.map(type => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="flex flex-col md:flex-row md:items-center justify-between">
          <div>
            <button
              onClick={() => setGeneratingEntities(!generatingEntities)}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mb-3 md:mb-0 mr-3 focus:outline-none"
            >
              {generatingEntities ? 'Cancel' : 'Generate Entities'}
            </button>
            
            {selectedEntities.length > 0 && (
              <button
                onClick={() => handleDeleteSelected()}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none mr-3"
              >
                Delete Selected ({selectedEntities.length})
              </button>
            )}
          </div>
          
          {selectedEntities.length > 1 && (
            <Link 
              to={`/simulation-create?entityIds=${selectedEntities.join(',')}`}
              className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 focus:outline-none"
            >
              Simulate Selected Entities
            </Link>
          )}
        </div>
      </div>
      
      {/* Generation form */}
      {generatingEntities && (
        <div className="mb-6 bg-gray-800 p-4 rounded-lg border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-4">Generate New Entities</h2>
          <EntityGenerationForm 
            entityTypes={entityTypes}
            onSubmit={handleGenerateEntities}
            disabled={loading}
            preselectedEntityTypeId={preselectedEntityTypeId}
          />
          <button
            onClick={() => setGeneratingEntities(false)}
            className="mt-4 text-gray-400 hover:text-white block ml-auto"
          >
            Cancel
          </button>
        </div>
      )}
      
      {/* Error display */}
      {error && (
        <div className="mb-6 bg-red-900 text-white p-4 rounded-lg">
          <h3 className="font-bold mb-2">Error</h3>
          <p>{error}</p>
        </div>
      )}
      
      {/* Loading indicator for entity generation */}
      {loading && entities.length > 0 && (
        <div className="mb-6 bg-gray-800 p-4 rounded-lg border border-gray-700">
          <LoadingIndicator 
            message="Generating entities, please wait..." 
            inline={true} 
            size="small"
          />
        </div>
      )}
      
      {/* Entity list */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-white">Entities</h2>
          
          {/* Select All/None buttons */}
          {filteredEntities.length > 0 && (
            <div className="inline-flex rounded-md shadow-sm" role="group">
              <button
                onClick={selectAll}
                className="px-3 py-1 text-sm bg-gray-700 text-gray-300 hover:bg-gray-600 rounded-l focus:outline-none"
                title="Select all entities"
              >
                Select All
              </button>
              <button
                onClick={selectNone}
                className="px-3 py-1 text-sm bg-gray-700 text-gray-300 hover:bg-gray-600 rounded-r focus:outline-none border-l border-gray-600"
                title="Deselect all entities"
              >
                Select None
              </button>
            </div>
          )}
        </div>
        
        {loading && !entities.length && (
          <div className="flex justify-center items-center p-8">
            <LoadingIndicator message="Loading entities..." size="large" />
          </div>
        )}
        
        {!loading && filteredEntities.length === 0 && (
          <div className="text-center p-8 bg-gray-800 rounded-lg border border-gray-700">
            <p className="text-gray-400">No entities found.</p>
            <button
              onClick={() => setGeneratingEntities(true)}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none"
            >
              Generate Entities
            </button>
          </div>
        )}
        
        {filteredEntities.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredEntities.map(entity => (
              <EntityCard 
                key={entity.id}
                entity={entity}
                isSelected={selectedEntities.includes(entity.id)}
                onSelect={handleSelectEntity}
                onViewDetails={handleViewEntity}
                onDelete={handleDeleteEntity}
              />
            ))}
          </div>
        )}
      </div>
      
      {/* Entity detail modal */}
      {viewingEntity && (
        <EntityDetail 
          entity={viewingEntity}
          entityType={entityTypes.find(t => t.id === viewingEntity.entity_type_id)}
          onClose={() => setViewingEntity(null)}
          onSave={handleUpdateEntity}
        />
      )}
      
      {/* Delete confirmation modal */}
      {deleteConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg max-w-md w-full border border-gray-700">
            <h3 className="text-xl font-bold text-white mb-4">Confirm Deletion</h3>
            <p className="text-gray-300 mb-6">
              {deleteConfirmation.id 
                ? `Are you sure you want to delete "${deleteConfirmation.name}"?` 
                : `Are you sure you want to delete all entities of type "${deleteConfirmation.typeName}"?`}
              <br/>
              <span className="text-red-400 text-sm">This action cannot be undone.</span>
            </p>
            
            <div className="flex justify-end space-x-4">
              <button
                onClick={cancelDelete}
                className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 focus:outline-none"
                disabled={deleting}
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none flex items-center justify-center disabled:bg-gray-600"
                disabled={deleting}
              >
                {deleting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-b-0 border-white mr-2"></div>
                    <span>Deleting...</span>
                  </>
                ) : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EntityList; 