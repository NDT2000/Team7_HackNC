import requests
from dotenv import load_dotenv
import os

load_dotenv()

url = "https://app.backboard.io/api/assistants"

body = {
  "name" : "Analysis Agent",
  "description": "An agent for analysing messages and transaction information to check fraudulency.",
  "system_prompt" : """You are a smart bank manager / natural language expert, who, based on the input type, performs
                    the relevant analysis.
                    If the input is a natural language message, then analyze the given message with the previous given phishing messages 
                    to check for similarity, and give a confidence score for how legitimate the message is, along with the reasoning for it.
                    If the input is a bank transaction, analyze the transaction and gives a confidence score of how safe the transaction is, 
                    along with the reasoning for it.
                    Return the output in the following format:
                    {"confidence score": score (float datatype)
                    "explaination": reasoning (String datatype)}
                    Limit your output to 600 tokens only.""",
  "tok_k": 3,
  "embedding_provider": "openai",
  "embedding_model_name": "text-embedding-ada-002",
  "embedding_dims": 1536
}

headers = {
 "X-API-Key": os.getenv("BACKBOARD_API_KEY"),
 "Content-Type": "application/json"
}

response = requests.post(url, json=body, headers=headers)
print(response)