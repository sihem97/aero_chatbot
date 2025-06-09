import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from typing import Dict, List

class NLPProcessor:
    def __init__(self, df: pd.DataFrame):
        """Initialize NLP processor with dataset"""
        self.df = df
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            stop_words=['le', 'la', 'les', 'de', 'des', 'du']
        )
        
        # Prepare vectors from incident descriptions
        incident_texts = self.df['Evenement Indésirable'].fillna('').astype(str).apply(self.clean_text)
        self.incident_vectors = self.vectorizer.fit_transform(incident_texts)
        print(f"Vectorizer initialized with {len(self.vectorizer.vocabulary_)} features")
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not isinstance(text, str):
            return ""
            
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
        
    def process_query(self, query: str) -> Dict:
        """Process user query and find similar cases"""
        try:
            # Clean query
            cleaned_query = self.clean_text(query)
            print(f"Cleaned query: {cleaned_query}")
            
            # Vectorize query
            query_vector = self.vectorizer.transform([cleaned_query])
            
            # Calculate similarities
            similarities = np.dot(
                self.incident_vectors, 
                query_vector.T
            ).toarray().flatten()
            
            # Get top matches
            top_indices = similarities.argsort()[-5:][::-1]
            
            similar_cases = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    similar_cases.append({
                        'id': int(self.df.index[idx]),
                        'incident': str(self.df.iloc[idx]['Evenement Indésirable']),
                        'similarity': float(similarities[idx]),
                        'severity': str(self.df.iloc[idx].get('Gravité (S0-S5)', 'S0')),
                        'solution': str(self.df.iloc[idx].get('conséquence', ''))
                    })
            
            print(f"Found {len(similar_cases)} similar cases")
            return {
                'similar_cases': similar_cases,
                'query_vector': query_vector
            }
            
        except Exception as e:
            print(f"Error in NLP processing: {str(e)}")
            raise