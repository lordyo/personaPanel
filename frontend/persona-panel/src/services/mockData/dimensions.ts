import { Dimension, DimensionType, ImportanceLevel } from '../../types';

const mockDimensions: Dimension[] = [
  {
    name: 'gender',
    description: 'The gender identity of the persona',
    type: DimensionType.CATEGORICAL,
    importance: ImportanceLevel.MEDIUM,
    constraints: {
      allowed_values: ['male', 'female', 'non-binary', 'other'],
      probabilities: [0.49, 0.49, 0.015, 0.005] // Realistic gender distribution
    }
  },
  {
    name: 'age',
    description: 'The age of the persona in years',
    type: DimensionType.NUMERIC,
    importance: ImportanceLevel.HIGH,
    constraints: {
      min: 18,
      max: 90,
      distribution: 'normal',
      mean: 38,
      std_dev: 14
    }
  },
  {
    name: 'occupation',
    description: 'The primary occupation or profession of the persona',
    type: DimensionType.TEXT,
    importance: ImportanceLevel.HIGH
  },
  {
    name: 'education_level',
    description: 'The highest level of education completed by the persona',
    type: DimensionType.CATEGORICAL,
    importance: ImportanceLevel.MEDIUM,
    constraints: {
      allowed_values: ['high school', 'some college', 'bachelor\'s degree', 'master\'s degree', 'doctoral degree', 'professional degree'],
      probabilities: [0.30, 0.20, 0.25, 0.15, 0.05, 0.05] // Approximate real-world distribution
    }
  },
  {
    name: 'personality_openness',
    description: 'Openness to experience (Big Five personality trait)',
    type: DimensionType.NUMERIC,
    importance: ImportanceLevel.HIGH,
    constraints: {
      min: 1,
      max: 10,
      distribution: 'normal',
      mean: 5.5,
      std_dev: 1.5
    }
  },
  {
    name: 'personality_conscientiousness',
    description: 'Conscientiousness (Big Five personality trait)',
    type: DimensionType.NUMERIC,
    importance: ImportanceLevel.HIGH,
    constraints: {
      min: 1,
      max: 10,
      distribution: 'normal',
      mean: 5.5,
      std_dev: 1.5
    }
  },
  {
    name: 'personality_extraversion',
    description: 'Extraversion (Big Five personality trait)',
    type: DimensionType.NUMERIC,
    importance: ImportanceLevel.HIGH,
    constraints: {
      min: 1,
      max: 10,
      distribution: 'normal',
      mean: 5.5,
      std_dev: 1.5
    }
  },
  {
    name: 'personality_agreeableness',
    description: 'Agreeableness (Big Five personality trait)',
    type: DimensionType.NUMERIC,
    importance: ImportanceLevel.HIGH,
    constraints: {
      min: 1,
      max: 10,
      distribution: 'normal',
      mean: 5.5,
      std_dev: 1.5
    }
  },
  {
    name: 'personality_neuroticism',
    description: 'Neuroticism (Big Five personality trait)',
    type: DimensionType.NUMERIC,
    importance: ImportanceLevel.HIGH,
    constraints: {
      min: 1,
      max: 10,
      distribution: 'normal',
      mean: 5.5,
      std_dev: 1.5
    }
  },
  {
    name: 'nationality',
    description: 'The country of origin or primary national identity',
    type: DimensionType.CATEGORICAL,
    importance: ImportanceLevel.MEDIUM,
    constraints: {
      allowed_values: ['American', 'Chinese', 'Indian', 'Brazilian', 'Japanese', 'Nigerian', 'Russian'],
      probabilities: [0.25, 0.20, 0.15, 0.10, 0.10, 0.10, 0.10] // Simplified global distribution
    }
  },
  {
    name: 'socioeconomic_background',
    description: 'The socioeconomic background of the persona',
    type: DimensionType.CATEGORICAL,
    importance: ImportanceLevel.MEDIUM,
    constraints: {
      allowed_values: ['working class', 'middle class', 'upper middle class', 'affluent'],
      probabilities: [0.25, 0.45, 0.25, 0.05] // Approximate bell curve
    }
  },
  {
    name: 'values',
    description: 'Core values or principles important to the persona',
    type: DimensionType.TEXT,
    importance: ImportanceLevel.HIGH
  }
];

export default mockDimensions; 