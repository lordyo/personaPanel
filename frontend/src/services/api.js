/**
 * API service for communicating with the backend.
 * Contains functions for making requests to the API endpoints.
 */

const API_URL = 'http://localhost:5000/api';

/**
 * Make a GET request to the specified endpoint.
 * 
 * @param {string} endpoint - The API endpoint to request
 * @returns {Promise} - The response data or error
 */
async function get(endpoint) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`);
    const data = await response.json();
    return data;
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
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`Error posting to ${endpoint}:`, error);
    throw error;
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
      },
      body: JSON.stringify(body),
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`Error putting to ${endpoint}:`, error);
    throw error;
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
  get,
  post,
  put,
  entityType: entityTypeApi,
  entity: entityApi,
  template: templateApi,
  simulation: simulationApi
};

export default api; 