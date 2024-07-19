# Delete all questions
python -m app.scripts.firebase_delete_collection --collection questions

# Generate questions (load to claude_question_list.csv)
python -m app.scripts.claude_qs

# Upload csv to firebase
python -m app.scripts.firebase_create_questions