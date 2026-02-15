import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

def get_assistant_id():
    url = "https://app.backboard.io/api/assistants"

    headers = {
    "X-API-Key": os.getenv("BACKBOARD_API_KEY")
    }

    response = requests.get(url, headers=headers)
    json_string = response.content.decode('utf-8')

    data_list = json.loads(json_string)

    for assistant in data_list:
        if assistant["name"] == "Analysis Agent":
            return assistant["assistant_id"]