/**
 * API service for communicating with the backend.
 * Contains functions for making requests to the API endpoints.
 */

const API_URL = 'http://localhost:5001/api';

/**
 * Make a GET request to the specified endpoint.
 * 
 * @param {string} endpoint - The API endpoint to request
 * @returns {Promise} - The response data or error
 */
async function get(endpoint) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache'
      },
      mode: 'cors',
      credentials: 'omit'  // Don't send credentials
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
    console.error(`Error fetching from ${endpoint}:`, error);
    return { status: 'error', message: error.message || 'Unknown error occurred' };
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
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
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
  getByType: (entityTypeId) => get(`/entity-types/${entityTypeId}/entities`),
  
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
   * @param {string|number} variability - Variability level (low, medium, high) or number (0-1)
   * @returns {Promise} - The generated entities
   */
  generate: (entityTypeId, count, variability) => {
    // Convert numeric variability to string (if it's a number)
    let variabilityLevel = variability;
    if (typeof variability === 'number') {
      if (variability < 0.33) {
        variabilityLevel = 'low';
      } else if (variability < 0.67) {
        variabilityLevel = 'medium';
      } else {
        variabilityLevel = 'high';
      }
    }
    
    return post('/entities', {
      entity_type_id: entityTypeId,
      count: count,
      variability: variabilityLevel,
      generate: true
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
  generateEntities: entityApi.generate,
  deleteEntity: entityApi.delete,
  deleteEntitiesByType: entityApi.deleteByType,
  
  getTemplates: templateApi.getAll,
  getTemplate: templateApi.getById,
  createEntityTypeFromTemplate: templateApi.createEntityType,
  
  getSimulations: simulationApi.getAll,
  getSimulation: simulationApi.getById,
  createSimulation: simulationApi.create,
  
  // Original API objects
  entityType: entityTypeApi,
  entity: entityApi,
  template: templateApi,
  simulation: simulationApi
};

// Export the API objects as named exports as well
export { entityTypeApi, entityApi, templateApi, simulationApi };

export default api; 