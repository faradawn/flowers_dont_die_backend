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
    system_prompt = """
    You are a grader of leetcode questions. In this conversation,  I will give you question and user_solution. First, check whether the user solution is correct. Provide a score based on the following rubric: 3 = Correct and optimal, 2 = correct but not optimal, 1 = incorrect. Also, provide a feedback in less than 50 words about the correct approach. 

    Output in the following format strictly: 
    ##Grade: 
    ##Feedback: 
    """
    prompt = f"""
    question: {question}
    user_solution: {user_text}
    """
    
    logging.info(f"Sending prompt to Claude API: {prompt}")
    
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0,
            system=system_prompt,
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
        # logging.info(f"Received response from Claude API: {response_content}")
        
        # Extract text content from the response
        if isinstance(response_content, list):
            response_text = ' '.join([block.text for block in response_content])
        else:
            response_text = response_content
        
        # logging.info(f"Extracted response text: {response_text}")
        
        # Improved parsing to handle multiline feedback
        grade = -1
        feedback = ""
        parsing_feedback = False

        for line in response_text.split('\n'):
            if line.startswith("##Grade:"):
                grade = int(line.replace("##Grade:", "").strip())
            elif line.startswith("##Feedback:"):
                parsing_feedback = True
                feedback = line.replace("##Feedback:", "").strip()
            elif parsing_feedback:
                feedback += "\n" + line.strip()

        logging.info(f"Parsed grade: {grade}, feedback: {feedback}")
        return grade, feedback

    except Exception as e:
        logging.error(f"An error occurred in Claude API call: {str(e)}")
        return -1, "Error in processing the response"


if __name__ == "__main__":
    question = "Given an array of integers heights representing the histogram's bar height where the width of each bar is 1, return the area of the largest rectangle in the histogram."
    user_text = """
    Keep a monotonic stack with [(element, count), ...]. Loop through the array elements. Count means the how far is the current index to that element, which is running width of the rectangle of that height.
    - Every time we see a smaller element, pop elements that are bigger than me, because they have no potential of incurring bigger rectangles.
    - We add the count of the last element we pop from the stack. 
    - Every time we see a new element, loop through the entire stack and increase the count of each element by 1.
    """
    grade, feedback = get_claude_response(question, user_text)
    print(f"Grade: {grade}, Feedback: {feedback}")