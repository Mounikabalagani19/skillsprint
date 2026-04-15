import sys; sys.path.insert(0, '.')
from app.nlp_generator import generate_questions

text = """
Python Non-Primitive (Built-in) Data Types
Non-primitive data types are used to store multiple values in a single variable.

A list is a mutable, ordered collection that allows duplicate and heterogeneous values.
A tuple is an immutable, ordered collection used to store final or fixed data.
A set is an unordered collection used to store unique values.
A dictionary stores data in the form of key-value pairs.

Types of Non-Primitive Data Types are List, Tuple, Set, and Dictionary.

Key Characteristics of list include Mutable, Ordered, Dynamic in size, Allows duplicate values.
Key Characteristics of tuple include Immutable, Faster than lists, Ordered collection.
A set includes Unordered, Does not allow duplicate values, Mutable, Uses hashing internally.

Lists are flexible but slower.
Tuples are faster and memory efficient.
Sets provide fast lookup and uniqueness.
Dictionaries are best for structured real-world data.
Keys must be unique in a dictionary.
"""

qs = generate_questions(text, num_questions=10)
print(f"Generated {len(qs)} questions\n")

covered = {}
for i, q in enumerate(qs, 1):
    qtype = q['type']
    qtext = q['question'][:80]
    print(f"Q{i} [{qtype}]: {qtext}")
    if q['options']:
        for opt in q['options']:
            marker = "  <-- ANSWER" if opt == q['answer'] else ""
            print(f"     {opt[:60]}{marker}")
    else:
        print(f"     Answer: {q['answer']}")
    key = q['answer'].strip().lower()[:40]
    if key in covered:
        print(f"  !! DUPLICATE ANSWER with Q{covered[key]}")
    covered[key] = i
    print()

print("Done. No duplicates printed above = success.")
