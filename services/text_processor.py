import re
import string

# Standard English Stopwords for lightweight NLP
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

def normalize_text(text: str) -> str:
    """
    Normalizes text for NLP processing:
    - Lowercase conversion
    - Normalize special characters while preserving symbols in C++, C#, .NET, Node.js
    - Whitespace collapse
    """
    if not text:
        return ""
    
    text = text.lower()
    
    # Replace newlines/tabs with spaces
    text = re.sub(r'[\r\n\t]+', ' ', text)
    
    # Replace non-printable characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    # Collapse consecutive spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_punctuation_keep_tech(text: str) -> str:
    """
    Removes general punctuation while preserving technical tokens like c++, c#, .js, etc.
    """
    normalized = normalize_text(text)
    # Replace characters that are not alphanumeric, spaces, or valid tech symbols (+, #, ., -)
    cleaned = re.sub(r'[^a-z0-9\s\+\#\.\-]', ' ', normalized)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def tokenize_words(text: str, remove_stopwords: bool = True) -> list[str]:
    """
    Splits text into words and optionally removes stopwords.
    """
    cleaned = clean_punctuation_keep_tech(text)
    tokens = cleaned.split()
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1 or t in {'c', 'r'}]
    return tokens

def generate_ngrams(tokens: list[str], n: int) -> list[str]:
    """
    Generates n-grams from token list.
    """
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
