import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
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
  const [entityTypes, setEntityTypes] = useState([]);
  const [entities, setEntities] = useState([]);
  const [filteredEntities, setFilteredEntities] = useState([]);
  const [selectedEntities, setSelectedEntities] = useState([]);
  const [viewingEntity, setViewingEntity] = useState(null);
  const [editingEntity, setEditingEntity] = useState(null);
  const [editingEntityType, setEditingEntityType] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generatingEntities, setGeneratingEntities] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTypeId, setFilterTypeId] = useState('');
  const [error, setError] = useState(null);
  const [deleteConfirmation, setDeleteConfirmation] = useState(null); // {id, name} for single entity or {typeId, typeName} for all of a type
  const [deleting, setDeleting] = useState(false);
  
  // Fetch entity types and entities on component mount
  useEffect(() => {
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
          
          // Add entity_type_name to each entity
          return entities.map(entity => ({
            ...entity,
            entity_type_id: entityType.id,
            entity_type_name: entityType.name || 'Unknown Type'
          }));
        });
        
        setEntities(allEntities);
        setFilteredEntities(allEntities);
      } catch (err) {
        setError('Failed to load data. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
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
      setGeneratingEntities(true);
      setError(null);
      
      // Find the entity type first to ensure we have the name
      const entityType = entityTypes.find(et => et.id === formData.entityTypeId);
      if (!entityType) {
        throw new Error("Entity type not found");
      }
      
      const response = await api.generateEntities(
        formData.entityTypeId,
        formData.count,
        formData.variability,
        formData.entityDescription
      );
      
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
          
          // Update the entities state
          setEntities(prev => {
            // Filter out any entities of this type that might have the same ID
            // This ensures we don't have duplicates
            const filteredEntities = prev.filter(e => 
              !processedEntities.some(newEntity => newEntity.id === e.id)
            );
            return [...filteredEntities, ...processedEntities];
          });
        } else {
          // Fallback to the old way - fetch entities again
          const newEntitiesResponse = await api.getEntitiesByType(formData.entityTypeId);
          
          // Get the entities from the response
          const newEntitiesData = newEntitiesResponse.data || newEntitiesResponse || [];
          
          // Add entity_type_name to each entity
          const processedEntities = newEntitiesData.map(entity => ({
            ...entity,
            entity_type_id: formData.entityTypeId,
            entity_type_name: entityType.name || 'Unknown Type'
          }));
          
          // Add or replace entities of this type in our state
          setEntities(prev => {
            // Filter out entities of the same type
            const otherEntities = prev.filter(e => e.entity_type_id !== formData.entityTypeId);
            // Add the new entities with proper type name
            return [...otherEntities, ...processedEntities];
          });
        }
      } else {
        setError('Failed to generate entities: ' + (response.message || 'Unknown error'));
      }
    } catch (err) {
      setError('Failed to generate entities. Please try again.');
      console.error(err);
    } finally {
      setGeneratingEntities(false);
    }
  };
  
  const handleClearFilters = () => {
    setSearchTerm('');
    setFilterTypeId('');
  };
  
  const handleDeleteEntity = (entityId) => {
    setLoading(true);
    
    api.deleteEntity(entityId)
      .then(() => {
        // Remove from selection if selected
        setSelectedEntities(prev => 
          prev.filter(id => id !== entityId)
        );
        
        // Close detail modal if viewing this entity
        if (viewingEntity && viewingEntity.id === entityId) {
          setViewingEntity(null);
        }
        
        // Close edit form if editing this entity
        if (editingEntity && editingEntity.id === entityId) {
          setEditingEntity(null);
        }
        
        // Remove from entities list
        setEntities(prev => 
          prev.filter(entity => entity.id !== entityId)
        );
        
        setError(null);
      })
      .catch(err => {
        console.error("Error deleting entity:", err);
        setError("Failed to delete entity. " + (err.message || ""));
      })
      .finally(() => {
        setLoading(false);
      });
  };
  
  const handleDeleteAllEntities = async () => {
    if (!filterTypeId) return;
    
    // Find the entity type name
    const entityType = entityTypes.find(type => type.id === filterTypeId);
    if (!entityType) return;
    
    // Set up confirmation dialog for deleting all entities of this type
    setDeleteConfirmation({
      typeId: filterTypeId,
      typeName: entityType.name,
      isAll: true
    });
  };
  
  const confirmDelete = async () => {
    try {
      setDeleting(true);
      
      if (deleteConfirmation.isAll) {
        // Delete all entities of a type
        const response = await api.deleteEntitiesByType(deleteConfirmation.typeId);
        
        if (response.status === 'success') {
          // Update the entities list by removing all entities of this type
          setEntities(prev => prev.filter(e => e.entity_type_id !== deleteConfirmation.typeId));
          setFilteredEntities(prev => prev.filter(e => e.entity_type_id !== deleteConfirmation.typeId));
          setSelectedEntities(prev => prev.filter(id => {
            const entity = entities.find(e => e.id === id);
            return entity && entity.entity_type_id !== deleteConfirmation.typeId;
          }));
        } else {
          setError(`Failed to delete entities: ${response.message}`);
        }
      } else {
        // Delete a single entity
        const response = await api.deleteEntity(deleteConfirmation.id);
        
        if (response.status === 'success') {
          // Update the entities list
          setEntities(prev => prev.filter(e => e.id !== deleteConfirmation.id));
          setFilteredEntities(prev => prev.filter(e => e.id !== deleteConfirmation.id));
          setSelectedEntities(prev => prev.filter(id => id !== deleteConfirmation.id));
        } else {
          setError(`Failed to delete entity: ${response.message}`);
        }
      }
    } catch (err) {
      setError('An error occurred during deletion. Please try again.');
      console.error(err);
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
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none"
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
      
      {/* Entity list */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-4">Entities</h2>
        
        {loading && (
          <div className="flex justify-center items-center p-8">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
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
    </div>
  );
};

export default EntityList; 