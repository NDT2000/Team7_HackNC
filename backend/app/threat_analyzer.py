import json
import asyncio
from backboard import BackboardClient
import valkey
import os
from .getassistantid import get_assistant_id
from dotenv import load_dotenv
from google import genai

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

        message = json.loads(analysis.content)

        confidence_score = message["confidence_score"]

        client = genai.Client(api_key = os.getenv("GEMINI_API_KEY"))

        response = client.models.generate_content(model = "gemini-3-flash-preview",
                contents = f"""Consider yourself to be a natural langauge analyst. For the following text: {text}, I received
                            an analysis: {analysis.content}. Validate the output. 
                            If you agree, just say yes.
                            If you do not, give the output in this format:
                            {{"confidence score": confidence score (float datatype)
                             "explaination": explaination (string datatype)}}
                            Limit your response to 600 characters. Note that the confidence score indicates the percentage
                            of the transaction being not fraudulent.""")
        
        gemini_resp = response.text

        if gemini_resp != "yes":
            gem_message = json.loads(gemini_resp)
            confidence_score = gem_message["confidence score"]

        if confidence_score < 0.4:
            self.db.sadd("global_blocklist", sender)
        
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

            message = json.loads(analysis.content)

            client = genai.Client(api_key = os.getenv("GEMINI_API_KEY"))

            confidence_score = message["confidence_score"]

            response = client.models.generate_content(model = "gemini-3-flash-preview",
                    contents = f"""Consider yourself to be a Bank Manager. For the following receiver: {merchant}, and 
                                amount: {amount}, I received an analysis: {analysis.content}. Validate the output. 
                                If you agree, just say yes.
                                If you do not, give the output in this format:
                                {{"confidence score": confidence score (float datatype)
                                "explaination": explaination (string datatype)}}
                                Limit your response to 600 characters. Note that the confidence score indicates the percentage
                                of the transaction being not fraudulent.""")
            
            gemini_resp = response.text
            print(gemini_resp)

            if gemini_resp != "yes":
                gem_message = json.loads(gemini_resp)
                confidence_score = gem_message["confidence score"]


            if confidence_score < 0.4:
                self.db.sadd("global_blocklist", merchant)
            
            return analysis.content
        
        return {"status": "SAFE", "reason": "Within normal spending limits."}
    
    async def analyze_crypto_wallet(self, wallet_address):
        """Analyze crypto wallet for suspicious activity"""
        if self.db.sismember("global_blocklist", wallet_address):
            return {"status": "BLOCKED", "reason": "Known malicious sender."}
            
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

        message = json.loads(analysis.content)

        confidence_score = message["confidence_score"]

        confidence_score = message["confidence_score"]

        response = client.models.generate_content(model = "gemini-3-flash-preview",
                    contents = f"""Consider yourself to be a Crypto expert. I recevied a payment request from the following wallet:
                                {wallet_address}, and based on that, I received an analysis: {analysis.content}. Validate the output. 
                                If you agree, just say yes.
                                If you do not, give the output in this format:
                                {{"confidence score": confidence score (float datatype)
                                "explaination": explaination (string datatype)}}
                                Limit your response to 600 characters. Note that the confidence score indicates the percentage
                                of the transaction being not fraudulent.""")
            
        gemini_resp = response.text
        print(gemini_resp)

        if gemini_resp != "yes":
            gem_message = json.loads(gemini_resp)
            confidence_score = gem_message["confidence score"]

        if confidence_score < 0.4:
            self.db.sadd("global_blocklist", wallet_address)
        
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
