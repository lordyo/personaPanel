import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import EntityCard from '../components/EntityCard';
import EntityForm from '../components/EntityForm';
import EntityGenerationForm from '../components/EntityGenerationForm';
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
  const [editingEntity, setEditingEntity] = useState(null);
  const [editingEntityType, setEditingEntityType] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generatingEntities, setGeneratingEntities] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTypeId, setFilterTypeId] = useState('');
  const [error, setError] = useState(null);
  
  // Fetch entity types and entities on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const typesResponse = await api.getEntityTypes();
        setEntityTypes(typesResponse.data);
        
        // Fetch all entities 
        const entitiesPromises = typesResponse.data.map(type => 
          api.getEntitiesByType(type.id)
        );
        
        const entitiesResponses = await Promise.all(entitiesPromises);
        const allEntities = entitiesResponses.flatMap(response => response.data);
        
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
    let filtered = [...entities];
    
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(entity => 
        entity.name.toLowerCase().includes(term) || 
        entity.entity_type_name.toLowerCase().includes(term)
      );
    }
    
    if (filterTypeId) {
      filtered = filtered.filter(entity => entity.entity_type_id === filterTypeId);
    }
    
    setFilteredEntities(filtered);
  }, [entities, searchTerm, filterTypeId]);
  
  const handleSelectEntity = (entityId) => {
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
      
      const response = await api.generateEntities(formData);
      
      if (response.status === 'success') {
        // Refresh the entities list
        const entityType = entityTypes.find(et => et.id === formData.entityTypeId);
        const newEntitiesResponse = await api.getEntitiesByType(formData.entityTypeId);
        
        // Add or replace entities of this type in our state
        setEntities(prev => {
          // Filter out entities of the same type
          const otherEntities = prev.filter(e => e.entity_type_id !== formData.entityTypeId);
          // Add the new entities
          return [...otherEntities, ...newEntitiesResponse.data];
        });
      } else {
        setError('Failed to generate entities: ' + response.message);
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
  
  if (loading && !entities.length) {
    return <LoadingIndicator message="Loading entities..." />;
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-blue-300">Entities</h1>
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
            
            {filteredEntities.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-400">No entities found.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredEntities.map(entity => (
                  <EntityCard 
                    key={entity.id}
                    entity={entity}
                    isSelected={selectedEntityIds.includes(entity.id)}
                    onSelect={handleSelectEntity}
                    onEdit={handleEditEntity}
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
    </div>
  );
};

export default EntityList; 