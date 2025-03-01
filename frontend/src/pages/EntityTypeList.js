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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('entity-types');
  
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch entity types and templates when the component mounts
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch entity types
        const entityTypeResponse = await entityTypeApi.getAll();
        if (entityTypeResponse.status === 'success') {
          setEntityTypes(entityTypeResponse.data || []);
        } else {
          console.error('Error fetching entity types:', entityTypeResponse.message);
        }
        
        // Fetch templates
        const templateResponse = await templateApi.getAll();
        if (templateResponse.status === 'success') {
          setTemplates(templateResponse.data || []);
        } else {
          console.error('Error fetching templates:', templateResponse.message);
        }
      } catch (err) {
        setError('Failed to load data. Please try again later.');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const handleEntityTypeSelect = (id) => {
    navigate(`/entity-types/${id}`);
  };

  const handleTemplateSelect = (id) => {
    navigate(`/templates/${id}`);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Entity Types</h1>
        <Link 
          to="/entity-types/create" 
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded"
        >
          Create New Entity Type
        </Link>
      </div>
      
      {/* Tabs */}
      <div className="mb-6 border-b">
        <ul className="flex flex-wrap -mb-px text-sm font-medium text-center">
          <li className="mr-2">
            <button
              className={`inline-block p-4 border-b-2 rounded-t-lg ${
                activeTab === 'entity-types' 
                  ? 'border-blue-600 text-blue-600' 
                  : 'border-transparent hover:text-gray-600 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab('entity-types')}
            >
              Your Entity Types
            </button>
          </li>
          <li className="mr-2">
            <button
              className={`inline-block p-4 border-b-2 rounded-t-lg ${
                activeTab === 'templates' 
                  ? 'border-blue-600 text-blue-600' 
                  : 'border-transparent hover:text-gray-600 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab('templates')}
            >
              Predefined Templates
            </button>
          </li>
        </ul>
      </div>
      
      {/* Content */}
      {loading ? (
        <div className="text-center py-8">
          <p>Loading...</p>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <p>{error}</p>
        </div>
      ) : (
        <div>
          {activeTab === 'entity-types' && (
            <>
              {entityTypes.length > 0 ? (
                <div>
                  {entityTypes.map((entityType) => (
                    <EntityTypeCard 
                      key={entityType.id} 
                      entityType={entityType} 
                      onSelect={handleEntityTypeSelect} 
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500 mb-4">You haven't created any entity types yet.</p>
                  <div className="flex flex-col items-center justify-center">
                    <Link 
                      to="/entity-types/create" 
                      className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded mb-3"
                    >
                      Create from Scratch
                    </Link>
                    <button 
                      className="text-blue-600 hover:text-blue-800 font-medium"
                      onClick={() => setActiveTab('templates')}
                    >
                      Or start from a template
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
          
          {activeTab === 'templates' && (
            <>
              <p className="text-gray-600 mb-4">
                Start with a predefined template and customize it to your needs.
              </p>
              <div>
                {templates.map((template) => (
                  <TemplateCard 
                    key={template.id} 
                    template={template} 
                    onSelect={handleTemplateSelect} 
                  />
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default EntityTypeList; 