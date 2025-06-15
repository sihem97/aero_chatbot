from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

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
    
    print(f"\n🚀 Aviation Safety Assistant initialized successfully")
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

def get_risk_level(severity, probability):
    """Calculate risk level based on severity and probability"""
    risk_matrix = {
        'P5': {'S5': 'A', 'S4': 'A', 'S3': 'B', 'S2': 'C', 'S1': 'C', 'S0': 'D'},
        'P4': {'S5': 'A', 'S4': 'A', 'S3': 'B', 'S2': 'C', 'S1': 'C', 'S0': 'D'},
        'P3': {'S5': 'A', 'S4': 'B', 'S3': 'C', 'S2': 'C', 'S1': 'D', 'S0': 'D'},
        'P2': {'S5': 'A', 'S4': 'B', 'S3': 'C', 'S2': 'C', 'S1': 'D', 'S0': 'D'},
        'P1': {'S5': 'B', 'S4': 'B', 'S3': 'C', 'S2': 'D', 'S1': 'D', 'S0': 'D'},
        'P0': {'S5': 'C', 'S4': 'C', 'S3': 'D', 'S2': 'D', 'S1': 'D', 'S0': 'D'}
    }
    return risk_matrix.get(probability, {}).get(severity, 'D')

@app.route("/chatbot", methods=["POST"])
def process_query():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400
            
        query = data['query'].strip()
        probability = data.get('probability', 'P0')
        timestamp = data.get('timestamp', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        user = data.get('user', 'marouuuuuux')
        
        cleaned_query = clean_text(query)
        query_vector = vectorizer.transform([cleaned_query])
        
        similarities = np.dot(incident_vectors, query_vector.T).toarray().flatten()
        top_indices = similarities.argsort()[-5:][::-1]
        
        similar_cases = []
        for idx in top_indices:
            if similarities[idx] > 0.1:
                similar_cases.append({
                    'incident': str(df.iloc[idx]['Evenement Indésirable']),
                    'classification': str(df.iloc[idx]['classification']),  # Ajout de la classification
                    'severity': str(df.iloc[idx]['Gravité (S0-S5)']),
                    'consequence': str(df.iloc[idx]['conséquence']),
                    'worst_case': str(df.iloc[idx]['Pire scénario considéré'])
                })
        
        best_match = similar_cases[0] if similar_cases else None
        classification = best_match['classification'] if best_match else "Non classifié"
        severity = best_match['severity'] if best_match else 'S0'
        risk_level = get_risk_level(severity, probability)
        
        response_data = {
            "status": "success",
            "response": {
                "query": query,
                "classification": classification,
                "severity": severity,
                "probability": probability,
                "risk_level": risk_level,
                "similar_cases": similar_cases[:3],
                "timestamp": timestamp,
                "user": user
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in process_query: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        "user": "marouuuuuux"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
