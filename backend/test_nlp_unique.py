import sys
sys.path.insert(0, '.')
from app.nlp_generator import generate_questions

text = """
An operator is a symbol that tells Python to perform an operation on one or more values (operands).
A variable is a named location in memory used to store data.
An expression is a combination of values, variables, and operators that evaluates to a value.
A function is a block of reusable code that performs a specific task.
A loop is a control structure that repeats a block of code while a condition is true.
A list is a collection of ordered, mutable elements in Python.
A string is a sequence of characters enclosed in quotes.
Arithmetic operators include addition, subtraction, multiplication, and division.
Comparison operators are used to compare two values and return a Boolean result.
Python supports several data types including integers, floats, strings, and booleans.
Indentation is used in Python to define blocks of code.
A module is a file containing Python definitions and statements.
"""

qs = generate_questions(text, num_questions=10)
print(f"Generated {len(qs)} questions\n")
for i, q in enumerate(qs, 1):
    qtype = q['type']
    qtext = q['question'][:75]
    ans   = q['answer'][:50]
    print(f"Q{i} [{qtype}]: {qtext}")
    if q['options']:
        for opt in q['options']:
            marker = " <-- correct" if opt == q['answer'] else ""
            print(f"   - {opt[:55]}{marker}")
    else:
        print(f"   ANS: {ans}")
    print()

# Check: no two questions should have identical answers about the same term
terms_seen = {}
for q in qs:
    key = q['answer'].lower()[:30]
    if key in terms_seen:
        print(f"DUPLICATE CONCEPT: '{key}' used in Q{terms_seen[key]} and another question!")
    else:
        terms_seen[key] = qs.index(q) + 1
print("Uniqueness check done.")
