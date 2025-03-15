import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import { batchSimulationApi, unifiedSimulationApi } from '../services/api';
import LoadingIndicator from '../components/LoadingIndicator';

const BatchSimulationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  // Get active tab from location state, default to batch
  const activeTab = location.state?.activeTab || 'batch';
  
  const [batchSimulation, setBatchSimulation] = useState(null);
  const [componentSimulations, setComponentSimulations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [exportFormat, setExportFormat] = useState('json');
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [exportError, setExportError] = useState(null);

  useEffect(() => {
    const fetchBatchSimulation = async () => {
      try {
        setLoading(true);
        // Fetch the batch simulation details
        const batchData = await batchSimulationApi.getById(id);
        console.log('Batch simulation details:', batchData);
        
        // Handle different response formats from the API
        const batchSimulationData = batchData?.data || batchData;
        
        if (!batchSimulationData || !batchSimulationData.id) {
          console.error('Invalid batch simulation data:', batchData);
          setError('Failed to load batch simulation: Invalid data received');
          setLoading(false);
          return;
        }
        
        // Extract simulations first so we can use them to calculate missing fields
        const simulations = batchSimulationData.simulations || [];
        
        // Calculate missing fields from simulations data
        const derivedData = {
          // Calculate interaction_size from the first simulation (number of entities)
          interaction_size: simulations.length > 0 ? simulations[0].entity_ids.length : null,
          
          // Get n_turns from the first simulation's metadata
          n_turns: simulations.length > 0 && simulations[0].metadata ? 
            simulations[0].metadata.n_turns || null : null,
          
          // Count the number of simulations
          num_simulations: simulations.length,
          
          // Get simulation_rounds from the first simulation's metadata
          simulation_rounds: simulations.length > 0 && simulations[0].metadata ? 
            simulations[0].metadata.simulation_rounds || 1 : 1
        };
        
        // Extract fields from metadata if they're not at the top level
        const metadata = batchSimulationData.metadata || {};
        const enhancedBatchData = {
          ...batchSimulationData,
          interaction_size: batchSimulationData.interaction_size || metadata.interaction_size || derivedData.interaction_size,
          n_turns: batchSimulationData.n_turns || metadata.n_turns || derivedData.n_turns,
          num_simulations: batchSimulationData.num_simulations || metadata.num_simulations || derivedData.num_simulations,
          simulation_rounds: batchSimulationData.simulation_rounds || metadata.simulation_rounds || derivedData.simulation_rounds,
          metadata: metadata
        };
        
        console.log('Enhanced batch data:', enhancedBatchData);
        setBatchSimulation(enhancedBatchData);
        
        if (simulations.length > 0) {
          console.log('Using simulations from batch data:', simulations.length);
          setComponentSimulations(simulations);
          setLoading(false);
          return;
        }
        
        // Fetch all component simulations that are part of this batch if not included
        console.log('Fetching component simulations for batch:', id);
        const simulationsResponse = await unifiedSimulationApi.getAll({
          batchId: id,
          limit: 100, // Set a reasonable limit
        });
        
        console.log('Component simulations response:', simulationsResponse);
        const simulationsData = simulationsResponse?.data || simulationsResponse || [];
        
        if (Array.isArray(simulationsData)) {
          setComponentSimulations(simulationsData);
        } else {
          console.error('Invalid component simulations data:', simulationsData);
          setComponentSimulations([]);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching batch simulation:', err);
        setError(err.message || 'Failed to fetch batch simulation');
        setLoading(false);
      }
    };

    fetchBatchSimulation();
  }, [id]);

  const handleDelete = async () => {
    try {
      setLoading(true);
      await batchSimulationApi.delete(id);
      setLoading(false);
      // Navigate back to the simulation list
      navigate('/simulations', {
        state: { 
          message: 'Batch simulation deleted successfully',
          activeTab: 'batch'  // Always go back to batch tab when deleting a batch
        }
      });
    } catch (err) {
      console.error('Error deleting batch simulation:', err);
      setError(err.message || 'Failed to delete batch simulation');
      setLoading(false);
    }
  };

  const handleExport = (format) => {
    console.log(`Starting export using form submission for format: ${format}`);
    setExportLoading(true);
    
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
        setExportLoading(false);
        setExportModalOpen(false);
      }, 1000);
    } catch (error) {
      console.error('Error during export:', error);
      setExportError(`Export failed: ${error.message}`);
      setExportLoading(false);
    }
  };

  if (loading) {
    return <LoadingIndicator />;
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4" role="alert">
          <p className="font-bold">Error</p>
          <p>{error}</p>
        </div>
        <button
          onClick={() => navigate('/simulations', { state: { activeTab } })}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Back to Simulations
        </button>
      </div>
    );
  }

  if (!batchSimulation) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4" role="alert">
          <p className="font-bold">Not Found</p>
          <p>Batch simulation not found</p>
        </div>
        <button
          onClick={() => navigate('/simulations', { state: { activeTab } })}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Back to Simulations
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-3xl font-bold text-blue-300">
          Batch Simulation: {batchSimulation.name}
        </h1>
        <div className="space-x-2">
          <button
            onClick={() => navigate('/simulations', { state: { activeTab: 'batch' } })}
            className="border border-gray-600 text-gray-300 hover:text-white hover:bg-gray-700 py-2 px-4 rounded-md transition-colors"
          >
            Back
          </button>
          <button
            onClick={() => setExportModalOpen(true)}
            className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
          >
            Export
          </button>
          <button
            onClick={() => setDeleteConfirmOpen(true)}
            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
          >
            Delete
          </button>
        </div>
      </div>

      {/* Batch Details */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-blue-300 mb-4">Batch Details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-gray-400">Description:</p>
            <p className="text-white">{batchSimulation.description || 'No description'}</p>
          </div>
          <div>
            <p className="text-gray-400">Status:</p>
            <p className="text-white">{batchSimulation.status}</p>
          </div>
          <div>
            <p className="text-gray-400">Created:</p>
            <p className="text-white">{new Date(batchSimulation.created_at).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-gray-400">Interaction Size:</p>
            <p className="text-white">{batchSimulation.interaction_size || '-'}</p>
          </div>
          <div>
            <p className="text-gray-400">Number of Turns:</p>
            <p className="text-white">{batchSimulation.n_turns || '-'}</p>
          </div>
          <div>
            <p className="text-gray-400">Number of Simulations:</p>
            <p className="text-white">{batchSimulation.num_simulations || '-'}</p>
          </div>
          <div>
            <p className="text-gray-400">Number of Rounds:</p>
            <p className="text-white">{batchSimulation.simulation_rounds || 1}</p>
          </div>
          <div>
            <p className="text-gray-400">Interaction Type:</p>
            <p className="text-white">{(batchSimulation.metadata && batchSimulation.metadata.interaction_type) || 'discussion'}</p>
          </div>
          <div>
            <p className="text-gray-400">Language:</p>
            <p className="text-white">{(batchSimulation.metadata && batchSimulation.metadata.language) || 'English'}</p>
          </div>
        </div>
      </div>

      {/* Context */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-blue-300 mb-4">Context</h2>
        <div className="whitespace-pre-wrap text-white bg-gray-700 p-4 rounded">
          {batchSimulation.context || 'No context provided'}
        </div>
      </div>

      {/* Component Simulations */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-blue-300 mb-4">Component Simulations</h2>
        
        {componentSimulations.length === 0 ? (
          <p className="text-gray-400">No component simulations found</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-gray-700 rounded-lg">
              <thead>
                <tr className="bg-gray-600 text-left">
                  <th className="px-4 py-2 text-blue-300">ID</th>
                  <th className="px-4 py-2 text-blue-300">Name</th>
                  <th className="px-4 py-2 text-blue-300">Status</th>
                  <th className="px-4 py-2 text-blue-300">Created</th>
                  <th className="px-4 py-2 text-blue-300">Actions</th>
                </tr>
              </thead>
              <tbody>
                {componentSimulations.map((sim) => (
                  <tr key={sim.id} className="border-t border-gray-600 hover:bg-gray-650">
                    <td className="px-4 py-2 text-white">{sim.id.substring(0, 8)}...</td>
                    <td className="px-4 py-2 text-white">{sim.name || 'No name'}</td>
                    <td className="px-4 py-2 text-white">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        sim.status === 'completed' || (sim.metadata && sim.metadata.status === 'completed') ? 'bg-green-900 text-green-300' :
                        sim.status === 'error' || (sim.metadata && sim.metadata.status === 'error') ? 'bg-red-900 text-red-300' :
                        sim.status === 'in_progress' || (sim.metadata && sim.metadata.status === 'in_progress') ? 'bg-blue-900 text-blue-300' :
                        'bg-green-900 text-green-300' // Default to completed (green) if no status
                      }`}>
                        {sim.status || (sim.metadata && sim.metadata.status) || 'Completed'}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-white">
                      {sim.created_at ? new Date(sim.created_at).toLocaleString() : 
                       sim.timestamp ? new Date(sim.timestamp).toLocaleString() : 'Unknown'}
                    </td>
                    <td className="px-4 py-2">
                      <Link
                        to={`/simulations/${sim.id}`}
                        state={{ 
                          fromBatch: true, 
                          batchId: batchSimulation.id,
                          batchName: batchSimulation.name,
                          activeTab: 'individual' 
                        }}
                        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-3 rounded text-sm"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirmOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-semibold text-blue-300 mb-4">Confirm Deletion</h3>
            <p className="text-white mb-6">
              Are you sure you want to delete this batch simulation? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setDeleteConfirmOpen(false)}
                className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Export Modal */}
      {exportModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-semibold text-blue-300 mb-4">Export Batch Simulation</h3>
            <div className="mb-4">
              <label className="block text-gray-300 mb-2">Format</label>
              <select
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value)}
                className="block w-full p-2 bg-gray-700 border border-gray-600 rounded text-white"
              >
                <option value="json">JSON</option>
                <option value="csv">CSV</option>
              </select>
            </div>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setExportModalOpen(false)}
                className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded"
              >
                Cancel
              </button>
              <button
                onClick={() => handleExport(exportFormat)}
                className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
              >
                Export
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BatchSimulationDetail; 