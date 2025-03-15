/**
 * API service for communicating with the backend.
 * Contains functions for making requests to the API endpoints.
 */

// Use environment variable if available, fallback to relative URL for proxy
const API_URL = process.env.REACT_APP_API_URL || '/api';
console.log('API_URL is:', API_URL);

/**
 * Make a GET request to the specified endpoint.
 * 
 * @param {string} endpoint - The API endpoint to request
 * @returns {Promise} - The response data or error
 */
async function get(endpoint) {
  let url = endpoint;
  // Ensure we have a proper URL by combining API_URL with endpoint
  if (!endpoint.startsWith('http') && !endpoint.startsWith('/')) {
    url = `${API_URL}/${endpoint}`;
  } else if (!endpoint.startsWith('http')) {
    url = `${API_URL}${endpoint}`;
  }
  
  console.log(`GET request to: ${url}`);
  
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache'
      },
      mode: 'cors',
      credentials: 'omit'  // Don't send credentials
    });
    
    if (!response.ok) {
      console.error(`API error for ${endpoint}: Status ${response.status}`);
      let errorText = '';
      try {
        errorText = await response.text();
        console.error(`Response body: ${errorText}`);
      } catch (e) {
        console.error(`Could not read response text: ${e.message}`);
      }
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    // Check if response is empty
    const text = await response.text();
    if (!text) {
      return { status: 'error', message: 'Empty response received from server' };
    }
    
    try {
      const data = JSON.parse(text);
      return data;
    } catch (e) {
      console.error(`JSON parse error for ${endpoint}:`, e);
      console.error(`Response text: ${text.substring(0, 200)}...`);
      return { status: 'error', message: 'Invalid JSON response from server' };
    }
  } catch (error) {
    console.error(`Error fetching from ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Make a POST request to the specified endpoint.
 * 
 * @param {string} endpoint - The API endpoint to request
 * @param {object} body - The data to send in the request body
 * @returns {Promise} - The response data or error
 */
async function post(endpoint, body) {
  let url = endpoint;
  // Ensure we have a proper URL by combining API_URL with endpoint
  if (!endpoint.startsWith('http') && !endpoint.startsWith('/')) {
    url = `${API_URL}/${endpoint}`;
  } else if (!endpoint.startsWith('http')) {
    url = `${API_URL}${endpoint}`;
  }
  
  console.log(`POST request to: ${url}`);
  console.log(`POST body: ${JSON.stringify(body, null, 2)}`);
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      mode: 'cors',
      credentials: 'omit',  // Don't send credentials
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    // Check if response is empty
    const text = await response.text();
    if (!text) {
      return { status: 'error', message: 'Empty response received from server' };
    }
    
    try {
      const data = JSON.parse(text);
      return data;
    } catch (parseError) {
      console.error('JSON parse error:', parseError);
      return { status: 'error', message: 'Invalid JSON response from server' };
    }
  } catch (error) {
    console.error(`Error posting to ${endpoint}:`, error);
    return { status: 'error', message: error.message || 'Unknown error occurred' };
  }
}

/**
 * Make a PUT request to the specified endpoint.
 * 
 * @param {string} endpoint - The API endpoint to request
 * @param {object} body - The data to send in the request body
 * @returns {Promise} - The response data or error
 */
async function put(endpoint, body) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      mode: 'cors',
      credentials: 'omit',  // Don't send credentials
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    // Check if response is empty
    const text = await response.text();
    if (!text) {
      return { status: 'error', message: 'Empty response received from server' };
    }
    
    try {
      const data = JSON.parse(text);
      return data;
    } catch (parseError) {
      console.error('JSON parse error:', parseError);
      return { status: 'error', message: 'Invalid JSON response from server' };
    }
  } catch (error) {
    console.error(`Error updating ${endpoint}:`, error);
    return { status: 'error', message: error.message || 'Unknown error occurred' };
  }
}

/**
 * Make a DELETE request to the specified endpoint.
 * 
 * @param {string} endpoint - The API endpoint to request
 * @returns {Promise} - The response data or error
 */
async function del(endpoint) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json',
      },
      mode: 'cors',
      credentials: 'omit',  // Don't send credentials
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    // Check if response is empty
    const text = await response.text();
    if (!text) {
      return { status: 'error', message: 'Empty response received from server' };
    }
    
    try {
      const data = JSON.parse(text);
      return data;
    } catch (parseError) {
      console.error('JSON parse error:', parseError);
      return { status: 'error', message: 'Invalid JSON response from server' };
    }
  } catch (error) {
    console.error(`Error deleting from ${endpoint}:`, error);
    return { status: 'error', message: error.message || 'Unknown error occurred' };
  }
}

// Entity Type Management
const entityTypeApi = {
  /**
   * Get all entity types.
   * 
   * @returns {Promise} - List of entity types
   */
  getAll: () => get('/entity-types'),
  
  /**
   * Get a specific entity type by id.
   * 
   * @param {string} id - The entity type id
   * @returns {Promise} - The entity type data
   */
  getById: (id) => get(`/entity-types/${id}`),
  
  /**
   * Create a new entity type.
   * 
   * @param {object} entityType - The entity type data to create
   * @returns {Promise} - The created entity type
   */
  create: (entityType) => post('/entity-types', entityType),
  
  /**
   * Update an existing entity type.
   * 
   * @param {string} id - The entity type id
   * @param {object} entityType - The updated entity type data
   * @returns {Promise} - The updated entity type
   */
  update: (id, entityType) => put(`/entity-types/${id}`, entityType),
  
  /**
   * Delete an entity type by ID.
   * 
   * @param {string} id - The entity type id to delete
   * @returns {Promise} - Response indicating success or failure
   */
  delete: (id) => del(`/entity-types/${id}`),

  /**
   * Suggest dimensions for an entity type using LLM.
   * 
   * @param {string} name - The entity type name
   * @param {string} description - The entity type description
   * @param {number} n_dimensions - Number of dimensions to generate (optional)
   * @returns {Promise} - The suggested dimensions
   */
  suggestDimensions: (name, description, n_dimensions = 5) => 
    post('/entity-types/suggest-dimensions', { name, description, n_dimensions }),
}

// Entity Management
const entityApi = {
  /**
   * Get a specific entity by id.
   * 
   * @param {string} id - The entity id
   * @returns {Promise} - The entity data
   */
  getById: (id) => get(`/entities/${id}`),
  
  /**
   * Get all entities for a specific entity type.
   * 
   * @param {string} entityTypeId - The entity type id
   * @returns {Promise} - List of entities
   */
  getByType: async (entityTypeId) => {
    try {
      const response = await get(`/entity-types/${entityTypeId}/entities`);
      
      // Extract entities from the response, handling both formats
      // API might return { status: "success", data: [...] } or just the array directly
      return response.data || response;
    } catch (error) {
      console.warn(`Error fetching entities for type ${entityTypeId}:`, error);
      // For corrupted entity types, return an empty array instead of propagating the error
      // This prevents the UI from breaking when a specific entity type has data issues
      return [];
    }
  },
  
  /**
   * Create a new entity.
   * 
   * @param {object} entity - The entity data to create
   * @returns {Promise} - The created entity
   */
  create: (entity) => post('/entities', entity),
  
  /**
   * Generate entities based on entity type.
   * 
   * @param {string} entityTypeId - The entity type id
   * @param {number} count - Number of entities to generate (1-20)
   * @param {number} variability - Variability level (0-1)
   * @param {string} entityDescription - Optional description to guide entity generation
   * @returns {Promise} - The generated entities
   */
  generateEntities: (entityTypeId, count = 1, variability = 0.5, entityDescription = '') => {
    return post('/entities', {
      entity_type_id: entityTypeId,
      generate: true,
      count: count,
      variability: variability,
      entity_description: entityDescription
    });
  },
  
  /**
   * Update an existing entity.
   * 
   * @param {string} id - The entity id
   * @param {object} entity - The updated entity data
   * @returns {Promise} - The updated entity
   */
  update: (id, entity) => put(`/entities/${id}`, entity),
  
  /**
   * Delete an entity by ID.
   * 
   * @param {string} id - The entity id to delete
   * @returns {Promise} - Response indicating success or failure
   */
  delete: (id) => del(`/entities/${id}`),
  
  /**
   * Delete all entities of a specific entity type.
   * 
   * @param {string} entityTypeId - The entity type id
   * @returns {Promise} - Response with count of deleted entities
   */
  deleteByType: (entityTypeId) => del(`/entity-types/${entityTypeId}/entities`),

  /**
   * Generate a batch of entities
   * 
   * @param {string} entityTypeId - ID of the entity type
   * @param {number} batchSize - Number of entities to generate
   * @param {number} variability - Variability level (0-1)
   * @param {string} entityDescription - Optional description to guide entity generation
   * @param {string} generationMethod - The generation method to use: 'multi-step' (default) or 'batch'
   * @returns {Promise} - The generated batch of entities
   */
  generateEntityBatch: (entityTypeId, batchSize = 5, variability = 0.7, entityDescription = '', generationMethod = 'multi-step') => {
    // Find the entity type to get its dimensions and other metadata
    return get(`/entity-types/${entityTypeId}`)
      .then(response => {
        // Extract the actual entity type data from the response
        // API returns { status: "success", data: {...} }
        const entityType = response.data || response;
        
        // Check if entity type exists
        if (!entityType) {
          throw new Error('Entity type not found');
        }
        
        // Check for dimensions
        if (!entityType.dimensions || !Array.isArray(entityType.dimensions) || entityType.dimensions.length === 0) {
          throw new Error('Entity type must have dimensions');
        }
        
        // Prepare data for batch generation
        const requestData = {
          entity_type: entityType.name,
          entity_description: entityDescription || entityType.description,
          dimensions: entityType.dimensions || [],
          batch_size: batchSize,
          variability: variability,
          output_fields: entityType.output_fields || [],
          generation_method: generationMethod // Add the generation method to the request
        };
        
        // The API_URL already includes "/api", so we don't need to add it again
        const endpoint = 'batch-entities/generate';
        return post(endpoint, requestData)
          .then(response => {
            // Return response as-is without wrapping in data
            // The batch API already includes status and entities
            return response;
          });
      });
  },
}

// Template Management
const templateApi = {
  /**
   * Get all available templates.
   * 
   * @returns {Promise} - List of templates
   */
  getAll: () => get('/templates'),
  
  /**
   * Get a specific template by id.
   * 
   * @param {string} id - The template id
   * @returns {Promise} - The template data
   */
  getById: (id) => get(`/templates/${id}`),
  
  /**
   * Create an entity type from a template.
   * 
   * @param {string} templateId - The template id
   * @param {object} customization - Customization options for the template
   * @returns {Promise} - The created entity type
   */
  createEntityType: (templateId, customization) => post(`/templates/${templateId}/create`, customization),
  
  /**
   * Delete a template by ID.
   * 
   * @param {string} id - The template id to delete
   * @returns {Promise} - Response indicating success or failure
   */
  delete: (id) => del(`/templates/${id}`),
}

// Simulation Management
const simulationApi = {
  /**
   * Get all simulations.
   * 
   * @returns {Promise} - List of simulations
   */
  getAll: () => get('/simulations'),
  
  /**
   * Get a specific simulation by id.
   * 
   * @param {string} id - The simulation id
   * @returns {Promise} - The simulation data
   */
  getById: (id) => get(`/simulations/${id}`),
  
  /**
   * Create a new simulation.
   * 
   * @param {object} simulation - The simulation data including context and entity IDs
   * @returns {Promise} - The created simulation
   */
  create: (simulation) => post('/simulations', simulation),
  
  /**
   * Delete a simulation by id.
   * 
   * @param {string} id - The simulation id to delete
   * @returns {Promise} - Response indicating success or failure
   */
  delete: (id) => del(`/simulations/${id}`),
}

/**
 * API methods for the unified simulation system.
 * This is the newer, more flexible simulation API that handles any number of entities.
 */
const unifiedSimulationApi = {
  /**
   * Get all unified simulations, with optional filtering.
   * 
   * @param {Object} params - Query parameters for filtering simulations
   *   @param {string} [params.entity_id] - Filter by entity ID
   *   @param {string} [params.entity_type_id] - Filter by entity type ID
   *   @param {string} [params.interaction_type] - Filter by interaction type (solo, dyadic, group)
   *   @param {number} [params.limit=20] - Maximum number of results to return
   *   @param {number} [params.offset=0] - Number of results to skip (for pagination)
   * @returns {Promise} - List of simulations
   */
  getAll: (params) => {
    const queryString = params ? `?${new URLSearchParams(params)}` : '';
    return get(`/unified-simulations${queryString}`);
  },
  
  /**
   * Get a specific unified simulation by id.
   * 
   * @param {string} id - The simulation id
   * @returns {Promise} - The simulation data
   */
  getById: (id) => get(`/unified-simulations/${id}`),
  
  /**
   * Create a new unified simulation.
   * 
   * @param {Object} simulation - The simulation data
   *   @param {string} simulation.context - Text description of the situation
   *   @param {string[]} simulation.entities - Array of entity IDs to include
   *   @param {number} [simulation.n_turns=1] - Number of turns to generate per round
   *   @param {number} [simulation.simulation_rounds=1] - Number of sequential LLM calls to make
   *   @param {Object} [simulation.metadata] - Optional metadata for the simulation
   *   @param {string} [simulation.name] - Optional name for the simulation
   *   @param {string} [simulation.interaction_type="discussion"] - Type of interaction (e.g., discussion, debate, trade, fight)
   *   @param {string} [simulation.language="English"] - Output language for the interaction
   * @returns {Promise} - The created simulation
   */
  create: (simulation) => post('/unified-simulations', simulation),
  
  /**
   * Continue an existing unified simulation with more turns.
   * 
   * @param {string} id - The simulation id to continue
   * @param {Object} options - Continuation options
   *   @param {number} [options.n_turns=1] - Number of turns to generate per round
   *   @param {number} [options.simulation_rounds=1] - Number of sequential LLM calls to make
   *   @param {string} [options.interaction_type="discussion"] - Type of interaction (e.g., discussion, debate, trade, fight)
   *   @param {string} [options.language="English"] - Output language for the interaction
   * @returns {Promise} - The updated simulation
   */
  continue: (id, options) => post(`/unified-simulations/${id}/continue`, options),
  
  /**
   * Delete a unified simulation by id.
   * 
   * @param {string} id - The simulation id to delete
   * @returns {Promise} - Response indicating success or failure
   */
  delete: (id) => del(`/unified-simulations/${id}`),
}

/**
 * API methods for the batch simulation system.
 * This handles running multiple simulations in parallel with configurable parameters.
 */
const batchSimulationApi = {
  /**
   * Get all batch simulations.
   * 
   * @param {Object} params - Query parameters
   *   @param {boolean} [params.include_simulations=false] - Whether to include simulations in each batch
   *   @param {number} [params.limit=20] - Maximum number of results to return
   *   @param {number} [params.offset=0] - Number of results to skip (for pagination)
   * @returns {Promise} - List of batch simulations
   */
  getAll: (params) => {
    const queryString = params ? `?${new URLSearchParams(params)}` : '';
    return get(`/batch-simulations${queryString}`);
  },
  
  /**
   * Get a specific batch simulation by id.
   * 
   * @param {string} id - The batch simulation id
   * @returns {Promise} - The batch simulation data with all simulations
   */
  getById: (id) => get(`/batch-simulations/${id}`),
  
  /**
   * Create a new batch simulation.
   * 
   * @param {Object} batchSimulation - The batch simulation data
   *   @param {string} batchSimulation.name - Name for the batch
   *   @param {string} [batchSimulation.description] - Optional description of the batch
   *   @param {string} batchSimulation.context - Text description of the situation
   *   @param {string[]} batchSimulation.entity_ids - Array of entity IDs to use in simulations
   *   @param {number} batchSimulation.interaction_size - Number of entities per simulation
   *   @param {number} batchSimulation.num_simulations - Number of simulations to run
   *   @param {number} [batchSimulation.n_turns=1] - Number of turns per simulation round
   *   @param {number} [batchSimulation.simulation_rounds=1] - Number of simulation rounds
   *   @param {Object} [batchSimulation.metadata] - Optional metadata for the batch
   * @returns {Promise} - The created batch simulation id and status
   */
  create: (batchSimulation) => post('/batch-simulations', batchSimulation),
  
  /**
   * Delete a batch simulation by id.
   * 
   * @param {string} id - The batch simulation id to delete
   * @returns {Promise} - Response indicating success or failure
   */
  delete: (id) => del(`/batch-simulations/${id}`),
  
  /**
   * Export batch simulation data in different formats.
   * 
   * @param {string} id - The batch simulation id
   * @param {string} format - Export format ('json' or 'csv')
   * @returns {Promise} - The exported data
   */
  export: (id, format = 'json') => {
    return get(`/batch-simulations/${id}/export?format=${format}`);
  }
}

// Export a default API object with all the API functions
const api = {
  // Base methods
  get,
  post,
  put,
  delete: del,
  
  // Higher-level methods for convenience
  getEntityTypes: entityTypeApi.getAll,
  getEntityType: entityTypeApi.getById,
  createEntityType: entityTypeApi.create,
  updateEntityType: entityTypeApi.update,
  
  getEntity: entityApi.getById,
  getEntitiesByType: entityApi.getByType,
  createEntity: entityApi.create,
  updateEntity: entityApi.update,
  generateEntities: entityApi.generateEntities,
  generateEntityBatch: entityApi.generateEntityBatch,
  deleteEntity: entityApi.delete,
  deleteEntitiesByType: entityApi.deleteByType,
  
  getTemplates: templateApi.getAll,
  getTemplate: templateApi.getById,
  createEntityTypeFromTemplate: templateApi.createEntityType,
  
  getSimulations: simulationApi.getAll,
  getSimulation: simulationApi.getById,
  createSimulation: simulationApi.create,
  deleteSimulation: simulationApi.delete,
  
  // New unified simulation methods
  getUnifiedSimulations: unifiedSimulationApi.getAll,
  getUnifiedSimulation: unifiedSimulationApi.getById,
  createUnifiedSimulation: unifiedSimulationApi.create,
  continueUnifiedSimulation: unifiedSimulationApi.continue,
  deleteUnifiedSimulation: unifiedSimulationApi.delete,
  
  // Batch simulation methods
  getBatchSimulations: batchSimulationApi.getAll,
  getBatchSimulation: batchSimulationApi.getById,
  createBatchSimulation: batchSimulationApi.create,
  deleteBatchSimulation: batchSimulationApi.delete,
  exportBatchSimulation: batchSimulationApi.export,
  
  // Original API objects
  entityType: entityTypeApi,
  entity: entityApi,
  template: templateApi,
  simulation: simulationApi,
  unifiedSimulation: unifiedSimulationApi,
  batchSimulation: batchSimulationApi
};

// Export the API objects as named exports as well
export { entityTypeApi, entityApi, templateApi, simulationApi, unifiedSimulationApi, batchSimulationApi };

export default api; 