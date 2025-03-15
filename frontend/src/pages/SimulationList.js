import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { unifiedSimulationApi, batchSimulationApi } from '../services/api';
import LoadingIndicator from '../components/LoadingIndicator';

/**
 * Page for viewing saved simulations
 */
const SimulationList = () => {
  const [simulations, setSimulations] = useState([]);
  const [batchSimulations, setBatchSimulations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [batchLoading, setBatchLoading] = useState(true);
  const [error, setError] = useState(null);
  const [batchError, setBatchError] = useState(null);
  const [deleteInProgress, setDeleteInProgress] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  // Filter for showing batch simulations
  const [showBatchSims, setShowBatchSims] = useState(() => {
    const savedFilter = localStorage.getItem('showBatchSimulations');
    return savedFilter === 'true'; // Default to false if not set
  });
  
  // Save filter preference
  useEffect(() => {
    localStorage.setItem('showBatchSimulations', showBatchSims);
  }, [showBatchSims]);
  
  // Initialize activeTab from localStorage or URL params, defaulting to 'individual'
  const [activeTab, setActiveTab] = useState(() => {
    // Check if tab is specified in URL params
    const params = new URLSearchParams(location.search);
    const tabParam = params.get('tab');
    
    if (tabParam === 'batch' || tabParam === 'individual') {
      return tabParam;
    }
    
    // Check location state
    if (location.state?.activeTab === 'batch' || location.state?.activeTab === 'individual') {
      return location.state.activeTab;
    }
    
    // Check localStorage
    const savedTab = localStorage.getItem('simulationListActiveTab');
    if (savedTab === 'batch' || savedTab === 'individual') {
      return savedTab;
    }
    
    // Default to individual
    return 'individual';
  });
  
  // Pagination
  const [limit, setLimit] = useState(20);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  
  // Pagination for batches
  const [batchLimit, setBatchLimit] = useState(20);
  const [batchOffset, setBatchOffset] = useState(0);
  const [batchHasMore, setBatchHasMore] = useState(false);

  // Save tab selection to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('simulationListActiveTab', activeTab);
    
    // Update URL with tab parameter
    const params = new URLSearchParams(location.search);
    params.set('tab', activeTab);
    
    // Update URL without triggering navigation
    const newUrl = `${location.pathname}?${params.toString()}`;
    window.history.replaceState(null, '', newUrl);
  }, [activeTab, location.pathname]);

  useEffect(() => {
    // Check for notification message from location state
    if (location.state?.message) {
      const timer = setTimeout(() => {
        // Preserve activeTab when clearing message
        navigate(location.pathname, { 
          replace: true, 
          state: { activeTab: location.state?.activeTab || activeTab } 
        });
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [location, navigate, activeTab]);

  // Handle tab changes
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    
    // Update URL with new tab
    navigate(`/simulations?tab=${tab}`, { 
      replace: true,
      state: { activeTab: tab }
    });
  };

  useEffect(() => {
    const fetchSimulations = async () => {
      try {
        setLoading(true);
        
        // Build query parameters
        const params = { 
          limit, 
          offset,
          // Only include batch simulations if the filter is enabled
          includeBatchSims: showBatchSims
        };
        
        const response = await unifiedSimulationApi.getAll(params);
        if (response && response.status === 'success') {
          setSimulations(response.data || []);
          // Check if there are more results
          setHasMore(response.data?.length === limit);
          setError(null);
        } else {
          console.error('Error fetching simulations:', response?.message || 'Unknown error');
          setError(response?.message || 'Failed to load simulations');
          setSimulations([]);
        }
        setLoading(false);
      } catch (err) {
        console.error("Error fetching simulations:", err);
        setError("Failed to load simulations. Please try again later.");
        setSimulations([]);
        setLoading(false);
      }
    };

    // Only fetch individual simulations when that tab is active or on first load
    if (activeTab === 'individual') {
      fetchSimulations();
    }
  }, [limit, offset, activeTab, showBatchSims]);

  useEffect(() => {
    const fetchBatchSimulations = async () => {
      try {
        setBatchLoading(true);
        
        // Build query parameters
        const params = { limit: batchLimit, offset: batchOffset };
        
        const response = await batchSimulationApi.getAll(params);
        if (response && response.status === 'success') {
          setBatchSimulations(response.data || []);
          // Check if there are more results
          setBatchHasMore(response.data?.length === batchLimit);
          setBatchError(null);
        } else {
          console.error('Error fetching batch simulations:', response?.message || 'Unknown error');
          setBatchError(response?.message || 'Failed to load batch simulations');
          setBatchSimulations([]);
        }
        setBatchLoading(false);
      } catch (err) {
        console.error("Error fetching batch simulations:", err);
        setBatchError("Failed to load batch simulations. Please try again later.");
        setBatchSimulations([]);
        setBatchLoading(false);
      }
    };

    // Only fetch batch simulations when that tab is active
    if (activeTab === 'batch') {
      fetchBatchSimulations();
    }
  }, [batchLimit, batchOffset, activeTab]);

  const handleViewSimulation = (id) => {
    navigate(`/simulations/${id}`, {
      state: { activeTab }
    });
  };
  
  const handleViewBatchSimulation = (id) => {
    navigate(`/batch-simulations/${id}`, {
      state: { activeTab }
    });
  };
  
  const handleCreateSimulation = () => {
    navigate('/simulations/create', {
      state: { activeTab }
    });
  };
  
  const handleCreateBatchSimulation = () => {
    navigate('/batch-simulations/create', {
      state: { activeTab }
    });
  };
  
  const handleContinueSimulation = (simulation) => {
    navigate('/simulations/create', { 
      state: { 
        continuationData: {
          id: simulation.id,
          name: simulation.name,
          entities: simulation.entity_ids,
          context: simulation.context_id,
          turns: simulation.final_turn_number || 0
        },
        activeTab
      }
    });
  };
  
  const handleDeleteSimulation = async (id) => {
    if (window.confirm('Are you sure you want to delete this simulation? This action cannot be undone.')) {
      try {
        setDeleteInProgress(true);
        const response = await unifiedSimulationApi.delete(id);
        
        if (response && response.status === 'success') {
          // Remove the deleted simulation from the list
          setSimulations(simulations.filter(sim => sim.id !== id));
          
          // Show success message
          navigate(location.pathname, { 
            replace: true, 
            state: { 
              message: 'Simulation deleted successfully',
              activeTab
            } 
          });
        } else {
          console.error('Error deleting simulation:', response?.message || 'Unknown error');
          setError(response?.message || 'Failed to delete simulation');
        }
        setDeleteInProgress(false);
      } catch (err) {
        console.error("Error deleting simulation:", err);
        setError("Failed to delete simulation. Please try again later.");
        setDeleteInProgress(false);
      }
    }
  };
  
  const handleDeleteBatchSimulation = async (id) => {
    if (window.confirm('Are you sure you want to delete this batch simulation? This action cannot be undone.')) {
      try {
        setDeleteInProgress(true);
        const response = await batchSimulationApi.delete(id);
        
        if (response && response.status === 'success') {
          // Remove the deleted simulation from the list
          setBatchSimulations(batchSimulations.filter(batch => batch.id !== id));
          
          // Show success message
          navigate(location.pathname, { 
            replace: true, 
            state: { 
              message: 'Batch simulation deleted successfully',
              activeTab
            } 
          });
        } else {
          console.error('Error deleting batch simulation:', response?.message || 'Unknown error');
          setBatchError(response?.message || 'Failed to delete batch simulation');
        }
        setDeleteInProgress(false);
      } catch (err) {
        console.error("Error deleting batch simulation:", err);
        setBatchError("Failed to delete batch simulation. Please try again later.");
        setDeleteInProgress(false);
      }
    }
  };
  
  const handleExportBatchSimulation = (id, format = 'json') => {
    console.log(`Starting export using form submission for batch ID: ${id}, format: ${format}`);
    
    try {
      // Create a hidden form element
      const form = document.createElement('form');
      form.method = 'POST';
      
      // Get current location components
      const currentProtocol = window.location.protocol;
      const currentHost = window.location.hostname;
      const currentPort = window.location.port || (currentProtocol === 'https:' ? '443' : '80');
      
      // Determine base URL for the API
      let apiBaseUrl;
      
      // First check environment variable
      if (process.env.REACT_APP_API_URL) {
        apiBaseUrl = process.env.REACT_APP_API_URL;
      } 
      // If running on the same host but different port, assume backend is on port 5000
      else if (currentPort !== '5000') {
        apiBaseUrl = `${currentProtocol}//${currentHost}:5000`;
      } 
      // If already on port 5000, use the current origin
      else {
        apiBaseUrl = window.location.origin;
      }
      
      // Remove trailing slash if any
      const baseUrl = apiBaseUrl.endsWith('/') ? apiBaseUrl.slice(0, -1) : apiBaseUrl;
      
      // Construct the final URL - check if baseUrl already includes /api
      const hasApiPrefix = baseUrl.endsWith('/api') || baseUrl.includes('/api/');
      const apiPath = hasApiPrefix ? '' : '/api';
      form.action = `${baseUrl}${apiPath}/batch-simulations/${id}/export`;
      
      console.log(`Export form action URL: ${form.action}`);
      form.target = '_blank'; // Open in a new tab

      // Add format parameter
      const formatInput = document.createElement('input');
      formatInput.type = 'hidden';
      formatInput.name = 'format';
      formatInput.value = format;
      form.appendChild(formatInput);

      // Add the form to the document and submit it
      document.body.appendChild(form);
      console.log('Submitting form for export...');
      form.submit();
      
      // Clean up the form
      setTimeout(() => {
        document.body.removeChild(form);
      }, 1000);
    } catch (error) {
      console.error('Error during export:', error);
      setError(`Export failed: ${error.message}`);
    }
  };
  
  const loadMore = () => {
    setOffset(prev => prev + limit);
  };
  
  const loadMoreBatches = () => {
    setBatchOffset(prev => prev + batchLimit);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    try {
      return new Date(dateString).toLocaleString();
    } catch (error) {
      console.error('Error formatting date:', error, 'Date string was:', dateString);
      return 'Invalid date format';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-blue-300">
          Simulations
        </h1>
      </div>
      
      {/* Tabs */}
      <div className="mb-6 border-b border-gray-700">
        <nav className="flex space-x-8">
          <button
            className={`py-3 px-1 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'individual'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-600'
            }`}
            onClick={() => handleTabChange('individual')}
            data-testid="individual-simulations-tab"
          >
            Individual Simulations
          </button>
          <button
            className={`py-3 px-1 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'batch'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-600'
            }`}
            onClick={() => handleTabChange('batch')}
            data-testid="batch-simulations-tab"
          >
            Batch Simulations
          </button>
        </nav>
      </div>
      
      {location.state?.message && (
        <div className="mb-6 p-4 bg-green-600 bg-opacity-10 border border-green-500 rounded-lg text-green-400">
          {location.state.message}
        </div>
      )}
      
      {/* Individual Simulations Tab Content */}
      {activeTab === 'individual' && (
        <>
          {error && (
            <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
              {error}
            </div>
          )}
          
          <div className="mb-6 flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h2 className="text-xl font-semibold text-blue-300">Individual Simulations</h2>
              
              {/* Batch simulation filter toggle */}
              <div className="flex items-center">
                <label className="inline-flex items-center cursor-pointer">
                  <span className="text-sm text-gray-300 mr-2">Show batch sims</span>
                  <div className="relative">
                    <input 
                      type="checkbox" 
                      className="sr-only peer" 
                      checked={showBatchSims} 
                      onChange={() => setShowBatchSims(!showBatchSims)}
                    />
                    <div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-gray-300 after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </div>
                </label>
              </div>
            </div>
            
            <button 
              className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
              onClick={handleCreateSimulation}
            >
              Create New Simulation
            </button>
          </div>
          
          {loading ? (
            <div className="flex justify-center items-center py-8">
              <LoadingIndicator />
            </div>
          ) : simulations.length === 0 ? (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 text-center">
              <h2 className="text-xl font-semibold text-blue-300 mb-2">
                No Simulations Found
              </h2>
              <p className="text-gray-300 mb-4">
                You haven't created any individual simulations yet. Create your first simulation to get started.
              </p>
              <button 
                className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
                onClick={handleCreateSimulation}
              >
                Create New Simulation
              </button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {simulations.map((simulation) => (
                  <div 
                    key={simulation.id}
                    className="border border-gray-700 rounded-lg overflow-hidden bg-gray-800 hover:bg-gray-750 transition-all duration-300 shadow-lg hover:shadow-xl flex flex-col h-full"
                  >
                    <div className="p-5 flex-grow">
                      <h3 className="text-xl font-semibold text-blue-300 mb-1 truncate">
                        {simulation.name || `Simulation ${simulation.id.slice(0, 8)}`}
                      </h3>
                      
                      <p className="text-gray-400 text-sm mb-3">
                        Created: {formatDate(simulation.created_at || simulation.timestamp)}
                      </p>
                      
                      <div className="flex mb-3 gap-2 flex-wrap">
                        <span className="bg-gray-700 text-gray-300 text-xs font-medium px-2.5 py-1 rounded-full">
                          {simulation.entity_ids?.length || 0} entities
                        </span>
                        
                        {/* Add tag showing if this is a batch or individual simulation */}
                        <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${
                          simulation.metadata?.batch_id 
                            ? 'bg-purple-900 text-purple-300' 
                            : 'bg-blue-900 text-blue-300'
                        }`}>
                          {simulation.metadata?.batch_id ? 'batch sim' : 'individual sim'}
                        </span>
                        
                        {simulation.final_turn_number && (
                          <span className="bg-gray-700 text-gray-300 text-xs font-medium px-2.5 py-1 rounded-full">
                            Turn {simulation.final_turn_number}
                          </span>
                        )}
                      </div>
                      
                      <p className="text-gray-300 mb-4 line-clamp-2 min-h-[3em]">
                        {simulation.context || "No context available"}
                      </p>
                    </div>
                    
                    <div className="border-t border-gray-700 p-3 flex justify-between items-center">
                      <div className="flex gap-2">
                        <button 
                          className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
                          onClick={() => handleViewSimulation(simulation.id)}
                        >
                          View
                        </button>
                        
                        <button 
                          className="text-red-400 hover:text-red-300 font-medium transition-colors"
                          onClick={() => handleDeleteSimulation(simulation.id)}
                          disabled={deleteInProgress}
                        >
                          Delete
                        </button>
                      </div>
                      
                      <button 
                        className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-1 px-3 rounded-md text-sm transition-colors"
                        onClick={() => handleContinueSimulation(simulation)}
                      >
                        Continue
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              
              {hasMore && (
                <div className="mt-8 text-center">
                  <button 
                    className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-2 px-4 rounded-md transition-colors"
                    onClick={loadMore}
                  >
                    Load More
                  </button>
                </div>
              )}
            </>
          )}
        </>
      )}
      
      {/* Batch Simulations Tab Content */}
      {activeTab === 'batch' && (
        <>
          {batchError && (
            <div className="mb-6 p-4 bg-red-400 bg-opacity-10 border border-red-400 rounded-lg text-red-400">
              {batchError}
            </div>
          )}
          
          <div className="mb-6 flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h2 className="text-xl font-semibold text-blue-300">Batch Simulations</h2>
            </div>
            
            <button 
              className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
              onClick={handleCreateBatchSimulation}
            >
              Create New Batch Simulation
            </button>
          </div>
          
          {batchLoading ? (
            <div className="flex justify-center items-center py-8">
              <LoadingIndicator />
            </div>
          ) : batchSimulations.length === 0 ? (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 text-center">
              <h2 className="text-xl font-semibold text-blue-300 mb-2">
                No Batch Simulations Found
              </h2>
              <p className="text-gray-300 mb-4">
                You haven't created any batch simulations yet. Create your first batch simulation to get started.
              </p>
              <button 
                className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors"
                onClick={handleCreateBatchSimulation}
              >
                Create New Batch Simulation
              </button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {batchSimulations.map((batch) => (
                  <div 
                    key={batch.id}
                    className="border border-gray-700 rounded-lg overflow-hidden bg-gray-800 hover:bg-gray-750 transition-all duration-300 shadow-lg hover:shadow-xl flex flex-col h-full"
                  >
                    <div className="p-5 flex-grow">
                      <h3 className="text-xl font-semibold text-blue-300 mb-1 truncate">
                        {batch.name || `Batch ${batch.id.slice(0, 8)}`}
                      </h3>
                      
                      <p className="text-gray-400 text-sm mb-3">
                        Created: {formatDate(batch.created_at || batch.timestamp)}
                      </p>
                      
                      <div className="flex mb-3 gap-2 flex-wrap">
                        <span className={`bg-gray-700 text-xs font-medium px-2.5 py-1 rounded-full
                          ${batch.status === 'completed' ? 'text-green-300' :
                            batch.status === 'partial' ? 'text-yellow-300' :
                            batch.status === 'failed' ? 'text-red-300' :
                            batch.status === 'in_progress' ? 'text-blue-300' : 'text-gray-300'}`}>
                          {batch.status?.charAt(0).toUpperCase() + batch.status?.slice(1) || "Unknown"}
                        </span>
                        
                        {batch.simulations && (
                          <span className="bg-gray-700 text-gray-300 text-xs font-medium px-2.5 py-1 rounded-full">
                            {batch.simulations.length} simulations
                          </span>
                        )}
                      </div>
                      
                      <p className="text-gray-300 mb-4 line-clamp-2 min-h-[3em]">
                        {batch.context || batch.description || "No description available"}
                      </p>
                    </div>
                    
                    <div className="border-t border-gray-700 p-3 flex justify-between items-center">
                      <div className="flex gap-2">
                        <button 
                          className="text-blue-400 hover:text-blue-300 font-medium transition-colors"
                          onClick={() => handleViewBatchSimulation(batch.id)}
                        >
                          View
                        </button>
                        
                        <button 
                          className="text-red-400 hover:text-red-300 font-medium transition-colors"
                          onClick={() => handleDeleteBatchSimulation(batch.id)}
                          disabled={deleteInProgress}
                        >
                          Delete
                        </button>
                      </div>
                      
                      <div className="flex gap-2">
                        <button 
                          className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-1 px-3 rounded-md text-sm transition-colors"
                          onClick={() => handleExportBatchSimulation(batch.id, 'json')}
                          title="Export as JSON"
                        >
                          Export
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              {batchHasMore && (
                <div className="mt-8 text-center">
                  <button 
                    className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-2 px-4 rounded-md transition-colors"
                    onClick={loadMoreBatches}
                  >
                    Load More
                  </button>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
};

export default SimulationList; 