import axios from 'axios';
import { 
  Dimension, 
  Persona, 
  Discussion, 
  GenerationSettings, 
  DiscussionSettings,
  ValidationResult,
  ApiResponse,
  DimensionType
} from '../types';

// Mock data for development fallback
import mockDimensions from './mockData/dimensions';
// Temporarily comment out the import to fix the linter error
// import mockPersonas from './mockData/personas';
import mockDiscussions from './mockData/discussions';

// Use an empty object as a fallback for mockPersonas
const mockPersonas: Record<string, any> = {};

// Base API configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Use mock data only if explicitly set or if API is not available
const useMockData = process.env.REACT_APP_USE_MOCK_DATA === 'true';

// Local storage keys
const LS_KEYS = {
  DIMENSIONS: 'persona_panel_dimensions',
  PERSONAS: 'persona_panel_personas',
  DISCUSSIONS: 'persona_panel_discussions'
};

// Helper functions for local storage
const getFromLocalStorage = <T>(key: string, defaultValue: T): T => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error(`Error reading from localStorage (${key}):`, error);
    return defaultValue;
  }
};

const saveToLocalStorage = <T>(key: string, value: T): void => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error(`Error saving to localStorage (${key}):`, error);
  }
};

// Dimensions API
export const dimensionsApi = {
  getAll: async (): Promise<ApiResponse<Dimension[]>> => {
    if (useMockData) {
      await delay(500);
      // Try to get from localStorage first, fall back to mock data
      const dimensions = getFromLocalStorage<Dimension[]>(LS_KEYS.DIMENSIONS, mockDimensions);
      return { success: true, data: dimensions };
    }
    
    try {
      const response = await api.get<Dimension[]>('/dimensions');
      // Save to localStorage as backup
      saveToLocalStorage(LS_KEYS.DIMENSIONS, response.data);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error fetching dimensions:', error);
      // Return error instead of falling back to localStorage
      return { 
        success: false, 
        error: 'Failed to fetch dimensions. The API server may be unavailable.' 
      };
    }
  },
  
  create: async (dimension: Dimension): Promise<ApiResponse<Dimension>> => {
    if (useMockData) {
      await delay(500);
      // Get current dimensions from localStorage
      const dimensions = getFromLocalStorage<Dimension[]>(LS_KEYS.DIMENSIONS, mockDimensions);
      // Add new dimension
      dimensions.push(dimension);
      // Save back to localStorage
      saveToLocalStorage(LS_KEYS.DIMENSIONS, dimensions);
      return { success: true, data: dimension };
    }
    
    try {
      const response = await api.post<Dimension>('/dimensions', dimension);
      // Update localStorage
      const dimensions = getFromLocalStorage<Dimension[]>(LS_KEYS.DIMENSIONS, []);
      dimensions.push(response.data);
      saveToLocalStorage(LS_KEYS.DIMENSIONS, dimensions);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error creating dimension:', error);
      return { success: false, error: 'Failed to create dimension' };
    }
  },
  
  update: async (name: string, dimension: Partial<Dimension>): Promise<ApiResponse<Dimension>> => {
    if (useMockData) {
      await delay(500);
      // Get current dimensions from localStorage
      const dimensions = getFromLocalStorage<Dimension[]>(LS_KEYS.DIMENSIONS, mockDimensions);
      const index = dimensions.findIndex(d => d.name === name);
      if (index === -1) {
        return { success: false, error: 'Dimension not found' };
      }
      
      dimensions[index] = { ...dimensions[index], ...dimension };
      // Save back to localStorage
      saveToLocalStorage(LS_KEYS.DIMENSIONS, dimensions);
      return { success: true, data: dimensions[index] };
    }
    
    try {
      const response = await api.put<Dimension>(`/dimensions/${name}`, dimension);
      // Update localStorage
      const dimensions = getFromLocalStorage<Dimension[]>(LS_KEYS.DIMENSIONS, []);
      const index = dimensions.findIndex(d => d.name === name);
      if (index !== -1) {
        dimensions[index] = response.data;
        saveToLocalStorage(LS_KEYS.DIMENSIONS, dimensions);
      }
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Error updating dimension:', error);
      return { success: false, error: 'Failed to update dimension' };
    }
  },
  
  delete: async (name: string): Promise<ApiResponse<void>> => {
    if (useMockData) {
      await delay(500);
      // Get current dimensions from localStorage
      const dimensions = getFromLocalStorage<Dimension[]>(LS_KEYS.DIMENSIONS, mockDimensions);
      const index = dimensions.findIndex(d => d.name === name);
      if (index === -1) {
        return { success: false, error: 'Dimension not found' };
      }
      
      dimensions.splice(index, 1);
      // Save back to localStorage
      saveToLocalStorage(LS_KEYS.DIMENSIONS, dimensions);
      return { success: true };
    }
    
    try {
      // First, get all dimensions to find the one with the matching name
      const allDimensionsResponse = await api.get('/dimensions');
      const dimensions = allDimensionsResponse.data;
      
      // Find the dimension with the matching name
      const dimension = Array.isArray(dimensions) 
        ? dimensions.find((d: Dimension) => d.name === name)
        : Object.values(dimensions as Record<string, Dimension>).find((d: Dimension) => d.name === name);
      
      if (!dimension) {
        return { success: false, error: 'Dimension not found' };
      }
      
      // Delete using the dimension's ID
      await api.delete(`/dimensions/${dimension.id}`);
      
      // Update localStorage
      const localDimensions = getFromLocalStorage<Dimension[]>(LS_KEYS.DIMENSIONS, []);
      const index = localDimensions.findIndex(d => d.name === name);
      if (index !== -1) {
        localDimensions.splice(index, 1);
        saveToLocalStorage(LS_KEYS.DIMENSIONS, localDimensions);
      }
      
      return { success: true };
    } catch (error) {
      console.error('Error deleting dimension:', error);
      return { success: false, error: 'Failed to delete dimension' };
    }
  }
};

// Personas API
export const personasApi = {
  getAll: async (): Promise<ApiResponse<Record<string, Persona>>> => {
    if (useMockData) {
      await delay(500);
      // Try to get from localStorage first, fall back to mock data
      const personas = getFromLocalStorage<Record<string, Persona>>(LS_KEYS.PERSONAS, mockPersonas);
      return { success: true, data: personas };
    }
    
    try {
      const response = await api.get('/personas');
      
      // Handle the response based on its structure
      let personasRecord: Record<string, Persona> = {};
      
      if (Array.isArray(response.data)) {
        // If it's an array, convert to record object
        response.data.forEach(persona => {
          personasRecord[persona.id] = persona;
        });
      } else if (typeof response.data === 'object') {
        // If it's already an object (JSON Server format), use it directly
        personasRecord = response.data;
      }
      
      // Save to localStorage as backup
      saveToLocalStorage(LS_KEYS.PERSONAS, personasRecord);
      return { success: true, data: personasRecord };
    } catch (error) {
      console.error('Error fetching personas:', error);
      // Return error instead of falling back to localStorage
      return { 
        success: false, 
        error: 'Failed to fetch personas. The API server may be unavailable.' 
      };
    }
  },
  
  getById: async (id: string): Promise<ApiResponse<Persona>> => {
    if (useMockData) {
      await delay(500);
      const persona = mockPersonas[id];
      if (!persona) {
        return { success: false, error: 'Persona not found' };
      }
      
      return { success: true, data: persona };
    }
    
    try {
      const response = await api.get<ApiResponse<Persona>>(`/personas/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching persona:', error);
      return { success: false, error: 'Failed to fetch persona' };
    }
  },
  
  create: async (persona: Omit<Persona, 'id'>): Promise<ApiResponse<Persona>> => {
    if (useMockData) {
      await delay(500);
      const id = Math.random().toString(36).substring(2, 9);
      const newPersona = { ...persona, id } as Persona;
      mockPersonas[id] = newPersona;
      return { success: true, data: newPersona };
    }
    
    try {
      // Try to save to the backend API
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
      try {
        console.log('Attempting to save persona to backend:', backendUrl);
        // Wrap the persona in the expected request format with a 'persona' field
        const backendResponse = await axios.post<ApiResponse<Persona>>(`${backendUrl}/api/personas/save`, { persona });
        console.log('Backend response:', backendResponse.data);
        
        if (backendResponse.data.success && backendResponse.data.data) {
          console.log('Successfully saved persona to backend');
          return { success: true, data: backendResponse.data.data };
        } else {
          return { 
            success: false, 
            error: backendResponse.data.error || 'Unknown error from backend service' 
          };
        }
      } catch (backendError: any) {
        console.error('Failed to save persona to backend:', backendError);
        if (backendError.response) {
          console.error('Error response:', {
            status: backendError.response.status,
            statusText: backendError.response.statusText,
            data: backendError.response.data
          });
        }
        
        // Return a clear error message instead of falling back to JSON server
        return { 
          success: false, 
          error: backendError.response?.data?.detail || 
                'Failed to save persona. The backend service is unavailable.' 
        };
      }
    } catch (error) {
      console.error('Error creating persona:', error);
      return { success: false, error: 'Failed to create persona due to an unexpected error' };
    }
  },
  
  update: async (id: string, persona: Partial<Persona>): Promise<ApiResponse<Persona>> => {
    if (useMockData) {
      await delay(500);
      if (!mockPersonas[id]) {
        return { success: false, error: 'Persona not found' };
      }
      
      mockPersonas[id] = { ...mockPersonas[id], ...persona };
      return { success: true, data: mockPersonas[id] };
    }
    
    try {
      const response = await api.put<ApiResponse<Persona>>(`/personas/${id}`, persona);
      return response.data;
    } catch (error) {
      console.error('Error updating persona:', error);
      return { success: false, error: 'Failed to update persona' };
    }
  },
  
  delete: async (id: string): Promise<ApiResponse<void>> => {
    if (useMockData) {
      await delay(500);
      if (!mockPersonas[id]) {
        return { success: false, error: 'Persona not found' };
      }
      
      delete mockPersonas[id];
      return { success: true };
    }
    
    try {
      const response = await api.delete<ApiResponse<void>>(`/personas/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting persona:', error);
      return { success: false, error: 'Failed to delete persona' };
    }
  },
  
  generate: async (settings: GenerationSettings): Promise<ApiResponse<Persona[]>> => {
    try {
      // Try to use the backend API (preferred method)
      return await generatePersonasViaBackend(settings, []).then(personas => ({
        success: true, 
        data: personas
      }));
    } catch (error) {
      console.error('Error generating personas:', error);
      return { 
        success: false, 
        error: 'Failed to generate personas. The backend service may be unavailable.'
      };
    }
  },
  
  validate: async (persona: Persona): Promise<ApiResponse<ValidationResult>> => {
    if (useMockData) {
      await delay(1000);
      const coherence_score = Math.random() * 10;
      
      return { 
        success: true, 
        data: {
          is_valid: coherence_score > 5,
          errors: coherence_score > 5 ? [] : ['Some traits seem inconsistent'],
          coherence_score,
          explanation: `This persona has a coherence score of ${coherence_score.toFixed(1)}/10.`,
          suggestions: coherence_score > 8 ? [] : ['Consider adding more details to the backstory']
        }
      };
    }
    
    try {
      const response = await api.post<ApiResponse<ValidationResult>>('/personas/validate', persona);
      return response.data;
    } catch (error) {
      console.error('Error validating persona:', error);
      return { success: false, error: 'Failed to validate persona' };
    }
  },
};

// Function to attempt persona generation via the backend
const generatePersonasViaBackend = async (settings: GenerationSettings, allDimensions: Dimension[]): Promise<Persona[]> => {
  // Try to use the backend API (DSPy and Claude)
  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
  const response = await axios.post(`${backendUrl}/api/personas/generate`, {
    dimensions: allDimensions,
    num_personas: settings.num_personas,
    diversity_level: settings.diversity_level || "medium",
    selected_dimensions: settings.dimensions || []
  });
  
  if (response.data && Array.isArray(response.data)) {
    console.log("Successfully generated personas using DSPy backend");
    return response.data;
  }
  
  throw new Error("Backend did not return valid persona data");
};

// Discussions API
export const discussionsApi = {
  getAll: async (): Promise<ApiResponse<Record<string, Discussion>>> => {
    if (useMockData) {
      await delay(500);
      return { success: true, data: mockDiscussions };
    }
    
    try {
      const response = await api.get<ApiResponse<Record<string, Discussion>>>('/discussions');
      return response.data;
    } catch (error) {
      console.error('Error fetching discussions:', error);
      return { success: false, error: 'Failed to fetch discussions' };
    }
  },
  
  getById: async (id: string): Promise<ApiResponse<Discussion>> => {
    if (useMockData) {
      await delay(500);
      const discussion = mockDiscussions[id];
      if (!discussion) {
        return { success: false, error: 'Discussion not found' };
      }
      
      return { success: true, data: discussion };
    }
    
    try {
      const response = await api.get<ApiResponse<Discussion>>(`/discussions/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching discussion:', error);
      return { success: false, error: 'Failed to fetch discussion' };
    }
  },
  
  create: async (settings: DiscussionSettings): Promise<ApiResponse<Discussion>> => {
    if (useMockData) {
      await delay(3000); // Longer delay to simulate generation
      // Return an error stating mock generation is disabled, instead of creating mock content
      return { 
        success: false, 
        error: 'Discussion generation requires a backend API connection. Mock generation has been disabled.' 
      };
    }
    
    try {
      const response = await api.post<ApiResponse<Discussion>>('/discussions', settings);
      return response.data;
    } catch (error) {
      console.error('Error creating discussion:', error);
      return { success: false, error: 'Failed to create discussion' };
    }
  },
  
  delete: async (id: string): Promise<ApiResponse<void>> => {
    if (useMockData) {
      await delay(500);
      if (!mockDiscussions[id]) {
        return { success: false, error: 'Discussion not found' };
      }
      
      delete mockDiscussions[id];
      return { success: true };
    }
    
    try {
      const response = await api.delete<ApiResponse<void>>(`/discussions/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting discussion:', error);
      return { success: false, error: 'Failed to delete discussion' };
    }
  },
};

export default {
  dimensions: dimensionsApi,
  personas: personasApi,
  discussions: discussionsApi,
}; 