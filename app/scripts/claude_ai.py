import os
from dotenv import load_dotenv
from pathlib import Path
import anthropic
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

parent_dir = Path(__file__).parent.parent
load_dotenv(parent_dir / '.env')
api_key = os.getenv('ANTHROPIC_API_KEY')

if not api_key:
    logging.error("Claude API key not found in environment variables.")
    exit(1)

client = anthropic.Anthropic(api_key=api_key)

def get_claude_response(question, user_text):
    prompt = (
        f"Question: {question}\n"
        f"User response: {user_text}\n"
        "Please provide a grade and encouraging, constructive feedback that is not too harsh. "
        "Ensure the feedback is concise and can be read in under 1 minutes."
    )
    logging.info(f"Sending prompt to Claude API: {prompt}")
    
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0,
            system="You are a world-class educator. Provide detailed and constructive feedback.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        response_content = message.content
        logging.info(f"Received response from Claude API: {response_content}")
        
        # Extract text content from the response
        if isinstance(response_content, list):
            response_text = ' '.join([block.text for block in response_content])
        else:
            response_text = response_content
        
        logging.info(f"Extracted response text: {response_text}")
        
        # Improved parsing to handle multiline feedback
        grade = "N/A"
        feedback = ""
        parsing_feedback = False

        for line in response_text.split('\n'):
            if line.startswith("Grade:"):
                grade = line.replace("Grade:", "").strip()
            elif line.startswith("Feedback:"):
                parsing_feedback = True
                feedback = line.replace("Feedback:", "").strip()
            elif parsing_feedback:
                feedback += "\n" + line.strip()

        logging.info(f"Parsed grade: {grade}, feedback: {feedback}")
        return grade, feedback

    except Exception as e:
        logging.error(f"An error occurred in Claude API call: {str(e)}")
        return "N/A", "Error in processing the response"


# if __name__ == "__main__":
#     question = "Explain the intuition behind Depth-First Search (DFS) algorithm."
#     user_text = "Depth-First Search (DFS) explores a graph by going as deep as possible before backtracking. It uses a stack data structure, either implicitly through recursion or explicitly with an actual stack."
#     grade, feedback = get_claude_response(question, user_text)
#     print(f"Grade: {grade}, Feedback: {feedback}")