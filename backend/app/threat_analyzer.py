import asyncio
import re
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class ThreatAnalyzer:
    def __init__(self):
        """Initialize threat analyzer with local phishing detection"""
        self.phishing_patterns = self._load_phishing_patterns()
        self.phishing_keywords = {
            "urgent": 10, "immediately": 10, "confirm": 8, "verify": 8,
            "click": 7, "link": 7, "account": 9, "security": 8,
            "suspended": 9, "locked": 9, "unusual activity": 8,
            "update": 7, "password": 10, "refund": 7, "payment": 7,
            "invoice": 6, "due": 6, "action required": 9, "suspend": 9,
            "device": 8, "unauthorized": 9, "compromise": 9
        }
    
    def _load_phishing_patterns(self):
        """Load known phishing messages from file"""
        try:
            phishing_file = Path(__file__).parent / "phishing_messages.txt"
            if phishing_file.exists():
                with open(phishing_file, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Warning: Could not load phishing patterns: {e}")
        return []
    
    def _calculate_similarity(self, text1, text2):
        """Calculate word overlap similarity between texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0
    
    def _analyze_phishing_score(self, text):
        """Calculate phishing risk score (0-100) locally"""
        text_lower = text.lower()
        score = 0
        detected_keywords = []
        
        # Check keyword indicators
        for keyword, weight in self.phishing_keywords.items():
            if keyword in text_lower:
                score += weight
                detected_keywords.append(keyword)
        
        # Check against known phishing patterns
        max_similarity = 0
        for pattern in self.phishing_patterns:
            similarity = self._calculate_similarity(text, pattern)
            max_similarity = max(max_similarity, similarity)
        
        pattern_score = int(max_similarity * 40)
        score += pattern_score
        
        # Check for suspicious patterns
        if "[link]" in text_lower or "click here" in text_lower:
            score += 15
            detected_keywords.append("suspicious link")
        
        if "$" in text and ("fee" in text_lower or "payment" in text_lower):
            score += 10
            detected_keywords.append("suspicious payment request")
        
        # Cap score at 100
        score = min(score, 100)
        
        return score, detected_keywords
    
    async def analyze_message(self, sender, text):
        """Analyze message for phishing/social engineering"""
        try:
            if not text and not sender:
                return {
                    "risk_score": 20,
                    "verdict": "allow",
                    "reasons": ["Insufficient data for analysis"],
                    "summary": "Not enough information provided."
                }
            
            # Analyze phishing indicators locally
            analyze_text = text if text else sender if sender else ""
            risk_score, keywords = self._analyze_phishing_score(analyze_text)
            
            # Determine verdict
            if risk_score >= 70:
                verdict = "block"
            elif risk_score >= 40:
                verdict = "review"
            else:
                verdict = "allow"
            
            # Generate reasons
            reasons = []
            if keywords:
                unique_keywords = list(set(keywords))[:3]
                reasons.append(f"Detected suspicious keywords: {', '.join(unique_keywords)}")
            if risk_score >= 40:
                reasons.append(f"Similarity to known phishing patterns detected")
            if not reasons:
                reasons.append("Low phishing probability - content appears legitimate")
            
            # Create summary
            if verdict == "block":
                summary = f"HIGH RISK: This message exhibits {risk_score}% similarity to known phishing attacks. BLOCK recommended."
            elif verdict == "review":
                summary = f"MEDIUM RISK: This message contains suspicious elements ({risk_score}%). Manual review recommended."
            else:
                summary = f"LOW RISK: This message appears legitimate ({risk_score}% risk score)."
            
            return {
                "risk_score": risk_score,
                "verdict": verdict,
                "reasons": reasons[:3],
                "summary": summary
            }
        except Exception as e:
            print(f"Error in analyze_message: {str(e)}")
            return {
                "risk_score": 30,
                "verdict": "review",
                "reasons": ["Analysis encountered an error"],
                "summary": "Please try again with a different message."
            }
    
    async def analyze_transaction(self, user_id, amount, merchant):
        """Analyze transaction for anomalies"""
        try:
            if not user_id or amount == 0:
                return {
                    "risk_score": 15,
                    "verdict": "allow",
                    "reasons": ["Standard transaction"],
                    "summary": "Transaction data provided for analysis."
                }
            
            # Simple heuristic-based transaction analysis
            risk_score = 15  # Base risk
            reasons = []
            
            # Suspicious amounts
            if amount > 50000:
                risk_score += 35
                reasons.append(f"Very large transaction amount: ${amount:,.2f}")
            elif amount > 10000:
                risk_score += 20
                reasons.append(f"Large transaction amount: ${amount:,.2f}")
            
            # Suspicious merchants
            suspicious_merchants = ["unknown", "gas station", "foreign", "atm", "casino", "wire transfer"]
            merchant_lower = merchant.lower() if merchant else ""
            if any(s in merchant_lower for s in suspicious_merchants):
                risk_score += 25
                reasons.append(f"Suspicious merchant type detected: {merchant}")
            
            if not reasons:
                reasons.append(f"Transaction to {merchant or 'Unknown Merchant'} appears normal")
            
            # Cap score
            risk_score = min(risk_score, 100)
            
            verdict = "block" if risk_score >= 70 else "review" if risk_score >= 40 else "allow"
            
            if verdict == "block":
                summary = f"HIGH RISK: Transaction flagged for review due to unusual amount or merchant ({risk_score}% risk)."
            elif verdict == "review":
                summary = f"MEDIUM RISK: Transaction exhibits some unusual characteristics ({risk_score}% risk). Manual verification recommended."
            else:
                summary = f"LOW RISK: Transaction appears normal based on amount and merchant ({risk_score}% risk)."
            
            return {
                "risk_score": risk_score,
                "verdict": verdict,
                "reasons": reasons[:3],
                "summary": summary
            }
        except Exception as e:
            print(f"Error in analyze_transaction: {str(e)}")
            return {
                "risk_score": 25,
                "verdict": "review",
                "reasons": ["Analysis encountered an error"],
                "summary": "Please provide valid transaction details."
            }
    
    async def analyze_crypto_wallet(self, wallet_address):
        """Analyze crypto wallet for suspicious activity"""
        # 1. Valkey "Hot List" Check
        if self.db.exists(f"malicious_wallet:{wallet_address}"):
            return {"status": "CRITICAL", "reason": "Wallet linked to known hack."}
        
        # 2. Valkey Reputation Check
        suspicious_score = self.db.get(f"wallet_reputation:{wallet_address}")
        if suspicious_score and float(suspicious_score) > 0.8:
            return {"status": "HIGH_RISK", "reason": f"Known suspicious activity. Risk score: {suspicious_score}"}
        
        client = BackboardClient(api_key=self.api_key)
        thread = await client.create_thread(self.assistant_id)
        
        prompt = f"Assess risk for crypto wallet {wallet_address}."
        analysis = await client.add_message(
            thread_id=thread.thread_id,
            content=prompt,
            llm_provider="openai",
            model_name="gpt-4o",
            stream=False
        )
        
        return analysis.content
    
    async def triage_threat(self, input_data):
        """Main entry point for threat analysis"""
        try:
            if input_data['type'] == 'message':
                sender = input_data['content']['sender']
                text = input_data['content']['body']
                return await self.analyze_message(sender, text)
            
            elif input_data['type'] == 'transaction':
                user_id = input_data['content']['user_id']
                amount = input_data['content']['amount']
                merchant = input_data['content']['merchant']
                return await self.analyze_transaction(user_id, amount, merchant)
        except Exception as e:
            print(f"Error in triage_threat: {str(e)}")
            return {
                "risk_score": 30,
                "verdict": "review",
                "reasons": ["Analysis failed"],
                "summary": "Unable to complete analysis. Please try again."
            }