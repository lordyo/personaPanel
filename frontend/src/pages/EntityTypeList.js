import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { entityTypeApi, templateApi } from '../services/api';
import EntityTypeCard from '../components/EntityTypeCard';
import TemplateCard from '../components/TemplateCard';

/**
 * Page component for listing entity types and templates.
 * 
 * @returns {JSX.Element} - Rendered component
 */
const EntityTypeList = () => {
  const [entityTypes, setEntityTypes] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [activeTab, setActiveTab] = useState('entityTypes');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [templatesError, setTemplatesError] = useState(null);
  const [deleteConfirmation, setDeleteConfirmation] = useState(null); // {id, name, type} where type is 'entityType' or 'template'
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch entity types
    const fetchEntityTypes = async () => {
      setIsLoading(true);
      try {
        console.log("Fetching entity types...");
        const response = await entityTypeApi.getAll();
        console.log("Entity types response:", response);
        if (response && response.status === 'success') {
          setEntityTypes(response.data || []);
          setError(null);
        } else {
          console.error('Error fetching entity types:', response?.message || 'Unknown error');
          setError(`Entity types: ${response?.message || 'Failed to load data'}`);
          setEntityTypes([]);
        }
      } catch (err) {
        console.error("Error fetching entity types:", err);
        setError(`Failed to load entity types: ${err.message || 'Please try again later.'}`);
        setEntityTypes([]);
      } finally {
        setIsLoading(false);
      }
    };

    // Fetch templates
    const fetchTemplates = async () => {
      setIsLoading(true);
      try {
        console.log("Fetching templates...");
        const response = await templateApi.getAll();
        console.log("Templates response:", response);
        if (response && response.status === 'success') {
          setTemplates(response.data || []);
          setTemplatesError(null);
        } else {
          console.error('Error fetching templates:', response?.message || 'Unknown error');
          setTemplatesError(`Templates: ${response?.message || 'Failed to load data'}`);
          setTemplates([]);
        }
      } catch (err) {
        console.error("Error fetching templates:", err);
        setTemplatesError(`Failed to load templates: ${err.message || 'Please try again later.'}`);
        setTemplates([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchEntityTypes();
    fetchTemplates();
  }, []);

  const handleCreateEntityType = () => {
    navigate('/entity-types/create');
  };

  const handleTemplateSelect = (templateId) => {
    navigate(`/templates/${templateId}`);
  };

  const handleEntityTypeSelect = (entityTypeId) => {
    navigate(`/entity-types/${entityTypeId}`);
  };

  const handleDeleteEntityType = (entityTypeId) => {
    const entityTypeToDelete = entityTypes.find(et => et.id === entityTypeId);
    if (entityTypeToDelete) {
      setDeleteConfirmation({
        id: entityTypeId,
        name: entityTypeToDelete.name || 'Unnamed Entity Type',
        type: 'entityType'
      });
    }
  };

  const handleDeleteTemplate = (templateId) => {
    const templateToDelete = templates.find(t => t.id === templateId);
    if (templateToDelete) {
      setDeleteConfirmation({
        id: templateId,
        name: templateToDelete.name || 'Unnamed Template',
        type: 'template'
      });
    }
  };

  const confirmDelete = async () => {
    if (!deleteConfirmation) return;
    
    try {
      setDeleting(true);
      
      if (deleteConfirmation.type === 'entityType') {
        // Delete the entity type
        await entityTypeApi.delete(deleteConfirmation.id);
        
        // Remove the entity type from state
        setEntityTypes(prev => prev.filter(et => et.id !== deleteConfirmation.id));
      } else if (deleteConfirmation.type === 'template') {
        // Delete the template
        await templateApi.delete(deleteConfirmation.id);
        
        // Remove the template from state
        setTemplates(prev => prev.filter(t => t.id !== deleteConfirmation.id));
      }
      
      // Clear error if any
      setError(null);
    } catch (err) {
      console.error("Error deleting:", err);
      setError(`Failed to delete ${deleteConfirmation.type}. ${err.message || ""}`);
    } finally {
      setDeleting(false);
      setDeleteConfirmation(null);
    }
  };
  
  const cancelDelete = () => {
    setDeleteConfirmation(null);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-blue-400">Entity Types</h1>
          <button 
            onClick={handleCreateEntityType}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md shadow-md transition-colors"
            data-testid="create-entity-type-button"
          >
            Create New Entity Type
          </button>
        </div>
        
        {/* Tabs */}
        <div className="mb-6 border-b border-gray-700">
          <nav className="flex space-x-8">
            <button
              className={`py-3 px-1 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'entityTypes'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-600'
              }`}
              onClick={() => setActiveTab('entityTypes')}
              data-testid="entity-types-tab"
            >
              Your Entity Types
            </button>
            <button
              className={`py-3 px-1 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'templates'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-600'
              }`}
              onClick={() => setActiveTab('templates')}
              data-testid="templates-tab"
            >
              Predefined Templates
            </button>
          </nav>
        </div>
        
        {/* Delete Confirmation Modal */}
        {deleteConfirmation && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 border border-gray-700 p-6 rounded-lg shadow-xl max-w-md w-full">
              <h3 className="text-xl font-bold text-red-400 mb-4">Delete Confirmation</h3>
              <p className="text-gray-300 mb-6">
                Are you sure you want to delete the {deleteConfirmation.type === 'entityType' ? 'entity type' : 'template'} "{deleteConfirmation.name}"? 
                This action cannot be undone.
              </p>
              <div className="flex justify-end gap-3">
                <button
                  className="px-4 py-2 text-gray-300 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors"
                  onClick={cancelDelete}
                  disabled={deleting}
                >
                  Cancel
                </button>
                <button
                  className="px-4 py-2 text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors flex items-center gap-2"
                  onClick={confirmDelete}
                  disabled={deleting}
                >
                  {deleting ? (
                    <>
                      <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Deleting...
                    </>
                  ) : (
                    'Delete'
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* Content area */}
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
          </div>
        ) : activeTab === 'entityTypes' ? (
          <div>
            {error ? (
              <div className="bg-red-900/30 border border-red-800 text-red-300 p-4 rounded-md mb-6">
                {error}
              </div>
            ) : entityTypes.length === 0 ? (
              <div className="text-center py-12 bg-gray-800/50 rounded-lg border border-gray-700">
                <p className="text-gray-400 mb-4">You haven't created any entity types yet.</p>
                <button 
                  onClick={handleCreateEntityType}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md shadow transition-colors"
                >
                  Create Your First Entity Type
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {entityTypes.map(entityType => (
                  <EntityTypeCard 
                    key={entityType.id} 
                    entityType={entityType} 
                    onView={handleEntityTypeSelect}
                    onDelete={handleDeleteEntityType}
                  />
                ))}
              </div>
            )}
          </div>
        ) : (
          <div>
            {templatesError ? (
              <div className="bg-gray-800/70 border border-gray-700 rounded-lg p-6 shadow-lg">
                <div className="flex items-center mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-yellow-500 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <h3 className="text-xl font-medium text-yellow-400">Template Service Unavailable</h3>
                </div>
                <p className="text-gray-300 mb-4">{templatesError}</p>
                <p className="text-gray-400 text-sm">You can still create custom entity types or try again later.</p>
              </div>
            ) : templates.length === 0 ? (
              <div className="text-center py-12 bg-gray-800/50 rounded-lg border border-gray-700">
                <p className="text-gray-400">No templates available at this time.</p>
              </div>
            ) : (
              <div>
                <p className="text-gray-300 mb-6">Use these predefined templates to quickly create common entity types.</p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {templates.map(template => (
                    <TemplateCard 
                      key={template.id} 
                      template={template} 
                      onSelect={handleTemplateSelect}
                      onDelete={handleDeleteTemplate}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EntityTypeList; 