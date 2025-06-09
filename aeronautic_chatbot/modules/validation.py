# -*- coding: utf-8 -*-
from typing import Dict
import re

class RequestValidator:
    def __init__(self):
        """Initialize request validator"""
        self.required_fields = ['query']
        
    def validate_request(self, request_data: Dict) -> bool:
        """Validate incoming request"""
        # Check if request data exists
        if not request_data:
            return False
            
        # Check required fields
        if not all(field in request_data for field in self.required_fields):
            return False
            
        # Validate query
        query = request_data.get('query', '')
        if not self.validate_query(query):
            return False
            
        return True
        
    def validate_query(self, query: str) -> bool:
        """Validate query string"""
        # Check if query is empty or too short
        if not query or len(query.strip()) < 3:
            return False
            
        # Check if query is too long (prevent abuse)
        if len(query) > 1000:
            return False
            
        # Check for basic SQL injection attempts
        if re.search(r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP)\b)', query, re.IGNORECASE):
            return False
            
        return True
        
    def sanitize_input(self, text: str) -> str:
        """Sanitize input text"""
        # Remove potential HTML
        text = re.sub(r'<[^>]*>', '', text)
        
        # Remove special characters but keep French accents
        text = re.sub(r'[^\w\s\u00C0-\u017F]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()