from app.firebase import db

def main():
    ref = db.collection('courses').document('Software_Engineering_1')
    data = {
        'course_name': 'Software Engineering 1',
        'course_topics': ['Dynamic Programming', 'Backtracking', 'Binary Tree', 'Data Structures']
    }
    ref.set(data)
    print("Document created successfully")

if __name__ == '__main__':
    main()
