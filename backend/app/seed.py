from app.database import SessionLocal, engine
from app.models import Challenge, Base

# --- Sample Challenges ---

challenges_to_add = [
    # Day 1
    Challenge(title="Day 1: Python List Slicing", question="What is the output of `my_list = [10, 20, 30, 40, 50]` followed by `print(my_list[1:3])`?", category="Coding", answer="[20, 30]"),
    Challenge(title="Day 1: Capital of France", question="What is the capital city of France?", category="General Knowledge", answer="Paris"),
    Challenge(title="Day 1: Simple Math Puzzle", question="If you have a pie with 8 slices and you eat 3, what fraction of the pie is left?", category="Math", answer="5/8"),
    # Missing Day 1 frontend question (hyperlink tag)
    Challenge(title="Day 1: Hyperlink Tag", question="Which HTML tag is used to create a hyperlink?", category="Frontend", answer="<a>"),
    # Day 2
    Challenge(title="Day 2: Reverse String", question="s = 'SkillSprint' → Output of print(s[::-1])?", category="Coding", answer="tnirpSllikS"),
    Challenge(title="Day 2: Red Planet", question="Which planet is called the 'Red Planet'?", category="General Knowledge", answer="Mars"),
    Challenge(title="Day 2: Three-digit Puzzle", question="I am a 3-digit number. Tens digit = ones digit + 5. Hundreds digit = tens digit – 8. What number am I?", category="Math", answer="194"),
    Challenge(title="Day 2: Background Property", question="Which CSS property changes background color?", category="Frontend", answer="background-color"),
    # Day 3
    Challenge(title="Day 3: Star Loop", question="for i in range(1, 5):\n    print(i, end=' ') → What is the output?", category="Coding", answer="1 2 3 4"),
    Challenge(title="Day 3: Telephone Inventor", question="Who invented the telephone?", category="General Knowledge", answer="Alexander Graham Bell"),
    Challenge(title="Day 3: Cats and Mice", question="5 cats catch 5 mice in 5 minutes. How many cats catch 100 mice in 100 minutes?", category="Math", answer="5"),
    Challenge(title="Day 3: JS Variable Keyword", question="Which keyword is used to declare a variable in JS (ES6)?", category="Frontend", answer="let"),
    # Day 4
    Challenge(title="Day 4: Power Operation", question="What is the output of print(2 ** 3 ** 2)?", category="Coding", answer="512"),
    Challenge(title="Day 4: Father of Computers", question="Who is known as the 'Father of Computers'?", category="General Knowledge", answer="Charles Babbage"),
    Challenge(title="Day 4: Sheep Puzzle", question="A farmer has 17 sheep. All but 9 run away. How many are left?", category="Math", answer="9"),
    Challenge(title="Day 4: Largest Heading", question="Which HTML tag is used for the largest heading?", category="Frontend", answer="<h1>"),
    # Day 5
    Challenge(title="Day 5: Append List", question="nums = [1,2,3]; nums.append([4,5]) → What is nums?", category="Coding", answer="[1,2,3,[4,5]]"),
    Challenge(title="Day 5: Currency of Japan", question="What is the national currency of Japan?", category="General Knowledge", answer="Yen"),
    Challenge(title="Day 5: Clock Angle", question="A clock shows 3:15. What is the angle between hour and minute hands?", category="Math", answer="7.5"),
    Challenge(title="Day 5: Text Size Property", question="Which CSS property is used to change text size?", category="Frontend", answer="font-size"),
    # Day 6
    Challenge(title="Day 6: List Length", question="x = [1,2,3]\nprint(len(x*3)) → Output?", category="Coding", answer="9"),
    Challenge(title="Day 6: First Moon Walker", question="Who was the first person to walk on the moon?", category="General Knowledge", answer="Neil Armstrong"),
    Challenge(title="Day 6: Train Travel", question="If a train travels 60 km in 1 hour, how long to travel 150 km?", category="Math", answer="2.5"),
    Challenge(title="Day 6: Image Source Attribute", question="Which HTML attribute specifies an image source?", category="Frontend", answer="src"),
    # Day 7
    Challenge(title="Day 7: Bool Outputs", question="What is the output of bool('', bool([]), bool(0))?", category="Coding", answer="False, False, False"),
    Challenge(title="Day 7: Largest Population", question="Which country has the largest population in the world (2025)?", category="General Knowledge", answer="China"),
    Challenge(title="Day 7: Sequence Puzzle", question="Fill in the blank: 2, 6, 12, 20, 30, _?", category="Math", answer="42"),
    Challenge(title="Day 7: Bold Text Property", question="Which CSS property makes text bold?", category="Frontend", answer="font-weight"),
    # Day 8
    Challenge(title="Day 8: Join String", question="print(','.join(['a','b','c'])) → Output?", category="Coding", answer="a,b,c"),
    Challenge(title="Day 8: Mona Lisa Painter", question="Who painted the Mona Lisa?", category="General Knowledge", answer="Leonardo da Vinci"),
    Challenge(title="Day 8: Next Square", question="What comes next? 1, 4, 9, 16, 25, _?", category="Math", answer="36"),
    Challenge(title="Day 8: Line Break Element", question="Which HTML element is used for a line break?", category="Frontend", answer="<br>"),
    # Day 9
    Challenge(title="Day 9: Dict Type", question="What is the output of print(type({}))?", category="Coding", answer="<class 'dict'>"),
    Challenge(title="Day 9: Capital of Australia", question="What is the capital of Australia?", category="General Knowledge", answer="Canberra"),
    Challenge(title="Day 9: Worker Puzzle", question="If 10 workers build a wall in 20 days, how many workers finish in 5 days?", category="Math", answer="40"),
    Challenge(title="Day 9: Letter Spacing Property", question="Which CSS property controls spacing between letters?", category="Frontend", answer="letter-spacing"),
    # Day 10
    Challenge(title="Day 10: Slice String", question="print('Python'[1:4]) → Output?", category="Coding", answer="yth"),
    Challenge(title="Day 10: Sahara Continent", question="Which continent is the Sahara Desert located in?", category="General Knowledge", answer="Africa"),
    Challenge(title="Day 10: Age Puzzle", question="A man is 30 years old, his son is 5. In how many years will the man be twice as old as his son?", category="Math", answer="5"),
    Challenge(title="Day 10: Console Method", question="Which JS method is used to print to the console?", category="Frontend", answer="console.log"),
    # Day 11
    Challenge(title="Day 11: Division Outputs", question="print(5//2, 5/2) → Output?", category="Coding", answer="2 2.5"),
    Challenge(title="Day 11: Shakespeare", question="Who wrote 'Romeo and Juliet'?", category="General Knowledge", answer="William Shakespeare"),
    Challenge(title="Day 11: Pencil Cost", question="If 2 pencils cost ₹8, how much do 5 pencils cost?", category="Math", answer="₹20"),
    Challenge(title="Day 11: Ordered List Element", question="Which HTML element is used for an ordered list?", category="Frontend", answer="<ol>"),
    # Day 12
    Challenge(title="Day 12: Set Intersection", question="a = {1,2,3}; b = {3,4,5}; print(a & b) → Output?", category="Coding", answer="{3}"),
    Challenge(title="Day 12: US Currency", question="What is the currency of the USA?", category="General Knowledge", answer="Dollar"),
    Challenge(title="Day 12: Travel Time", question="A car travels 60 km/h. How long to travel 120 km?", category="Math", answer="2"),
    Challenge(title="Day 12: Text Align Property", question="Which CSS property is used to align text?", category="Frontend", answer="text-align"),
    # Day 13
    Challenge(title="Day 13: List Append Mutability", question="x = [1,2,3]; y = x; y.append(4); print(x) → Output?", category="Coding", answer="[1,2,3,4]"),
    Challenge(title="Day 13: Photosynthesis Gas", question="Which gas do plants produce during photosynthesis?", category="General Knowledge", answer="Oxygen"),
    Challenge(title="Day 13: Arithmetic", question="Solve: 15 – (3 × 2) + 4 = ?", category="Math", answer="13"),
    Challenge(title="Day 13: Table Row Element", question="Which HTML element is used for a table row?", category="Frontend", answer="<tr>"),
    # Day 14
    Challenge(title="Day 14: Bool False String", question="print(bool('False')) → Output?", category="Coding", answer="True"),
    Challenge(title="Day 14: Largest Ocean", question="What is the largest ocean on Earth?", category="General Knowledge", answer="Pacific Ocean"),
    Challenge(title="Day 14: Percentage Apples", question="A farmer has 100 apples. He gives 40% to his friend. How many left?", category="Math", answer="60"),
    Challenge(title="Day 14: Rounded Corners", question="Which CSS property makes corners rounded?", category="Frontend", answer="border-radius"),
    # Day 15
    Challenge(title="Day 15: Even Range", question="print(list(range(2,10,2))) → Output?", category="Coding", answer="[2,4,6,8]"),
    Challenge(title="Day 15: National Language of China", question="What is the national language of China?", category="General Knowledge", answer="Mandarin"),
    Challenge(title="Day 15: Solve for x", question="If 7x = 56, what is x?", category="Math", answer="8"),
    Challenge(title="Day 15: Image Tag", question="Which HTML tag is used to display an image?", category="Frontend", answer="<img>"),
    # Day 16
    Challenge(title="Day 16: Multiply String Number", question="a = '123'\nprint(int(a)*2) → Output?", category="Coding", answer="246"),
    Challenge(title="Day 16: Gravity Discoverer", question="Who discovered gravity?", category="General Knowledge", answer="Sir Isaac Newton"),
    Challenge(title="Day 16: Rectangle Area", question="A rectangle has length 10 and width 5. What is its area?", category="Math", answer="50"),
    Challenge(title="Day 16: Text Shadow Property", question="Which CSS property is used for shadow effect on text?", category="Frontend", answer="text-shadow"),
    # Day 17
    Challenge(title="Day 17: Capitalized Hello", question="print('hello'.capitalize()) → Output?", category="Coding", answer="Hello"),
    Challenge(title="Day 17: Prime Minister of India 2025", question="Who is the Prime Minister of India in 2025?", category="General Knowledge", answer="Narendra Modi"),
    Challenge(title="Day 17: Missing Number", question="Find the missing number: 2, 4, 8, 16, _, 64", category="Math", answer="32"),
    Challenge(title="Day 17: Checkbox Tag", question="Which HTML tag creates a checkbox?", category="Frontend", answer="<input type=\"checkbox\">"),
    # Day 18
    Challenge(title="Day 18: Modulo", question="print(7%3) → Output?", category="Coding", answer="1"),
    Challenge(title="Day 18: Tallest Mountain", question="What is the tallest mountain in the world?", category="General Knowledge", answer="Mount Everest"),
    Challenge(title="Day 18: Order of Operations", question="If 12 ÷ 3 × 2 = ?, find the answer.", category="Math", answer="8"),
    Challenge(title="Day 18: Alert Function", question="Which JS function shows an alert box?", category="Frontend", answer="alert"),
    # Day 19
    Challenge(title="Day 19: Sorted List", question="print(sorted([3,1,2])) → Output?", category="Coding", answer="[1,2,3]"),
    Challenge(title="Day 19: National Anthem Author", question="Who wrote the Indian National Anthem?", category="General Knowledge", answer="Rabindranath Tagore"),
    Challenge(title="Day 19: Probability Red", question="A bag has 3 red and 2 blue balls. If you pick one randomly, what's the probability it is red?", category="Math", answer="3/5"),
    Challenge(title="Day 19: Italic Font Property", question="Which CSS property changes font style to italic?", category="Frontend", answer="font-style"),
    # Day 20
    Challenge(title="Day 20: Multiply List", question="a = [1,2]; print(a*3) → Output?", category="Coding", answer="[1,2,1,2,1,2]"),
    Challenge(title="Day 20: Land of Rising Sun", question="Which country is known as the 'Land of Rising Sun'?", category="General Knowledge", answer="Japan"),
    Challenge(title="Day 20: Men and Days", question="If 6 men build a wall in 12 days, how many men in 4 days?", category="Math", answer="18"),
    Challenge(title="Day 20: Form Element", question="Which HTML element defines a form?", category="Frontend", answer="<form>"),
    # Day 21
    Challenge(title="Day 21: Substring Check", question="print('ab' in 'abc') → Output?", category="Coding", answer="True"),
    Challenge(title="Day 21: Largest Planet", question="Which planet is the largest in our solar system?", category="General Knowledge", answer="Jupiter"),
    Challenge(title="Day 21: Percentage", question="What is 15% of 200?", category="Math", answer="30"),
    Challenge(title="Day 21: Padding Property", question="Which CSS property sets space inside a box?", category="Frontend", answer="padding"),
    # Day 22
    Challenge(title="Day 22: String Length", question="print(len('SkillSprint')) → Output?", category="Coding", answer="11"),
    Challenge(title="Day 22: Iron Man of India", question="Who is called the 'Iron Man of India'?", category="General Knowledge", answer="Sardar Vallabhbhai Patel"),
    Challenge(title="Day 22: Chocolates Left", question="A box has 12 chocolates. You eat 1/3rd. How many left?", category="Math", answer="8"),
    Challenge(title="Day 22: Alt Text Attribute", question="Which HTML attribute specifies alternative text for images?", category="Frontend", answer="alt"),
    # Day 23
    Challenge(title="Day 23: Tuple Type", question="x = (1,2,3)\nprint(type(x)) → Output?", category="Coding", answer="<class 'tuple'>"),
    Challenge(title="Day 23: Capital of Italy", question="What is the capital of Italy?", category="General Knowledge", answer="Rome"),
    Challenge(title="Day 23: Solve for x", question="If 5x = 25, then x = ?", category="Math", answer="5"),
    Challenge(title="Day 23: Color Property", question="Which CSS property changes text color?", category="Frontend", answer="color"),
    # Day 24
    Challenge(title="Day 24: Uppercase", question="print('Python'.upper()) → Output?", category="Coding", answer="PYTHON"),
    Challenge(title="Day 24: First President of India", question="Who was the first President of India?", category="General Knowledge", answer="Dr. Rajendra Prasad"),
    Challenge(title="Day 24: Arithmetic", question="Solve: 81 ÷ 9 + 5 = ?", category="Math", answer="14"),
    Challenge(title="Day 24: Dropdown Element", question="Which HTML element is used for dropdown list?", category="Frontend", answer="<select>"),
    # Day 25
    Challenge(title="Day 25: Sum List", question="nums = [10,20,30)\nprint(sum(nums)) → Output?", category="Coding", answer="60"),
    Challenge(title="Day 25: Longest River", question="Which is the longest river in the world?", category="General Knowledge", answer="Nile"),
    Challenge(title="Day 25: Fibonacci Next", question="What comes next? 1, 1, 2, 3, 5, 8, _?", category="Math", answer="13"),
    Challenge(title="Day 25: Height Property", question="Which CSS property changes element height?", category="Frontend", answer="height"),
    # Day 26
    Challenge(title="Day 26: Repeat String", question="print('Hi' * 3) → Output?", category="Coding", answer="HiHiHi"),
    Challenge(title="Day 26: US President 2025", question="Who is the current President of the USA (2025)?", category="General Knowledge", answer="Joe Biden"),
    Challenge(title="Day 26: Square 9", question="If 7² = 49, what is 9²?", category="Math", answer="81"),
    Challenge(title="Day 26: Nav Element", question="Which HTML element defines a navigation link?", category="Frontend", answer="<nav>"),
    # Day 27
    Challenge(title="Day 27: Division and Mod", question="print(10//3, 10%3) → Output?", category="Coding", answer="3 1"),
    Challenge(title="Day 27: Smallest Country", question="Which is the smallest country in the world?", category="General Knowledge", answer="Vatican City"),
    Challenge(title="Day 27: Worker Days", question="If 2 workers take 10 days, how many days for 5 workers?", category="Math", answer="4"),
    Challenge(title="Day 27: Border Color", question="Which CSS property sets border color?", category="Frontend", answer="border-color"),
    # Day 28
    Challenge(title="Day 28: List from String", question="print(list('123')) → Output?", category="Coding", answer="['1','2','3']"),
    Challenge(title="Day 28: UK Currency", question="What is the currency of the UK?", category="General Knowledge", answer="Pound Sterling"),
    Challenge(title="Day 28: Solve for x", question="If 12 + x = 20, find x.", category="Math", answer="8"),
    Challenge(title="Day 28: Parse JSON", question="Which JS function parses JSON string into object?", category="Frontend", answer="JSON.parse"),
    # Day 29
    Challenge(title="Day 29: Count P", question="print('apple'.count('p')) → Output?", category="Coding", answer="2"),
    Challenge(title="Day 29: Discovery of India Author", question="Who wrote 'Discovery of India'?", category="General Knowledge", answer="Jawaharlal Nehru"),
    Challenge(title="Day 29: Money Left", question="A man has ₹100. He spends 25%. How much left?", category="Math", answer="75"),
    Challenge(title="Day 29: Horizontal Line Tag", question="Which HTML tag is used for a horizontal line?", category="Frontend", answer="<hr>"),
    # Day 30
    Challenge(title="Day 30: Lowercase", question="print('HELLO'.lower()) → Output?", category="Coding", answer="hello"),
    Challenge(title="Day 30: Capital of Canada", question="What is the capital of Canada?", category="General Knowledge", answer="Ottawa"),
    Challenge(title="Day 30: Cube Volume", question="A cube has side 4 cm. Find its volume.", category="Math", answer="64"),

    Challenge(title="Day 30: Animation Speed", question="Which CSS property controls animation speed?", category="Frontend", answer="animation-duration"),
]


def seed_database() -> int:
    """Create tables and seed default challenges if not present.
    Returns the number of items inserted (0 if nothing to add).
    """
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if challenges already exist to avoid duplicates.
        # Also dedupe the in-memory seed list by title before insert.
        existing_titles = {c.title for c in db.query(Challenge).all()}
        seen_titles = set(existing_titles)
        new_challenges = []
        for c in challenges_to_add:
            if c.title in seen_titles:
                continue
            seen_titles.add(c.title)
            new_challenges.append(c)

        # If the Challenge model exposes a 'day' column, try to populate it by parsing the title
        import re
        for c in new_challenges:
            try:
                m = re.search(r"Day\s*(\d+)", c.title or "", re.IGNORECASE)
                if m:
                    c.day = int(m.group(1))
            except Exception:
                pass

        if new_challenges:
            db.add_all(new_challenges)
            db.commit()
            print(f"Successfully added {len(new_challenges)} new challenges to the database.")
            return len(new_challenges)
        else:
            print("Challenges already exist in the database. No new challenges were added.")
            return 0

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
        return 0

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()