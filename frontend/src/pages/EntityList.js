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
  const [selectedEntityIds, setSelectedEntityIds] = useState([]);
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
        const allEntities = entitiesResponses.flatMap(response => 
          response.data || response || []
        );
        
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
    // Find the entity in our list
    const entity = entities.find(e => e.id === entityId);
    if (entity) {
      setViewingEntity(entity);
    }
    
    setSelectedEntityIds(prev => {
      if (prev.includes(entityId)) {
        return prev.filter(id => id !== entityId);
      } else {
        return [...prev, entityId];
      }
    });
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
    try {
      setLoading(true);
      const response = await api.updateEntity(updatedEntity.id, updatedEntity);
      
      if (response.status === 'success') {
        // Update the entity in the local state
        setEntities(prev => prev.map(entity => 
          entity.id === updatedEntity.id ? updatedEntity : entity
        ));
        
        // Clear editing state
        setEditingEntity(null);
        setEditingEntityType(null);
      } else {
        setError('Failed to update entity.');
      }
    } catch (err) {
      setError('Failed to update entity.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleGenerateEntities = async (formData) => {
    try {
      setGeneratingEntities(true);
      setError(null);
      
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
          const entityType = entityTypes.find(et => et.id === formData.entityTypeId);
          const processedEntities = newEntities.map(entity => ({
            ...entity,
            entity_type_id: formData.entityTypeId,
            entity_type_name: entityType?.name || 'Unknown Type'
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
          const entityType = entityTypes.find(et => et.id === formData.entityTypeId);
          const newEntitiesResponse = await api.getEntitiesByType(formData.entityTypeId);
          
          // Add or replace entities of this type in our state
          setEntities(prev => {
            // Filter out entities of the same type
            const otherEntities = prev.filter(e => e.entity_type_id !== formData.entityTypeId);
            // Add the new entities - check if response has data property or is the data itself
            const newEntities = newEntitiesResponse.data || newEntitiesResponse;
            return [...otherEntities, ...(Array.isArray(newEntities) ? newEntities : [])];
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
  
  const handleDeleteEntity = async (entityId) => {
    if (!entityId) {
      console.error("Attempted to delete entity with undefined ID");
      return;
    }
    
    // Find the entity to show its name in the confirmation
    const entityToDelete = entities.find(e => e.id === entityId);
    if (!entityToDelete) return;
    
    // Set up confirmation dialog
    setDeleteConfirmation({
      id: entityId,
      name: entityToDelete.name || 'Unnamed Entity',
      isAll: false
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
          setSelectedEntityIds(prev => prev.filter(id => {
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
          setSelectedEntityIds(prev => prev.filter(id => id !== deleteConfirmation.id));
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
  
  if (loading && !entities.length) {
    return <LoadingIndicator message="Loading entities..." />;
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-blue-300">Entity Management</h1>
        <Link 
          to="/simulations/create" 
          className={`px-4 py-2 rounded transition-colors ${
            !selectedEntityIds.length 
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed' 
              : 'bg-green-400 hover:bg-green-500 text-white'
          }`}
          onClick={e => !selectedEntityIds.length && e.preventDefault()}
        >
          Simulate with {selectedEntityIds.length} Selected
        </Link>
      </div>
      
      {error && (
        <div className="p-4 mb-6 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
          <p>{error}</p>
        </div>
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column: Entity Generation */}
        <div className="lg:col-span-1">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 shadow-card">
            <h2 className="text-xl font-semibold text-blue-300 mb-4">Generate Entities</h2>
            {generatingEntities ? (
              <LoadingIndicator message="Generating entities..." />
            ) : (
              <EntityGenerationForm 
                entityTypes={entityTypes} 
                onGenerate={handleGenerateEntities} 
              />
            )}
          </div>
        </div>
        
        {/* Right column: Entity List */}
        <div className="lg:col-span-2">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 shadow-card">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
              <h2 className="text-xl font-semibold text-blue-300 mb-3 md:mb-0">Entity List</h2>
              
              <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3 w-full md:w-auto">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search entities..."
                  className="px-3 py-2 bg-gray-750 border border-gray-700 rounded text-gray-300 focus:outline-none focus:border-blue-500"
                />
                
                <select
                  value={filterTypeId}
                  onChange={(e) => setFilterTypeId(e.target.value)}
                  className="px-3 py-2 bg-gray-750 border border-gray-700 rounded text-gray-300 focus:outline-none focus:border-blue-500"
                >
                  <option value="">All Types</option>
                  {entityTypes.map(type => (
                    <option key={type.id} value={type.id}>
                      {type.name}
                    </option>
                  ))}
                </select>
                
                {(searchTerm || filterTypeId) && (
                  <button
                    onClick={handleClearFilters}
                    className="px-3 py-2 bg-gray-750 text-gray-300 hover:text-blue-300 rounded border border-gray-700"
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>
            
            <div className="flex justify-between items-center mb-4">
              {/* Removed duplicate "Entity List" heading */}
              
              {filterTypeId && (
                <button
                  onClick={handleDeleteAllEntities}
                  className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded"
                >
                  Delete All
                </button>
              )}
            </div>
            
            {filteredEntities.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-400">No entities found.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredEntities
                  .filter(entity => entity && entity.id) // Extra validation filter
                  .map(entity => (
                    <EntityCard 
                      key={entity.id}
                      entity={entity}
                      isSelected={selectedEntityIds.includes(entity.id)}
                      onSelect={handleSelectEntity}
                      onEdit={handleEditEntity}
                      onDelete={handleDeleteEntity}
                    />
                  ))}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Entity Edit Modal */}
      {editingEntity && editingEntityType && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-blue-300 mb-4">
                Edit Entity: {editingEntity.name}
              </h2>
              
              <EntityForm 
                entity={editingEntity}
                entityType={editingEntityType}
                onSave={handleUpdateEntity}
                onCancel={() => {
                  setEditingEntity(null);
                  setEditingEntityType(null);
                }}
              />
            </div>
            
            <div className="bg-gray-850 px-6 py-4 border-t border-gray-700 flex justify-end">
              <button 
                onClick={() => {
                  setEditingEntity(null);
                  setEditingEntityType(null);
                }}
                className="px-4 py-2 border border-gray-600 rounded text-gray-300 hover:text-gray-200"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Delete Confirmation Modal */}
      {deleteConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg shadow-lg border border-gray-700 p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold text-red-400 mb-4">Confirm Deletion</h3>
            
            <p className="text-gray-300 mb-6">
              {deleteConfirmation.isAll 
                ? `Are you sure you want to delete ALL entities of type "${deleteConfirmation.typeName}"? This action cannot be undone.`
                : `Are you sure you want to delete "${deleteConfirmation.name}"? This action cannot be undone.`}
            </p>
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={cancelDelete}
                className="px-4 py-2 border border-gray-600 rounded text-gray-300 hover:border-gray-500 hover:text-gray-200"
                disabled={deleting}
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded flex items-center"
                disabled={deleting}
              >
                {deleting ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Deleting...
                  </>
                ) : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Detail Modal */}
      {viewingEntity && (
        <EntityDetail 
          entity={viewingEntity} 
          onClose={() => setViewingEntity(null)}
        />
      )}
    </div>
  );
};

export default EntityList; 