
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
