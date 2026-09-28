# ============================================
# TEE Layer - Trusted Execution Environment
# Simulated secure processing layer
# Supports: Ollama (Local) + Gemini + Groq (Cloud)
# ============================================

import hashlib
import re
import os
import requests
from datetime import datetime


class TEELayer:
    """
    Simulated Trusted Execution Environment.
    - PII detect karta hai
    - Sensitive data anonymize karta hai
    - Local ya Cloud AI ka decision leta hai
    - Audit log maintain karta hai
    """
    
    def __init__(self):
        self.audit_log = []
        self.local_ai_available = self._check_ollama()
        self.groq_client = self._init_groq()
    
    # ========================================
    # CHECK: Ollama running hai?
    # ========================================
    def _check_ollama(self):
        """Local Ollama AI chal raha hai ya nahi"""
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            return r.status_code == 200
        except:
            return False
    
    # ========================================
    # INIT: Groq client setup
    # ========================================
    def _init_groq(self):
        """Groq client initialize karta hai (agar API key hai)"""
        try:
            api_key = None
            
            # Pehle Streamlit secrets try karo
            try:
                import streamlit as st
                api_key = st.secrets.get("GROQ_API_KEY")
            except:
                pass
            
            # Phir environment variable
            if not api_key:
                api_key = os.getenv("GROQ_API_KEY")
            
            if api_key:
                from groq import Groq
                return Groq(api_key=api_key)
        except Exception as e:
            pass
        return None
    
    # ========================================
    # DETECT: PII dhundo
    # ========================================
    def detect_pii(self, text):
        """Text mein sensitive info detect karta hai"""
        patterns = {
            "email": r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
            "phone": r"\b[6-9]\d{9}\b",
            "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
            "aadhaar": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
        }
        found = []
        for name, pattern in patterns.items():
            if re.search(pattern, text):
                found.append(name)
        return found
    
    # ========================================
    # ANONYMIZE: Sensitive data replace
    # ========================================
    def anonymize(self, text):
        """Sensitive data ko placeholder se replace karta hai"""
        text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[EMAIL]", text)
        text = re.sub(r"\b[6-9]\d{9}\b", "[PHONE]", text)
        text = re.sub(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", "[CARD]", text)
        text = re.sub(r"\b\d{4}\s?\d{4}\s?\d{4}\b", "[AADHAAR]", text)
        return text
    
    # ========================================
    # HASH: Data fingerprint
    # ========================================
    def hash_data(self, text):
        """Data ka SHA256 hash (audit ke liye)"""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
    
    # ========================================
    # ROUTE: Local ya Cloud decide karo
    # ========================================
    def decide_route(self, text, force_local=False):
        """Local ya Cloud decide karo"""
        if force_local and self.local_ai_available:
            return "local"
        pii = self.detect_pii(text)
        if pii and self.local_ai_available:
            return "local"
        if not self.local_ai_available:
            return "cloud"
        return "cloud"
    
    # ========================================
    # LOCAL AI: Ollama se response
    # ========================================
    def query_local_ai(self, prompt, model="qwen2.5:0.5b"):
        """Local Ollama AI se response (CPU only)"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_gpu_layers": 0,
                        "num_thread": 4,
                        "temperature": 0.7
                    }
                },
                timeout=120
            )
            return response.json().get("response", "No response")
        except Exception as e:
            return f"Local AI Error: {e}"
    
    # ========================================
    # CLOUD AI: Groq se response (with fallback)
    # ========================================
    def query_groq(self, prompt, model="openai/gpt-oss-120b"):
        """
        Groq Cloud AI se response.
        Free tier: 14,400 requests/day
        Auto-fallback if primary model fails.
        """
        if not self.groq_client:
            return None
        
        # Fallback chain: try models in priority order
        models_to_try = [
            "openai/gpt-oss-120b",      # Best quality
            "openai/gpt-oss-20b",       # Faster, lighter
            "qwen/qwen3.6-27b",         # Alternative
        ]
        
        for m in models_to_try:
            try:
                response = self.groq_client.chat.completions.create(
                    model=m,
                    messages=[
                        {"role": "system", "content": "You are a cyber security expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1024
                )
                return response.choices[0].message.content
            except Exception as e:
                # Agar yeh model nahi mila, next try karo
                if "model_not_found" in str(e) or "does not exist" in str(e):
                    continue
                # Doosre errors (rate limit, etc.) — return error
                return f"Groq Error: {e}"
        
        return None  # Sab models fail ho gaye — Gemini pe fallback karega
    
    # ========================================
    # PROCESS: Main TEE pipeline
    # ========================================
    def process(self, prompt, force_local=False):
        """Main TEE pipeline"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        pii_found = self.detect_pii(prompt)
        route = self.decide_route(prompt, force_local)
        
        if route == "cloud":
            safe_prompt = self.anonymize(prompt)
        else:
            safe_prompt = prompt
        
        data_hash = self.hash_data(prompt)
        
        log_entry = {
            "timestamp": timestamp,
            "hash": data_hash,
            "pii_found": pii_found if pii_found else ["None"],
            "route": route,
            "anonymized": "Yes" if route == "cloud" and pii_found else "No"
        }
        self.audit_log.append(log_entry)
        
        return {
            "route": route,
            "safe_prompt": safe_prompt,
            "pii_found": pii_found,
            "hash": data_hash,
            "log": log_entry
        }