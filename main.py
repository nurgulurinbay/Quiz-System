import json

FILE = "questions.json"


# -------- LOAD --------
def load_questions():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []


# -------- SAVE --------
def save_questions(questions):
    with open(FILE, "w") as f:
        json.dump(questions, f, indent=4)


# -------- ADD QUESTION --------
def add_question():
    questions = load_questions()

    print("\n--- Add New Question ---")
    text = input("Question: ")

    options = []
    for i in range(4):
        opt = input(f"Option {i+1}: ")
        options.append(opt)

    # FIXED: store correct option text
    while True:
        try:
            correct_index = int(input("Correct option number (1-4): "))
            if 1 <= correct_index <= 4:
                answer = options[correct_index - 1]
                break
            else:
                print("Enter number from 1 to 4!")
        except:
            print("Invalid input!")

    question = {
        "text": text,
        "options": options,
        "answer": answer
    }

    questions.append(question)
    save_questions(questions)

    print("✅ Question added!")


# -------- START QUIZ --------
def start_quiz():
    questions = load_questions()

    if not questions:
        print("⚠ No questions available!")
        return

    score = 0

    for q in questions:
        print("\n" + q["text"])

        for i, opt in enumerate(q["options"], 1):
            print(f"{i}. {opt}")

        while True:
            try:
                choice = int(input("Your answer (1-4): "))
                if 1 <= choice <= 4:
                    break
                else:
                    print("Enter number from 1 to 4!")
            except:
                print("Invalid input!")

        if q["options"][choice - 1] == q["answer"]:
            print("✅ Correct!")
            score += 1
        else:
            print(f"❌ Wrong! Correct answer: {q['answer']}")

    print(f"\n🎯 Final Score: {score}/{len(questions)}")


# -------- MENU --------
def main():
    while True:
        print("\n=== QUIZ SYSTEM ===")
        print("1. Start Quiz")
        print("2. Add Question")
        print("3. Exit")

        choice = input("Choose: ")

        if choice == "1":
            start_quiz()
        elif choice == "2":
            add_question()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")


# -------- RUN --------
if __name__ == "__main__":
    main()