import { Discussion } from '../../types';

// Mock discussions data for development and testing
const mockDiscussions: Record<string, any> = {
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
  },
  'd2': {
    id: 'd2',
    settings: {
      personas: ['p2', 'p4'],
      topic: 'Education Reform and Environmental Sustainability',
      format: 'conversation',
      num_rounds: 2
    },
    content: `# Education Reform and Environmental Sustainability

*A conversation between Maria Rodriguez and Zainab Okafor*

**Maria Rodriguez**: As an educator with over twenty years of experience, I've seen how disconnected our curriculum has become from the real challenges students will face. Environmental issues are mentioned briefly in science classes, but we're not preparing students to think critically about sustainability in their communities. I try to incorporate gardening and local ecology into my history lessons, but it's challenging within the current standardized testing framework.

**Zainab Okafor**: That's precisely the disconnect I see in my work as well. The environmental challenges we face require interdisciplinary thinking, yet our education systems remain siloed. In my research across different African communities, I've observed that traditional knowledge systems often integrate environmental stewardship across all aspects of learning. Western education could learn from this approach. Have you found ways to bring real-world environmental projects into your classroom despite the constraints?

**Maria Rodriguez**: Yes, though it's not always easy. I've developed a community history project where students interview local elders about how the environment has changed over generations. They create maps showing changes in local agriculture, water sources, and wildlife. It helps them see environmental issues as part of their community's story rather than abstract global problems. I've found that connecting environmental concepts to personal and cultural narratives makes them more engaging for students. How do you think we could better integrate traditional knowledge systems into formal education?

**Zainab Okafor**: That project sounds wonderful, Maria! It creates exactly the kind of intergenerational and place-based learning that research shows is effective. To answer your question, I believe we need to start by acknowledging that environmental knowledge exists in many forms, not just in textbooks. In my ideal curriculum, students would learn scientific principles alongside indigenous knowledge, with elders and community members recognized as legitimate educators alongside certified teachers. For example, in Nigeria, I've documented traditional farming techniques that are more sustainable than modern industrial methods, yet this knowledge is being lost because it's not valued in formal education. Schools could serve as bridges between traditional wisdom and contemporary science, rather than replacing one with the other.`,
    created_at: '2023-12-03T09:15:00Z'
  },
  'd3': {
    id: 'd3',
    settings: {
      personas: ['p1', 'p2', 'p4'],
      topic: 'The Future of Work in an AI-Driven Economy',
      format: 'panel',
      num_rounds: 3
    },
    content: `# The Future of Work in an AI-Driven Economy

*A panel between Alex Chen, Maria Rodriguez, and Zainab Okafor*

**Alex Chen**: From my perspective in the tech industry, I see AI transforming work in ways that are both exciting and concerning. While AI will automate many routine tasks, it's also creating new categories of jobs that we couldn't have imagined a decade ago. The key challenge is ensuring that the transition doesn't leave vulnerable populations behind. Companies developing these technologies need to consider the broader societal impacts, not just technical capabilities.

**Maria Rodriguez**: As an educator, I'm deeply concerned about how we're preparing students for this changing landscape. Our education system was designed for an industrial economy, not an AI-driven one. We're still teaching many skills that will be automated, while neglecting the human capabilities that will become more valuable - creativity, emotional intelligence, ethical reasoning, and adaptability. We need to fundamentally rethink education to emphasize these uniquely human strengths.

**Zainab Okafor**: I'd like to add a global perspective here. The impacts of AI on work will be felt very differently across regions. In many developing countries, the traditional path of industrialization as a route to economic development may be cut off by automation. However, digital technologies also create opportunities to leapfrog traditional development stages. The question is whether the benefits of AI will be distributed equitably or further concentrate wealth and power. We need inclusive policies that ensure technologies serve diverse communities.

**Alex Chen**: That's an excellent point about global inequality, Zainab. In Silicon Valley, there's often a blindspot about how technologies developed in our bubble will impact different regions and socioeconomic groups. Maria, I agree completely about education reform. The technical skills we teach today may be obsolete quickly, but critical thinking and creativity remain essential. I'd add that continuous learning throughout one's career will become the norm - the idea of education as something that ends when you start working is already outdated.

**Maria Rodriguez**: Exactly, Alex. We need to move from a model of "education, then work" to "lifelong learning." This has implications for how we structure educational institutions, workplace training, and even social safety nets. I'm curious, Zainab, in your research across different communities, have you observed alternative models of work and learning that might be more resilient in the face of technological disruption?

**Zainab Okafor**: Yes, I've studied communities that emphasize collective knowledge-sharing and intergenerational learning, which creates remarkable resilience. These models don't separate "education" from "work" in the way Western systems do. I believe we can learn from these approaches while embracing new technologies. Alex, given your position in the tech industry, what responsibility do you think technology companies have in shaping a more equitable future of work?`,
    created_at: '2024-01-20T16:45:00Z'
  }
};

export default mockDiscussions; 