"""
Sampling utilities for the GenAI Persona Framework.
"""
import random
from typing import Dict, List, Any, Optional, TypeVar, Callable

from persona_framework.modules.dimension import Dimension, DimensionRegistry
from persona_framework.modules.persona import Persona


T = TypeVar('T')


def sample_with_diversity(items: List[T], n: int, 
                          diversity_fn: Callable[[T, T], float],
                          attempts: int = 100) -> List[T]:
    """
    Sample n items from a list, maximizing diversity.
    
    Args:
        items: List of items to sample from
        n: Number of items to sample
        diversity_fn: Function that returns a diversity score between two items
        attempts: Number of sampling attempts to make
        
    Returns:
        List[T]: List of sampled items
    """
    if n >= len(items):
        return items
    
    best_sample = None
    best_diversity = -1
    
    for _ in range(attempts):
        sample = random.sample(items, n)
        
        # Calculate diversity as the sum of pairwise diversity scores
        diversity = 0
        count = 0
        for i in range(len(sample)):
            for j in range(i+1, len(sample)):
                diversity += diversity_fn(sample[i], sample[j])
                count += 1
        
        if count > 0:
            avg_diversity = diversity / count
        else:
            avg_diversity = 0
        
        if avg_diversity > best_diversity:
            best_diversity = avg_diversity
            best_sample = sample
    
    return best_sample


def persona_diversity(p1: Persona, p2: Persona) -> float:
    """
    Calculate diversity between two personas.
    
    Args:
        p1: First persona
        p2: Second persona
        
    Returns:
        float: Diversity score (0-1)
    """
    # Get all dimensions
    all_dimensions = set()
    for trait in p1.traits:
        all_dimensions.add(trait.dimension)
    for trait in p2.traits:
        all_dimensions.add(trait.dimension)
    
    if not all_dimensions:
        return 0
    
    # Calculate diversity for each dimension
    dimension_diversity = 0
    for dim in all_dimensions:
        v1 = p1.get_trait_value(dim)
        v2 = p2.get_trait_value(dim)
        
        # If either persona doesn't have this dimension, count as 0.5 diverse
        if v1 is None or v2 is None:
            dimension_diversity += 0.5
            continue
        
        # For numeric values, calculate normalized difference
        if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
            # Assume values are in range 0-100 for normalization
            max_diff = 100
            diff = abs(v1 - v2) / max_diff
            dimension_diversity += min(diff, 1.0)
        # For strings, binary comparison
        else:
            dimension_diversity += 1.0 if str(v1) != str(v2) else 0.0
    
    return dimension_diversity / len(all_dimensions)


def sample_diverse_personas(personas: List[Persona], n: int) -> List[Persona]:
    """
    Sample n personas from a list, maximizing diversity.
    
    Args:
        personas: List of personas to sample from
        n: Number of personas to sample
        
    Returns:
        List[Persona]: List of sampled personas
    """
    return sample_with_diversity(personas, n, persona_diversity) 