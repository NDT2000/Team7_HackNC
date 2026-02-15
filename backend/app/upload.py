import requests
import os
from dotenv import load_dotenv
from .getassistantid import get_assistant_id

load_dotenv()

assistant_id = get_assistant_id()

headers = {
 "X-API-Key": os.getenv("BACKBOARD_API_KEY")
}

with open("phishing_messages.txt", "rb") as f:
    response = requests.post(
        f"https://app.backboard.io/api/assistants/{assistant_id}/documents",
        headers = headers,
        files={"file": f}
    )

document = response.json()
document_id = document['document_id']
status = {document['status']}

while status != "indexed":
    response = requests.get(
    f"https://app.backboard.io/api/documents/{document_id}/status",
    headers = headers
    )
    
    status = response.json()["status"]

print(status)