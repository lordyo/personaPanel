#!/usr/bin/env python3
"""
Test script to demonstrate how bisociative fuel words are used in entity generation.
This script loads the bisociative words and shows sample combinations.
"""

import os
import json
import random
import sys

# Get the repository root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
BISOCIATIVE_WORDS_PATH = os.path.join(CONFIG_DIR, "bisociative_words.json")

def get_random_bisociative_words(count=2):
    """Get random words for bisociative fuel from the word list."""
    try:
        with open(BISOCIATIVE_WORDS_PATH, 'r') as f:
            word_data = json.load(f)
            words = word_data.get("words", [])
            
        if not words:
            print("No bisociative words found in the configuration file.")
            sys.exit(1)
            
        return random.sample(words, min(count, len(words)))
    except Exception as e:
        print(f"Error getting bisociative words: {str(e)}")
        sys.exit(1)

def main():
    """Show examples of bisociative fuel word combinations."""
    # Load the words
    try:
        with open(BISOCIATIVE_WORDS_PATH, 'r') as f:
            word_data = json.load(f)
            words = word_data.get("words", [])
        
        print(f"Loaded {len(words)} bisociative fuel words")
        
        # Print some examples
        print("\nExample words (sample of 20):")
        sample = random.sample(words, min(20, len(words)))
        for i in range(0, len(sample), 4):
            row = sample[i:min(i+4, len(sample))]
            print(", ".join(row))
            
        # Print example combinations
        print("\nExample bisociative fuel combinations (as used in entity generation):")
        for i in range(10):
            fuel_words = get_random_bisociative_words(2)
            print(f"{i+1}. '{fuel_words[0]}, {fuel_words[1]}'")
            
        print("\nHow these are used in entity generation:")
        print("1. Two random words are selected from the list")
        print("2. They're provided to the LLM as 'bisociative fuel' for creative inspiration")
        print("3. The LLM subtly incorporates these words/concepts into the entity name and backstory")
        print("4. This creates more diverse and unexpected entity characteristics")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 