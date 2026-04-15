import sys; sys.path.insert(0, '.')
from app.nlp_generator import generate_questions, _extract_definitions

text = """
Managerial economics is a part of Economics and it is concerned with business practice for the purpose of facilitating decision making.
There is scope that the managerial economist can decide on the best alternative to maximize the profits for the firm.
These are demand forecasting techniques used to predict sales.
Which is best production technique? (c) What should be the level of output and price for the product? (d)
A firm is an organization that combines factors of production to produce goods or services.
Demand is the quantity of a good that consumers are willing and able to buy at a given price.
Supply is the amount of a product available for sale at a given price.
Price elasticity is the measure of how sensitive demand is to price changes.
A market is a place where buyers and sellers come together to exchange goods.
Profit maximization is the process by which a firm determines the price and output level that returns the greatest profit.
"""

print("=== Definitions extracted ===")
defs = _extract_definitions(text)
for term, defn in defs:
    print(f"  [{term}] => {defn[:70]}")

print()
print("=== Generated questions ===")
qs = generate_questions(text, num_questions=8)
for i, q in enumerate(qs, 1):
    print(f"Q{i} [{q['type']}]: {q['question'][:80]}")
    if q['options']:
        for opt in q['options']:
            marker = "  <-- ANSWER" if opt == q['answer'] else ""
            print(f"     {opt[:60]}{marker}")
    else:
        print(f"     Answer: {q['answer']}")
    print()

bad = [q for q in qs if q['answer'] in ('There', 'These', 'Which', 'This', 'That')]
if bad:
    print(f"FAIL: Found {len(bad)} bad pronoun questions!")
else:
    print("PASS: No pronoun/demonstrative terms found.")

bad_defn = [q for q in qs if '?' in q['question'] or '(c)' in q['question']]
if bad_defn:
    print(f"FAIL: Found {len(bad_defn)} questions with garbage text!")
else:
    print("PASS: No garbage text in questions.")
