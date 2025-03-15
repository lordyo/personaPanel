#!/usr/bin/env python3
"""
Extract interesting words from the NLTK Gutenberg corpus.
This script selects words that would make good bisociative fuel for entity generation.
"""

import os
import json
import random
import re
import string
from collections import Counter
import nltk
from nltk.corpus import gutenberg, stopwords
from nltk.tokenize import RegexpTokenizer

# Ensure necessary NLTK data is downloaded
nltk.download('gutenberg', quiet=True)
nltk.download('punkt', quiet=True)  
nltk.download('stopwords', quiet=True)

# Define paths
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(REPO_ROOT, "config")
BISOCIATIVE_WORDS_PATH = os.path.join(CONFIG_DIR, "bisociative_words.json")

# Load existing words just to report how many we're replacing
try:
    with open(BISOCIATIVE_WORDS_PATH, 'r') as f:
        data = json.load(f)
        existing_words = data.get("words", [])
    print(f"Found {len(existing_words)} existing bisociative words that will be replaced")
except Exception as e:
    print(f"Could not load existing words: {str(e)}")
    existing_words = []

# Get all available files from gutenberg corpus
gutenberg_files = gutenberg.fileids()
print(f"Found {len(gutenberg_files)} texts in the Gutenberg corpus")

# Get English stopwords from NLTK
stop_words = set(stopwords.words('english'))
print(f"Loaded {len(stop_words)} stopwords")

# Add more common words to exclude
ADDITIONAL_EXCLUDE_WORDS = set([
    'would', 'could', 'should', 'said', 'made', 'went', 'come', 'came', 'going', 'gone',
    'know', 'knew', 'known', 'think', 'thought', 'things', 'thing', 'something', 'anything',
    'nothing', 'everything', 'away', 'back', 'much', 'many', 'more', 'most', 'still', 'well',
    'else', 'even', 'upon', 'mine', 'thine', 'thee', 'thou', 'thy', 'doth', 'hath', 'shall',
    'however', 'therefore', 'though', 'through', 'always', 'never', 'often', 'sometimes',
    'usually', 'might', 'must', 'shall', 'which', 'whose', 'whom', 'whoever', 'whatever',
    'till', 'until', 'whenever', 'wherever', 'indeed', 'perhaps', 'rather', 'whether',
    'during', 'while', 'then', 'thus', 'here', 'there', 'where', 'when', 'what', 'that'
])

# Combine stopwords with additional exclusions
EXCLUDE_WORDS = stop_words.union(ADDITIONAL_EXCLUDE_WORDS)
print(f"Total words to exclude: {len(EXCLUDE_WORDS)}")

# Create tokenizer that splits on non-alphabetic characters
tokenizer = RegexpTokenizer(r'[a-zA-Z]+')

# Process all texts and extract words
all_words = []
for file_id in gutenberg_files:
    print(f"Processing {file_id}...")
    text = gutenberg.raw(file_id)
    # Use RegexpTokenizer instead of word_tokenize to avoid punkt issues
    tokens = tokenizer.tokenize(text.lower())
    
    # Filter tokens to only include words (no punctuation, numbers, etc.)
    words = [word for word in tokens if word.isalpha() and len(word) > 3]
    all_words.extend(words)

# Count word frequencies
word_counts = Counter(all_words)
print(f"Found {len(word_counts)} unique words")

# Filter words
filtered_words = []
for word, count in word_counts.items():
    # Include words that:
    # 1. Are not in the exclude list
    # 2. Are between 4 and 12 characters (not too short, not too long)
    # 3. Appear at least 5 times but not more than 500 times (not too rare, not too common)
    if (word.lower() not in EXCLUDE_WORDS and 
        4 <= len(word) <= 12 and 
        5 <= count <= 500):
        filtered_words.append(word)

print(f"After filtering, found {len(filtered_words)} suitable words")

# Randomize and select 2000 words (or all if less than 2000)
random.shuffle(filtered_words)
words_to_select = min(2000, len(filtered_words))
selected_words = filtered_words[:words_to_select]
print(f"Selected {len(selected_words)} words from Gutenberg corpus")

# Write to file, replacing the old list completely
with open(BISOCIATIVE_WORDS_PATH, 'w') as f:
    json.dump({"words": selected_words}, f, indent=2)

print(f"Updated bisociative words file at {BISOCIATIVE_WORDS_PATH}")

# Print some examples
print("\nSample of selected words:")
for i in range(0, min(40, len(selected_words)), 4):
    row = selected_words[i:i+4]
    print(", ".join(row)) 