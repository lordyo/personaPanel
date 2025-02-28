import { Persona } from '../../types';

// Mock personas data for development and testing
const mockPersonas: Record<string, Persona> = {
  'p1': {
    id: 'p1',
    name: 'Alex Chen',
    traits: [
      { dimension: 'gender', value: 'male' },
      { dimension: 'age', value: 32 },
      { dimension: 'occupation', value: 'Software Engineer' },
      { dimension: 'education_level', value: 'Master\'s Degree' },
      { dimension: 'nationality', value: 'Chinese-American' },
      { dimension: 'socioeconomic_background', value: 'middle class' },
      { dimension: 'openness', value: 8 },
      { dimension: 'conscientiousness', value: 7 },
      { dimension: 'extraversion', value: 6 },
      { dimension: 'agreeableness', value: 7 },
      { dimension: 'neuroticism', value: 4 }
    ],
    backstory: 'Alex Chen is a 32-year-old Software Engineer who identifies as male. Born and raised with Chinese-American roots, he values innovation, family, and continuous learning. Alex grew up in a middle-class household in San Francisco, where his parents encouraged his interest in technology from an early age. After completing his Master\'s degree in Computer Science, he worked for several tech startups before landing his current position at a major tech company. He enjoys rock climbing on weekends and participates in local coding meetups.'
  },
  'p2': {
    id: 'p2',
    name: 'Maria Rodriguez',
    traits: [
      { dimension: 'gender', value: 'female' },
      { dimension: 'age', value: 45 },
      { dimension: 'occupation', value: 'High School Teacher' },
      { dimension: 'education_level', value: 'Bachelor\'s Degree' },
      { dimension: 'nationality', value: 'Mexican-American' },
      { dimension: 'socioeconomic_background', value: 'working class' },
      { dimension: 'openness', value: 7 },
      { dimension: 'conscientiousness', value: 8 },
      { dimension: 'extraversion', value: 7 },
      { dimension: 'agreeableness', value: 8 },
      { dimension: 'neuroticism', value: 5 }
    ],
    backstory: 'Maria Rodriguez is a 45-year-old High School Teacher who identifies as female. Born and raised with Mexican-American roots, she values education, community, and cultural heritage. Maria grew up in a working-class family in Los Angeles and was the first in her family to attend college. She has been teaching history for over twenty years and is known for incorporating cultural perspectives into her curriculum. She is actively involved in her local community, organizing cultural events and mentoring first-generation college students.'
  },
  'p3': {
    id: 'p3',
    name: 'James Wilson',
    traits: [
      { dimension: 'gender', value: 'male' },
      { dimension: 'age', value: 58 },
      { dimension: 'occupation', value: 'Small Business Owner' },
      { dimension: 'education_level', value: 'High School Diploma' },
      { dimension: 'nationality', value: 'American' },
      { dimension: 'socioeconomic_background', value: 'working class' },
      { dimension: 'openness', value: 5 },
      { dimension: 'conscientiousness', value: 9 },
      { dimension: 'extraversion', value: 6 },
      { dimension: 'agreeableness', value: 6 },
      { dimension: 'neuroticism', value: 4 }
    ],
    backstory: 'James Wilson is a 58-year-old Small Business Owner who identifies as male. Born and raised in rural Michigan, he values hard work, tradition, and self-reliance. After graduating high school, James worked in his father\'s hardware store before taking over the business. He has successfully adapted the store to changing market conditions over the decades, recently adding an online presence. James is active in his local Chamber of Commerce and coaches Little League baseball in his spare time.'
  },
  'p4': {
    id: 'p4',
    name: 'Zainab Okafor',
    traits: [
      { dimension: 'gender', value: 'female' },
      { dimension: 'age', value: 37 },
      { dimension: 'occupation', value: 'Environmental Scientist' },
      { dimension: 'education_level', value: 'PhD' },
      { dimension: 'nationality', value: 'Nigerian-American' },
      { dimension: 'socioeconomic_background', value: 'upper middle class' },
      { dimension: 'openness', value: 9 },
      { dimension: 'conscientiousness', value: 8 },
      { dimension: 'extraversion', value: 5 },
      { dimension: 'agreeableness', value: 7 },
      { dimension: 'neuroticism', value: 3 }
    ],
    backstory: 'Zainab Okafor is a 37-year-old Environmental Scientist who identifies as female. Born in Lagos, Nigeria and raised in the United States, she values sustainability, global perspective, and intellectual curiosity. Zainab completed her PhD in Environmental Science at MIT and now leads research projects on sustainable agriculture practices across different ecosystems. She travels frequently for her research and has published several papers on indigenous farming techniques. In her free time, she enjoys botanical photography and volunteers with youth science programs.'
  }
};

export default mockPersonas; 