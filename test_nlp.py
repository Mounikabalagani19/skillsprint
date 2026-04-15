import sys
sys.path.insert(0, 'backend')
from app.nlp_generator import generate_questions

sample = """
A variable is a named container that stores data values.
In Python, variables are created when you assign a value to them.
Python supports several data types including integers, strings, lists, and dictionaries.
Types of variables are: local variable, global variable, and instance variable.
A function is a block of reusable code that performs a specific task.
Functions can accept parameters and return values.
Loops are used to execute a block of code repeatedly.
Python has two main types of loops: the for loop and the while loop.
A list is an ordered, mutable collection of items separated by commas and enclosed in square brackets.
An integer refers to a whole number without a decimal point.
A dictionary is a collection of key-value pairs that is unordered and changeable.
"""

qs = generate_questions(sample, num_questions=10)
for i, q in enumerate(qs, 1):
    print(f"{i}. [{q['type']}] {q['question']}")
    if q['options']:
        print(f"   Options: {q['options']}")
    print(f"   Answer: {q['answer']}")
    print()
print(f"Total: {len(qs)} questions generated")
