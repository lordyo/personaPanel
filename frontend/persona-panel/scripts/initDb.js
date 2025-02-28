const fs = require('fs');
const path = require('path');

// Create the scripts directory if it doesn't exist
const scriptsDir = path.join(__dirname);
if (!fs.existsSync(scriptsDir)) {
  fs.mkdirSync(scriptsDir, { recursive: true });
}

// Create mock data directly in this script
const mockDimensions = [
  {
    name: 'gender',
    description: 'The gender identity of the persona',
    type: 'categorical',
    importance: 'medium',
    constraints: {
      allowed_values: ['male', 'female', 'non-binary', 'other'],
      probabilities: [0.49, 0.49, 0.015, 0.005]
    }
  },
  {
    name: 'age',
    description: 'The age of the persona in years',
    type: 'numeric',
    importance: 'high',
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
    type: 'text',
    importance: 'high'
  },
  {
    name: 'education_level',
    description: 'The highest level of education completed by the persona',
    type: 'categorical',
    importance: 'medium',
    constraints: {
      allowed_values: ['high school', 'some college', 'bachelor\'s degree', 'master\'s degree', 'doctoral degree', 'professional degree'],
      probabilities: [0.30, 0.20, 0.25, 0.15, 0.05, 0.05]
    }
  },
  {
    name: 'personality_openness',
    description: 'Openness to experience (Big Five personality trait)',
    type: 'numeric',
    importance: 'high',
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
    type: 'numeric',
    importance: 'high',
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
    type: 'numeric',
    importance: 'high',
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
    type: 'numeric',
    importance: 'high',
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
    type: 'numeric',
    importance: 'high',
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
    type: 'categorical',
    importance: 'medium',
    constraints: {
      allowed_values: ['American', 'Chinese', 'Indian', 'Brazilian', 'Japanese', 'Nigerian', 'Russian'],
      probabilities: [0.25, 0.20, 0.15, 0.10, 0.10, 0.10, 0.10]
    }
  },
  {
    name: 'socioeconomic_background',
    description: 'The socioeconomic background of the persona',
    type: 'categorical',
    importance: 'medium',
    constraints: {
      allowed_values: ['working class', 'middle class', 'upper middle class', 'affluent'],
      probabilities: [0.25, 0.45, 0.25, 0.05]
    }
  },
  {
    name: 'values',
    description: 'Core values or principles important to the persona',
    type: 'text',
    importance: 'high'
  }
];

const mockPersonas = {
  'p1': {
    id: 'p1',
    name: 'Alex Chen',
    traits: [
      { dimension: 'gender', value: 'non-binary' },
      { dimension: 'age', value: 32 },
      { dimension: 'occupation', value: 'Software Engineer' },
      { dimension: 'education_level', value: "bachelor's degree" },
      { dimension: 'personality_openness', value: 8 },
      { dimension: 'personality_conscientiousness', value: 7 },
      { dimension: 'personality_extraversion', value: 4 },
      { dimension: 'personality_agreeableness', value: 6 },
      { dimension: 'personality_neuroticism', value: 5 },
      { dimension: 'nationality', value: 'Chinese-American' },
      { dimension: 'socioeconomic_background', value: 'middle class' },
      { dimension: 'values', value: 'innovation, knowledge, harmony' }
    ],
    backstory: `Alex Chen is a 32-year-old Software Engineer who identifies as non-binary. Born and raised in a middle class family with Chinese-American roots, they developed a strong sense of innovation, knowledge, and harmony from an early age.`
  },
  'p2': {
    id: 'p2',
    name: 'Maria Rodriguez',
    traits: [
      { dimension: 'gender', value: 'female' },
      { dimension: 'age', value: 45 },
      { dimension: 'occupation', value: 'High School Teacher' },
      { dimension: 'education_level', value: "master's degree" },
      { dimension: 'personality_openness', value: 6 },
      { dimension: 'personality_conscientiousness', value: 8 },
      { dimension: 'personality_extraversion', value: 7 },
      { dimension: 'personality_agreeableness', value: 9 },
      { dimension: 'personality_neuroticism', value: 4 },
      { dimension: 'nationality', value: 'Mexican-American' },
      { dimension: 'socioeconomic_background', value: 'working class' },
      { dimension: 'values', value: 'family, community, education' }
    ],
    backstory: `Maria Rodriguez is a 45-year-old High School Teacher who identifies as female. Born and raised in a working class family with Mexican-American roots, she developed a strong sense of family, community, and education from an early age.`
  }
};

const mockDiscussions = {
  'd1': {
    id: 'd1',
    settings: {
      personas: ['p1', 'p2'],
      topic: 'The Role of Technology in Education',
      format: 'conversation',
      num_rounds: 3
    },
    content: `# The Role of Technology in Education\n\n*A conversation between Alex Chen and Maria Rodriguez*\n\n**Alex Chen**: As someone who works in technology, I believe we need to integrate more digital tools in education. What do you think?\n\n**Maria Rodriguez**: While I see the benefits, we need to ensure technology enhances rather than replaces human connection in the classroom.`,
    created_at: '2023-11-15T14:30:00Z'
  }
};

// Create db.json with mock data
const dbData = {
  dimensions: mockDimensions,
  personas: mockPersonas,
  discussions: mockDiscussions
};

// Write to db.json
fs.writeFileSync(
  path.join(__dirname, '../db.json'),
  JSON.stringify(dbData, null, 2),
  'utf8'
);

console.log('Database initialized with mock data!'); 