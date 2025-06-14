from flask import Flask, request, jsonify, send_file, after_this_request
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from datetime import datetime
from fpdf2 import FPDF
import os
import tempfile

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

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Aviation Safety Assistant - Rapport de Sécurité', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(data):
    pdf = PDF()
    pdf.add_page()
    
    # Configuration
    pdf.set_font('Arial', '', 11)
    left_margin = 20
    
    # En-tête avec date et ID
    report_id = f"ASA-{datetime.now().strftime('%Y%m%d%H%M')}"
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, "Rapport d'Étude de Risques", 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, f"Date de génération : {data['timestamp']}", 0, 1, 'L')
    pdf.cell(0, 5, f"Version : {report_id}", 0, 1, 'L')
    pdf.ln(5)

    # Événement
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, "Événement Indésirable :", 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, data['query'])
    pdf.ln(5)

    # Cas similaire et détails
    if data.get('similar_cases') and len(data['similar_cases']) > 0:
        similar_case = data['similar_cases'][0]
        
        if similar_case.get('classification'):
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 7, "Classification :", 0, 1, 'L')
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 7, similar_case['classification'])
            pdf.ln(5)

        if similar_case.get('consequence'):
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 7, "Conséquences :", 0, 1, 'L')
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 7, similar_case['consequence'])
            pdf.ln(5)

        if similar_case.get('worst_case'):
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 7, "Pire Scénario Considéré :", 0, 1, 'L')
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(220, 53, 69)  # Rouge pour le pire scénario
            pdf.multi_cell(0, 7, similar_case['worst_case'])
            pdf.set_text_color(0, 0, 0)  # Retour au noir
            pdf.ln(5)

    # Évaluation des risques
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, "Évaluation des Risques :", 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f"Sévérité : {data['severity']}", 0, 1, 'L')
    pdf.cell(0, 7, f"Probabilité : {data['probability']}", 0, 1, 'L')
    pdf.cell(0, 7, f"Niveau de Risque : {data['risk_level']}", 0, 1, 'L')
    pdf.ln(5)

    # Mesures d'atténuation
    if data.get('measures'):
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, "Mesures d'atténuation :", 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        
        for i, measure in enumerate(data['measures'], 1):
            pdf.multi_cell(0, 7, f"{i}. {measure}")
        pdf.ln(5)

    # Échéance
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 7, "Échéance :", 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    echeance = {
        'A': "immédiatement plutôt que possible",
        'B': "Actions implémentées sous 1 mois",
        'C': "Actions implémentées sous 3 mois",
        'D': "suivi continue"
    }.get(data['risk_level'], "non définie")
    pdf.cell(0, 7, echeance, 0, 1, 'L')
    pdf.ln(5)

    # Tableau d'approbation
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(60, 10, "APPROUVÉ PAR", 1)
    pdf.cell(60, 10, "DATE", 1)
    pdf.cell(60, 10, "SIGNATURE", 1)
    pdf.ln()
    pdf.set_font('Arial', '', 11)
    pdf.cell(60, 10, data['user'], 1)
    pdf.cell(60, 10, data['timestamp'], 1)
    pdf.cell(60, 10, "", 1)

    # Création d'un fichier temporaire
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = temp_file.name
    pdf.output(pdf_path)
    
    return pdf_path

def clean_text(text):
    """Clean and normalize text"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

@app.route("/generate-pdf", methods=["POST"])
def create_pdf():
    try:
        data = request.json
        pdf_path = generate_pdf(data)
        
        @after_this_request
        def cleanup(response):
            try:
                os.remove(pdf_path)
            except Exception as e:
                print(f"Error cleaning up PDF file: {e}")
            return response
            
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Rapport_Securite_ASA-{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chatbot", methods=["POST"])
def process_query():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400
            
        query = data['query'].strip()
        probability = data.get('probability', 'P0')
        timestamp = data.get('timestamp', '2025-06-13 22:15:03')
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
                    'severity': str(df.iloc[idx]['Gravité (S0-S5)']),
                    'consequence': str(df.iloc[idx]['conséquence']),
                    'worst_case': str(df.iloc[idx]['Pire scénario considéré']),
                    'classification': str(df.iloc[idx].get('Classification', ''))
                })
        
        best_match = similar_cases[0] if similar_cases else None
        severity = best_match['severity'] if best_match else 'S0'
        
        response_data = {
            "status": "success",
            "response": {
                "query": query,
                "severity": severity,
                "probability": probability,
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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
