# -*- coding: utf-8 -*-
from datetime import datetime
import uuid
from typing import Dict, List

class ReportGenerator:
    def __init__(self):
        """Initialize report generator"""
        self.report_counter = 0
        
    def create_report(self, query: str, analysis: Dict, similar_cases: List[Dict]) -> Dict:
        """Generate incident report"""
        # Generate unique report ID
        timestamp = datetime.utcnow()
        report_id = f"INC-{timestamp.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Create report
        report = {
            "report_id": report_id,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "incident_description": query,
            "severity": analysis['severity'],
            "risk_level": analysis['risk_level'],
            "immediate_actions": analysis['immediate_actions'],
            "recommendations": analysis['recommendations'],
            "similar_cases": [
                {
                    "id": case['id'],
                    "incident": case['incident'],
                    "similarity": case['similarity']
                }
                for case in similar_cases[:3]
            ],
            "status": "open"
        }
        
        # Store report (in a real application, this would go to a database)
        self.store_report(report)
        
        return report
        
    def store_report(self, report: Dict) -> None:
        """Store report - placeholder for database integration"""
        # In a real application, this would store to a database
        self.report_counter += 1
        print(f"Report {report['report_id']} stored successfully")