
import asyncio
from backboard import BackboardClient
import valkey
import os
from .getassistantid import get_assistant_id
from dotenv import load_dotenv

load_dotenv()

class ThreatAnalyzer:
    def __init__(self):
        self.assistant_id = get_assistant_id()
        self.api_key = os.getenv("BACKBOARD_API_KEY")
        self.db = valkey.Valkey(host="localhost", port=6379, db=0)
    
    async def analyze_message(self, sender, text):
        """Analyze message for phishing/social engineering"""
        # Check blocklist
        if self.db.sismember("global_blocklist", sender):
            return {"status": "BLOCKED", "reason": "Known malicious sender."}
        
        client = BackboardClient(api_key=self.api_key)
        thread = await client.create_thread(self.assistant_id)
        
        rag_context = await client.add_message(
            thread_id = thread.thread_id,
            content=f"What are the top 3 messages which have similar content to: {text}?",
            stream=False
        )
        
        prompt = f"Analyze this text for social engineering based on known scams: {text}\nContext: {rag_context}"
        analysis = await client.add_message(
            thread_id=thread.thread_id,
            content=prompt,
            llm_provider="openai",
            model_name="gpt-4o",
            stream=False
        )
        
        return analysis.content
    
    async def analyze_transaction(self, user_id, amount, merchant):
        """Analyze transaction for anomalies"""
        avg_spend = float(self.db.get(f"user:{user_id}:avg_spend") or 10)
        
        if amount > (avg_spend * 10):
            client = BackboardClient(api_key=self.api_key)
            thread = await client.create_thread(self.assistant_id)
            
            prompt = f"User usually spends ${avg_spend}. Now spending ${amount} at {merchant}. Is this risky?"
            analysis = await client.add_message(
                thread_id=thread.thread_id,
                content=prompt,
                llm_provider="openai",
                model_name="gpt-4o",
                stream=False
            )
            return analysis.content
        
        return {"status": "SAFE", "reason": "Within normal spending limits."}
    
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
        if input_data['type'] == 'message':
            sender = input_data['content']['sender']
            text = input_data['content']['body']
            return await self.analyze_message(sender, text)
        
        elif input_data['type'] == 'transaction':
            user_id = input_data['content']['user_id']
            amount = input_data['content']['amount']
            merchant = input_data['content']['merchant']
            return await self.analyze_transaction(user_id, amount, merchant)
        
        elif input_data['type'] == 'crypto':
            wallet_address = input_data['content']['address']
            return await self.analyze_crypto_wallet(wallet_address)
        
        else:
            raise ValueError(f"Unknown threat type: {input_data['type']}")
