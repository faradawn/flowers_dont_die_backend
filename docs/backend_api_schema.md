# Dcoumentation of Backend API
- Check the full API documentation at: https://backend.faradawn.site:8001
- Server IP address (old url) http://129.114.24.200:8001

## Login Screen
```
curl -X POST "https://backend.faradawn.site:8001/create_user" \
     -H "Content-Type: application/json" \
     -d '{"username": "Fara", "password": "1234"}'

curl -X POST "https://backend.faradawn.site:8001/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "Fara", "password": "1234"}'

curl -X POST "https://backend.faradawn.site:8001/delete_account" \
     -H "Content-Type: application/json" \
     -d '{"uid": "xxx"}'
```


## Course Screen
```
curl -X POST "https://backend.faradawn.site:8001/courses" \
     -H "Content-Type: application/json" \
     -d '{"uid": 100}'

curl -X POST "https://backend.faradawn.site:8001/courses" \
     -H "Content-Type: application/json" \
     -d '{"uid": 100}'
```

### 01 - Get Garden
```
POST {
  uid: 100
  course_id: 101
}

Firebase garden [
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
]

Response {
  status: str
  message: str
  course_id: str
  course_name: str
  garden_rows: [
    {
      row_num: int,
      topic: str,
      questions_done: List[str]
    }
  ]
}


curl -X POST "https://backend.faradawn.site:8001/get_garden" \
     -H "Content-Type: application/json" \
     -d '{"uid": "Fara_fd7bc457-2ca9-47fd-8825-7bea04b0d313", "course_id": "Software_Engineer_53fc0699-7eb2-4e66-bdd9-e1fa51aa4c3c"}'
```

### New garden
```

```

### 02 - Get Question
```
POST {
    uid: str
    course_id: str
    topic: str
}

Firebase questions [
  question_id {
    difficulty: str
    topic: str
    answer: str
    question: str
    question_number: str
    options: List[str]
    time_limit: int (seconds)
  }
]

Response {
    status: str
    message: str
    question_id: str    
    difficulty: str
    topic: str
    answer: str
    question: str
    question_number: str
    options: List[str]
    time_limit: int
}


curl -X POST "http://0.0.0.0:8001/get_question" \
     -H "Content-Type: application/json" \
     -d '{"uid": "100", "course_id": "Software_Engineer_53fc0699-7eb2-4e66-bdd9-e1fa51aa4c3c", "topic": "Binary Search", "difficulty": "Easy"}'
```

### 03 - When user submits an answer
```
POST /garden/submit_answer {
  uid: '100',
  neighbor_uid: '101',
  course_id: '10001',
  question_id: 'q1',
  response_time: 10,
  user_answer: 'A',
  correct_answer: 'B'
}

Response {
  status: 'success'
}

curl -X POST "https://backend.faradawn.site:8001/garden/submit_answer" \
     -H "Content-Type: application/json" \
     -d '{"uid": "100", "neighbor_uid": "Faradawn_2_a19480c7-d365-415b-a50d-bc71de51776c", "course_id": "101", "question_id": "SxGy1eypKa7Wq31BXuPd", "response_time": 10, "user_answer": "B", "correct_answer": "B"}'
```

### Submit text response 
```
curl -X POST "https://backend.faradawn.site:8001/submit_text_response" \
     -H "Content-Type: application/json" \
     -d '{"uid": "100", 
     "question_id": "SxGy1eypKa7Wq31BXuPd", 
     "question": "You are given a string target, an array of strings words, and an integer array costs, both arrays of the same length.Imagine an empty string s. You can perform the following operation any number of times (including zero): Choose an index i in the range [0, words.length - 1].Append words[i] to s.The cost of operation is costs[i].Return the minimum cost to make s equal to target. If it's not possible, return -1.", 
     "transcribed_text": "- The idea is dfs + memo. At every dfs(i), we ask what is the min cost of match the target from i to the end. So we want to calculate dfs(0).- At each dfs(i), we try a split j from i+1 to n, and see if target[i, j] can be matched using a word in words. We create the array of words into a set in the beginning. - We also record a global memo array that memorizes the min cost from i to the end. So it avoid repeated calculation. "
     }'


```

### Submit audio response 
```
curl -X POST "https://backend.faradawn.site:8001/submit_audio_response" \
  -H "Content-Type: multipart/form-data" \
  -F "uid=user123" \
  -F "question_id=q001" \
  -F "question=Given an array of integers heights representing the histogram's bar height where the width of each bar is 1, return the area of the largest rectangle in the histogram." \
  -F "audio_file=@stack_audio.m4a"
```

### 04 - Create Garden
```
POST /garden/create_garden {
  uid
}

Response {
  status: 'success'
}
```



## Select Neighbor Screen
```
POST /select_neighbor {
  uid,
  course_id,
}

Response [
  {
    uid: 102,
    username: "Faradawn",
    total_flowers: 50,
  },
  {
    uid: 103,
    username: "Mike",
    total_flowers: 10,
  },
  {
    uid: 104,
    username: "Ray",
    total_flowers: 5,
  }
]

curl -X POST "https://backend.faradawn.site:8001/select_neighbor" \
     -H "Content-Type: application/json" \
     -d '{"uid": 100, "course_id": 101}'
```



### Notes
- Even if the collection is deleted, can still get collection adn add document 

