# Dcoumentation of Firebase Database

## users 
```
user_id {
    username: str,
    password: str,
}
```

## gardens
```
garden_id {
    uid: str,
    username: str,
    course_id: str,
    garden_rows: List[
      {
        row_num: int,
        topic: str,
        questions_done: List[str]
      }
    ]
}
```

## questions 
```
question_id {
    difficulty: str
    topic: str
    answer: str
    question: str
    question_number: str
    options: List[str]
    time_limit: int (seconds)
}
```