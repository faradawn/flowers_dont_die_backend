import os
from dotenv import load_dotenv
from pathlib import Path
import anthropic

# Get the parent directory
parent_dir = Path(__file__).parent.parent

# Load the .env file from the parent directory
load_dotenv(parent_dir / '.env')

# Now you can access the API key from the environment variables
api_key = os.getenv('ANTHROPIC_API_KEY')

# Use the API key to initialize the client
client = anthropic.Anthropic(api_key=api_key)

message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1000,
    temperature=0,
    system="You are a world-class poet. Respond only with short poems.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Why is the ocean salty?"
                }
            ]
        }
    ]
)
print(message.content)