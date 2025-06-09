from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

def get_utc_timestamp():
    return datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")

# Initialize components
try:
    print("\nLoading dataset...")
    df = pd.read_csv('data/bdd_ia.csv', encoding='utf-8')
    
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        stop_words=['le', 'la', 'les', 'de', 'des', 'du']
    )
    
    print("Preparing text vectors...")
    incident_texts = df['Evenement Indésirable'].fillna('').astype(str)
    incident_vectors = vectorizer.fit_transform(incident_texts)
    
    print(f"\n🚀 Aviation Safety Chatbot initialized successfully")
    print(f"Loaded {len(df)} safety cases")
    
except Exception as e:
    print(f"\n❌ Error during initialization: {str(e)}")
    raise SystemExit(1)

def clean_text(text):
    """Clean and normalize text"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_consequences(text):
    """Parse numbered consequences into a list"""
    if pd.isna(text):
        return []
    items = re.split(r'\d+\.', text)
    return [item.strip() for item in items if item.strip()]

@app.route("/chatbot", methods=["POST"])
def process_query():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400
            
        query = data['query'].strip()
        cleaned_query = clean_text(query)
        query_vector = vectorizer.transform([cleaned_query])
        
        similarities = np.dot(incident_vectors, query_vector.T).toarray().flatten()
        top_indices = similarities.argsort()[-5:][::-1]
        
        similar_cases = []
        for idx in top_indices:
            if similarities[idx] > 0.1:
                similar_cases.append({
                    'id': int(df.iloc[idx]['ID']),
                    'incident': str(df.iloc[idx]['Evenement Indésirable']),
                    'similarity': float(similarities[idx]),
                    'severity': str(df.iloc[idx]['Gravité (S0-S5)']),
                    'consequence': str(df.iloc[idx]['conséquence']),
                    'worst_case': str(df.iloc[idx]['Pire scénario considéré'])
                })
        
        best_match = similar_cases[0] if similar_cases else None
        
        response_data = {
            "status": "success",
            "response": {
                "query": query,
                "severity": best_match['severity'] if best_match else 'S0',
                "consequences": parse_consequences(best_match['consequence']) if best_match else [],
                "worst_case": best_match['worst_case'] if best_match else "",
                "similar_cases": [
                    {
                        "id": case['id'],
                        "incident": case['incident'],
                        "similarity": case['similarity'],
                        "severity": case['severity'],
                        "consequences": parse_consequences(case['consequence']),
                        "worst_case": case['worst_case']
                    } for case in similar_cases[:3]
                ]
            },
            "metadata": {
                "timestamp": get_utc_timestamp(),
                "user": "sihem97"
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "metadata": {
                "timestamp": get_utc_timestamp(),
                "user": "sihem97"
            }
        }), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": get_utc_timestamp(),
        "user": "sihem97"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)