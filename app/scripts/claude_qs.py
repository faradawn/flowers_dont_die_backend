# usage: python3 -m app.scripts.claude_qs

import os
from dotenv import load_dotenv
from pathlib import Path
import anthropic
import csv

parent_dir = Path(__file__).parent.parent
load_dotenv(parent_dir / '.env')
api_key = os.getenv('ANTHROPIC_API_KEY')

if not api_key:
    print("Claude API key not found in environment variables.")
    exit(1)

client = anthropic.Anthropic(api_key=api_key)

def ask_claude(leetcode_question_number):
    system_prompt = """
    You are a teacher creating multiple choice questions. I will provide you with a leetcode question number. You will describe the full question in less than 100 words. 
    Produce 1 correct approach and 2 incorrect approaches. 
    Then, create 2 other incorrect approaches that uses a similiar method as the correct approach to make the question harder. 
    Limit each approach in 50 words. Don’t say why the incorrect approach is wrong. Output in the following format: 
##question_number:
##topic:
##difficulty:
##question:
##correct_approach:
##incorrect_approach_1: 
##incorrect_approach_2:
##incorrect_approach_3:
##incorrect_approach_4:
    """
    prompt = f"""
    leetcode question number: {leetcode_question_number}
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

def parse_to_csv(text_response):
    # Initialize a dictionary to store the parsed data
    data = {}
    
    # Split the response into lines
    lines = text_response.strip().split('\n')
    
    # Parse each line
    for line in lines:
        if line.startswith('##'):
            key, value = line[2:].split(':', 1)
            data[key.strip()] = value.strip()
    
    # Prepare the row to be written to CSV
    row = [
        data.get('question_number', ''),
        data.get('topic', ''),
        data.get('difficulty', ''),
        data.get('question', ''),
        data.get('correct_approach', ''),
        data.get('incorrect_approach_1', ''),
        data.get('incorrect_approach_2', ''),
        data.get('incorrect_approach_3', ''),  # Same topic option 2
        data.get('incorrect_approach_4', '')  # Same topic option 3
    ]
    
    # Corrected path to the CSV file
    csv_file = 'app/scripts/claude_question_list.csv'
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header if the file doesn't exist
        if not file_exists:
            writer.writerow([
                'question_number', 'topic', 'difficulty', 'question',
                'correct_approach', 'incorrect_approach_1', 'incorrect_approach_2',
                'incorrect_approach_3', 'same_topic_option_4'
            ])
        
        # Write the data row
        writer.writerow(row)

if __name__ == "__main__":
    question_arr = [
        "704: Binary Search. Topic: Binary Search. Difficulty: Easy",
        "153: Find Minimum in Rotated Sorted Array. Topic: Binary Search. Difficulty: Medium",
        "26: Remove Duplicates from Sorted Array. Topic: Two Pointers. Difficulty: Easy",
        "15: 3Sum. Topic: Two Pointers. Difficulty: Medium",
        "20: Valid Parentheses. Topic: Stack. Difficulty: Easy",
        "155: Min Stack. Topic: Stack. Difficulty: Medium",
        "104: Maximum Depth of Binary Tree. Topic: Binary Tree. Difficulty: Easy",
        "94: Binary Tree Inorder Traversal. Topic: Binary Tree. Difficulty: Medium",
        "102: Binary Tree Level Order Traversal. Topic: BFS. Difficulty: Easy",
        "127: Word Ladder. Topic: BFS. Difficulty: Medium",
        "112: Path Sum. Topic: DFS. Difficulty: Easy",
        "200: Number of Islands. Topic: DFS. Difficulty: Medium",
        "70: Climbing Stairs. Topic: Dynamic Programming. Difficulty: Easy",
        "300: Longest Increasing Subsequence. Topic: Dynamic Programming. Difficulty: Medium"
    ]

    for i, q in enumerate(question_arr):
        print("Processing question", i)
        res = ask_claude(q)
        if res != -1:
            parse_to_csv(res)
        else:
            print(f"Failed to process question {q}")
        
        if i > 1:
            break
