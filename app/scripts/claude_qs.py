import os
from dotenv import load_dotenv
from pathlib import Path
import anthropic

parent_dir = Path(__file__).parent.parent
load_dotenv(parent_dir / '.env')
api_key = os.getenv('ANTHROPIC_API_KEY')

if not api_key:
    print("Claude API key not found in environment variables.")
    exit(1)

client = anthropic.Anthropic(api_key=api_key)

def ask_claude(question_slug, question_text):
    system_prompt = """
You are an algorithm expert creating multiple choice questions for computer science students. I will provide a LeetCode question text and question slug. Your task is to produce 1 correct approach and 2 incorrect approaches, each limited to 50 words. Do not explain why the incorrect approaches are wrong. Output the responses in the following format. After each colon, don't add a new line.
##correct_approach:
##incorrect_approach_1: 
##Incorrect_approach_2:
    """
    prompt = f"""
    question slug: {question_slug}
    question text: {question_text}
    """
    
    print(f"Sending prompt to Claude API: {prompt}")
    
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
      
        
        # Extract text content from the response
        if isinstance(response_content, list):
            response_text = ' '.join([block.text for block in response_content])
        else:
            response_text = response_content
        
        return response_text
        
    except Exception as e:
        print(f"An error occurred in Claude API call: {str(e)}")
        return -1, "Error in processing the response"

# parse the claude's output and append to a csv "claude_question_list.csv" with the following headers
# question_number, topic, difficulty, question, correct_approach, incorrect_approach_1, incorrect_approach_2
import csv

def parse_to_csv(claude_res, question_number, topic, difficulty, slug, question_text, csv_file='app/scripts/claude_question_list.csv'):
    """
    question_number,topic,difficulty,slug,question,correct_approach,incorrect_approach_1,incorrect_approach_2
    """
    # Initialize a dictionary to store the parsed data
    data = {}
    
    # Split the response into lines
    lines = claude_res.strip().split('\n')
    
    # Parse each line
    for line in lines:
        if line.startswith('##'):
            print("Line", line)
            key, value = line[2:].split(':', 1)
            data[key.strip()] = value.strip()

    # Prepare the row to be written to CSV
    row = [
        question_number,
        topic,
        difficulty,
        slug,
        question_text,
        data.get('correct_approach', ''),
        data.get('incorrect_approach_1', ''),
        data.get('Incorrect_approach_2', '')
    ]
    
    # Append the row to the CSV file
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header if the file doesn't exist
        if not file_exists:
            writer.writerow(['question_number', 'topic', 'difficulty', 'slug', 'question', 'correct_approach', 'incorrect_approach_1', 'incorrect_approach_2'])
        
        # Write the data row
        writer.writerow(row)


if __name__ == "__main__":
    question_arr = [
    "78. Subsets (Easy, Backtracking)",
    "77. Combinations (Easy, Backtracking)",
    "104. Maximum Depth of Binary Tree (Easy, Binary Tree)",
    "144. Binary Tree Preorder Traversal (Easy, Binary Tree)",
    "141. Linked List Cycle (Easy, Data Structures)",
    "160. Intersection of Two Linked Lists (Easy, Data Structures)"
]

    for i, q in enumerate(question_arr):
        print("doing", i)
        res = ask_claude(q)
        parse_to_csv(res)
        
def process_question(leetcode_question_number):
    """
    Processes a LeetCode question number by calling the Claude API and formatting the response.
    
    Args:
    leetcode_question_number (str): The unique identifier for the LeetCode question.
    
    Returns:
    str: Formatted response suitable for further processing or None if an error occurs.
    """
    # Fetch and process Claude's response
    response = ask_claude(leetcode_question_number)
    if response == -1:
        print("Failed to process question due to API error.")
        return None
    
    # Assuming response is correctly formatted for your use case
    return response
