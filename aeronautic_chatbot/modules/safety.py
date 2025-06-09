# -*- coding: utf-8 -*-
from typing import Dict, List
import re

class SafetyAnalyzer:
    def __init__(self, df):
        """Initialize safety analyzer with dataset"""
        self.df = df
        self.severity_mapping = {
            'S0': 0, 'S1': 1, 'S2': 2, 'S3': 3, 'S4': 4, 'S5': 5
        }
        
    def clean_severity(self, severity: str) -> str:
        """Clean severity string to standard format"""
        if pd.isna(severity):
            return 'S0'
        return re.split(r'\s*–\s*', str(severity))[0]
        
    def analyze_incident(self, query: str, similar_cases: List[Dict]) -> Dict:
        """Analyze incident and provide recommendations"""
        if not similar_cases:
            return {
                'severity': 'S0',
                'immediate_actions': ['No similar cases found'],
                'recommendations': ['Consult safety officer'],
                'risk_level': 'Unknown'
            }
            
        # Get most severe similar case
        max_severity = max(
            [self.severity_mapping[self.clean_severity(case['severity'])] 
             for case in similar_cases]
        )
        severity = f'S{max_severity}'
        
        # Get immediate actions from most similar case
        immediate_actions = []
        if similar_cases[0]['solution']:
            immediate_actions = [
                action.strip() 
                for action in similar_cases[0]['solution'].split('.')
                if action.strip()
            ]
        
        # Generate recommendations
        recommendations = self.generate_recommendations(
            severity, 
            similar_cases
        )
        
        return {
            'severity': severity,
            'immediate_actions': immediate_actions,
            'recommendations': recommendations,
            'risk_level': self.get_risk_level(severity)
        }
        
    def get_risk_level(self, severity: str) -> str:
        """Map severity to risk level"""
        risk_mapping = {
            'S0': 'Minimal',
            'S1': 'Low',
            'S2': 'Moderate',
            'S3': 'Significant',
            'S4': 'High',
            'S5': 'Critical'
        }
        return risk_mapping.get(severity, 'Unknown')
        
    def generate_recommendations(self, severity: str, similar_cases: List[Dict]) -> List[str]:
        """Generate safety recommendations based on severity and similar cases"""
        recommendations = []
        
        # Add severity-based recommendations
        if severity in ['S4', 'S5']:
            recommendations.append("Immediate action required")
            recommendations.append("Notify safety officer immediately")
            recommendations.append("Document all actions taken")
            
        # Add case-based recommendations
        if similar_cases:
            best_match = similar_cases[0]
            if best_match['solution']:
                recommendations.extend([
                    f"Based on similar incident (ID: {best_match['id']}): {action.strip()}"
                    for action in best_match['solution'].split('.')
                    if action.strip()
                ])
                
        return recommendations