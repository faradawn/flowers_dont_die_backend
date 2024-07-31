from app.firebase import db
from app.scripts.claude_qs import ask_claude, parse_to_csv
import requests

csv_file = 'app/scripts/claude_question_list.csv'
course_id = 'Software_Engineering_1'

def get_course_id():
    course_id = None
    for course in db.collection('courses').stream():
        course_id = course.id
        break
    return course_id

def fetch_leetcode(slug):
    """
    {'link': 'https://leetcode.com/problems/number-of-islands', 'questionId': '200', 'questionFrontendId': '200', 'questionTitle': 'Number of Islands', 'titleSlug': 'number-of-islands', 'difficulty': 'Medium', 'isPaidOnly': False, 'question': '<p>Given an <code>m x n</code> 2D binary grid <code>grid</code> which represents a map of <code>&#39;1&#39;</code>s (land) and <code>&#39;0&#39;</code>s (water), return <em>the number of islands</em>.</p>\n\n<p>An <strong>island</strong> is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.</p>\n\n<p>&nbsp;</p>\n<p><strong class="example">Example 1:</strong></p>\n\n<pre>\n<strong>Input:</strong> grid = [\n  [&quot;1&quot;,&quot;1&quot;,&quot;1&quot;,&quot;1&quot;,&quot;0&quot;],\n  [&quot;1&quot;,&quot;1&quot;,&quot;0&quot;,&quot;1&quot;,&quot;0&quot;],\n  [&quot;1&quot;,&quot;1&quot;,&quot;0&quot;,&quot;0&quot;,&quot;0&quot;],\n  [&quot;0&quot;,&quot;0&quot;,&quot;0&quot;,&quot;0&quot;,&quot;0&quot;]\n]\n<strong>Output:</strong> 1\n</pre>\n\n<p><strong class="example">Example 2:</strong></p>\n\n<pre>\n<strong>Input:</strong> grid = [\n  [&quot;1&quot;,&quot;1&quot;,&quot;0&quot;,&quot;0&quot;,&quot;0&quot;],\n  [&quot;1&quot;,&quot;1&quot;,&quot;0&quot;,&quot;0&quot;,&quot;0&quot;],\n  [&quot;0&quot;,&quot;0&quot;,&quot;1&quot;,&quot;0&quot;,&quot;0&quot;],\n  [&quot;0&quot;,&quot;0&quot;,&quot;0&quot;,&quot;1&quot;,&quot;1&quot;]\n]\n<strong>Output:</strong> 3\n</pre>\n\n<p>&nbsp;</p>\n<p><strong>Constraints:</strong></p>\n\n<ul>\n\t<li><code>m == grid.length</code></li>\n\t<li><code>n == grid[i].length</code></li>\n\t<li><code>1 &lt;= m, n &lt;= 300</code></li>\n\t<li><code>grid[i][j]</code> is <code>&#39;0&#39;</code> or <code>&#39;1&#39;</code>.</li>\n</ul>\n', 'exampleTestcases': '[["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]\n[["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]', 'topicTags': [{'name': 'Array', 'slug': 'array', 'translatedName': None}, {'name': 'Depth-First Search', 'slug': 'depth-first-search', 'translatedName': None}, {'name': 'Breadth-First Search', 'slug': 'breadth-first-search', 'translatedName': None}, {'name': 'Union Find', 'slug': 'union-find', 'translatedName': None}, {'name': 'Matrix', 'slug': 'matrix', 'translatedName': None}], 'hints': [], 'solution': {'id': '342', 'canSeeDetail': False, 'paidOnly': True, 'hasVideoSolution': True, 'paidOnlyVideo': True}, 'companyTagStats': None, 'likes': 22797, 'dislikes': 522, 'similarQuestions': '[{"title": "Surrounded Regions", "titleSlug": "surrounded-regions", "difficulty": "Medium", "translatedTitle": null}, {"title": "Walls and Gates", "titleSlug": "walls-and-gates", "difficulty": "Medium", "translatedTitle": null}, {"title": "Number of Islands II", "titleSlug": "number-of-islands-ii", "difficulty": "Hard", "translatedTitle": null}, {"title": "Number of Connected Components in an Undirected Graph", "titleSlug": "number-of-connected-components-in-an-undirected-graph", "difficulty": "Medium", "translatedTitle": null}, {"title": "Number of Distinct Islands", "titleSlug": "number-of-distinct-islands", "difficulty": "Medium", "translatedTitle": null}, {"title": "Max Area of Island", "titleSlug": "max-area-of-island", "difficulty": "Medium", "translatedTitle": null}, {"title": "Count Sub Islands", "titleSlug": "count-sub-islands", "difficulty": "Medium", "translatedTitle": null}, {"title": "Find All Groups of Farmland", "titleSlug": "find-all-groups-of-farmland", "difficulty": "Medium", "translatedTitle": null}, {"title": "Count Unreachable Pairs of Nodes in an Undirected Graph", "titleSlug": "count-unreachable-pairs-of-nodes-in-an-undirected-graph", "difficulty": "Medium", "translatedTitle": null}, {"title": "Maximum Number of Fish in a Grid", "titleSlug": "maximum-number-of-fish-in-a-grid", "difficulty": "Medium", "translatedTitle": null}]'}
    
    """
    base_url = "https://alfa-leetcode-api.onrender.com/select"
    params = {"titleSlug": slug}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def csv_to_firebase(course_id='Software_Engineering_1', file_name='app/scripts/claude_question_list.csv'):
    import csv
    import os

    firebase_ref = db.collection('questions')
    questions_data = []

    with open(file_name, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            question_dict = {
                'course_id': course_id,
                'topic': row['topic'],
                'difficulty': row['difficulty'],
                'slug': row['slug'],
                'answer': 'A',  # Assuming the correct solution is always 'A'
                'question': row['question'],
                'question_number': row['question_number'],
                'options': [
                    row['correct_approach'],
                    row['incorrect_approach_1'],
                    row.get('incorrect_approach_2', ''),
                ],
                'time_limit': 90
            }
            
            # Create the document ID as (topic|difficulty|slug)
            doc_id = f"{row['topic']}|{row['difficulty']}|{row['slug']}"
            
            # Use the created document ID when adding the question to Firestore
            firebase_ref.document(doc_id).set(question_dict)
            
            print(f"Adding question_number: {question_dict['question_number']}, topic: {question_dict['topic']}, difficulty: {question_dict['difficulty']}")



def main_pipeline(slug, topic):
    res = fetch_leetcode(slug)
    claude_res = ask_claude(slug, res['question'])
    print("claude res", claude_res)
    parse_to_csv(claude_res, res['questionFrontendId'], topic, res['difficulty'], slug, res['question'], csv_file)
    
    csv_to_firebase(course_id=course_id, file_name=csv_file)

if __name__ == '__main__':
    # main_pipeline('climbing-stairs', 'Dynamic Programming')
    csv_to_firebase(course_id=course_id, file_name=csv_file)

# Usage
# python3 -m app.scripts.firebase_delete_collection --collection questions
# python3 -m app.scripts.firebase_create_questions


