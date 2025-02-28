// Dimension Types
export enum DimensionType {
  CATEGORICAL = 'categorical',
  NUMERIC = 'numeric',
  TEXT = 'text'
}

export enum ImportanceLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high'
}

export interface CategoricalConstraint {
  allowed_values: string[];
  probabilities?: number[]; // Probability weights for each allowed value
}

export interface NumericConstraint {
  min: number;
  max: number;
  distribution?: 'uniform' | 'normal' | 'skewed'; // Type of distribution
  mean?: number; // For normal distribution
  std_dev?: number; // For normal distribution
  skew_direction?: 'left' | 'right'; // For skewed distribution
  skew_factor?: number; // For skewed distribution (0-1)
}

export interface Constraint {
  [key: string]: any;
  allowed_values?: string[];
  probabilities?: number[];
  min?: number;
  max?: number;
  distribution?: 'uniform' | 'normal' | 'skewed';
  mean?: number;
  std_dev?: number;
  skew_direction?: 'left' | 'right';
  skew_factor?: number;
}

export interface Dependency {
  dimension: string;
  condition: string;
}

export interface Dimension {
  name: string;
  description: string;
  type: DimensionType;
  importance: ImportanceLevel;
  constraints?: Constraint;
  dependencies?: Dependency[];
}

// Persona Types
export interface Trait {
  dimension: string;
  value: any;
  explanation?: string;
}

export interface Persona {
  id: string;
  name: string;
  traits: Trait[];
  backstory: string;
  additional_attributes?: Record<string, any>;
}

export interface PersonaLibrary {
  personas: Record<string, Persona>;
}

// Generation Types
export interface GenerationSettings {
  num_personas: number;
  diversity_level: 'low' | 'medium' | 'high';
  dimensions?: string[];
}

export interface ValidationResult {
  is_valid: boolean;
  errors: string[];
  coherence_score?: number;
  explanation?: string;
  suggestions?: string[];
}

// Discussion Types
export interface DiscussionSettings {
  personas: string[];
  topic: string;
  format: 'debate' | 'conversation' | 'interview' | 'panel';
  num_rounds: number;
}

export interface Discussion {
  id: string;
  settings: DiscussionSettings;
  content: string;
  created_at: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// App State Types
export interface AppState {
  dimensions: Dimension[];
  personas: Record<string, Persona>;
  discussions: Record<string, Discussion>;
  settings: {
    generation: {
      default_model: string;
      temperature: number;
      diversity_preference: string;
      backstory_detail_level: string;
    };
    validation: {
      strictness: string;
      coherence_threshold: number;
    };
    persistence: {
      format: string;
      default_save_location: string;
    };
  };
} 