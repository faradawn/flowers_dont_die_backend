from app.scripts.leetcode_fetch import fetch_leetcode_data
from app.scripts.claude_qs import process_question
from app.scripts.firebase_create_questions import upload_questions

def upload_complete_question(slug):
    """
    Orchestrates the fetching, processing, and uploading of question data based on a given slug.
    
    Args:
    slug (str): The slug representing the LeetCode question.
    """
    # Fetch the question data from LeetCode
    question_data = fetch_leetcode_data(slug)
    if not question_data:
        print(f"Failed to fetch data for slug: {slug}")
        return

    # Process the question data using Claude's API
    processed_data = process_question(slug)  # Updated to pass slug directly
    if not processed_data:
        print(f"Failed to process data for slug: {slug}")
        return

    # Upload the processed data to Firebase
    upload_result = upload_questions(processed_data)
    if upload_result:
        print(f"Successfully uploaded data for slug: {slug}")
    else:
        print(f"Failed to upload data for slug: {slug}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python upload_question_to_firebase.py <question_slug>")
    else:
        question_slug = sys.argv[1]
        upload_complete_question(question_slug)
