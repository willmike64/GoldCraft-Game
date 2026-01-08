import streamlit as st
from .firebase_service import get_firebase_service
import datetime

class Analytics:
    def __init__(self):
        self.firebase_service = get_firebase_service()
    
    def log_action(self, email: str, action: str, data: dict = None):
        """Log user action to Firebase"""
        try:
            if self.firebase_service and self.firebase_service.db:
                self.firebase_service.db.collection('analytics').add({
                    'email': email,
                    'action': action,
                    'data': data or {},
                    'timestamp': datetime.datetime.now()
                })
        except:
            pass
    
    def log_login(self, email: str):
        """Log user login"""
        self.log_action(email, 'login')

analytics = Analytics()