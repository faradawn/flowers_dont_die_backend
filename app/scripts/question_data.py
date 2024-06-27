import uuid

questions_data = [
    {
        'course_id': 'Software_Engineer_53fc0699-7eb2-4e66-bdd9-e1fa51aa4c3c',
        'topic': 'Array',
        'difficulty': 'easy',
        'answer': 'A',
        'question': 'Merge two strings by alternating characters. Append remaining characters of the longer string.',
        'question_number': 'Leetcode 1768',
        'options': [
            'Two pointers. Iterate alternatively.',
            'Convert strings to lists, concatenate, convert back.',
            'Single loop for shorter string, append remaining characters.',
            'Recursion, merge one character at a time.'
        ]
    },
    {
        'course_id': '101',
        'topic': 'Array',
        'difficulty': 'medium',
        'answer': 'A',
        'question': 'Reverse the order of words in a string. Ignore extra spaces.',
        'question_number': '151',
        'options': [
            'Split, reverse words, join back together.',
            'Two-pointer technique to swap characters.',
            'Use stack to reverse order of words.',
            'Loop, reverse each word individually.'
        ]
    },
    {
        'course_id': '101',
        'topic': 'Array',
        'difficulty': 'hard',
        'answer': 'A',
        'question': 'Find max profit with at most k stock transactions. Sell before buying again.',
        'question_number': '188',
        'options': [
            'Dynamic programming with 2D array for max profit.',
            'Sort prices, select k largest differences.',
            'Greedy, buy at local min, sell at local max.',
            'Recursive, try all transactions, return max profit.'
        ]
    }
]
