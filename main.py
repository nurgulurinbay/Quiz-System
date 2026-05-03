import json
import random

FILE = "questions.json"


class Question:
    def __init__(self, text, options, answer, topic, difficulty):
        self.text = text
        self.options = options
        self.answer = answer
        self.topic = topic
        self.difficulty = difficulty

    def to_dict(self):
        return {
            "text": self.text,
            "options": self.options,
            "answer": self.answer,
            "topic": self.topic,
            "difficulty": self.difficulty
        }


class QuestionBank:
    def __init__(self, file_path):
        self.file_path = file_path
        self.questions = self.load()

    def load(self):
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except:
            return []

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.questions, f, indent=4)

    def add_question(self, question: Question):
        self.questions.append(question.to_dict())
        self.save()

    def get_filtered(self, topic, difficulty):
        return [
            q for q in self.questions
            if q["topic"] == topic and q["difficulty"] == difficulty
        ]


class QuizEngine:
    def __init__(self, bank: QuestionBank):
        self.bank = bank

    def start(self):
        topic = input("Choose topic: ")
        difficulty = input("Choose difficulty (easy/medium/hard): ")

        questions = self.bank.get_filtered(topic, difficulty)

        if not questions:
            print("No questions found for this filter!")
            return

        random.shuffle(questions)

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
                except:
                    pass
                print("Invalid input!")

            if q["options"][choice - 1] == q["answer"]:
                print("Correct!")
                score += 1
            else:
                print("Wrong!")

        print(f"\nFinal Score: {score}/{len(questions)}")


def add_question_ui(bank: QuestionBank):
    print("\n--- Add Question ---")

    text = input("Question: ")

    options = []
    for i in range(4):
        options.append(input(f"Option {i+1}: "))

    while True:
        try:
            correct = int(input("Correct option (1-4): "))
            if 1 <= correct <= 4:
                answer = options[correct - 1]
                break
        except:
            pass

    topic = input("Topic: ")
    difficulty = input("Difficulty (easy/medium/hard): ")

    q = Question(text, options, answer, topic, difficulty)
    bank.add_question(q)

    print("Question added!")


def main():
    bank = QuestionBank(FILE)
    quiz = QuizEngine(bank)

    while True:
        print("\n=== QUIZ SYSTEM ===")
        print("1. Start Quiz")
        print("2. Add Question")
        print("3. Exit")

        choice = input("Choose: ")

        if choice == "1":
            quiz.start()
        elif choice == "2":
            add_question_ui(bank)
        elif choice == "3":
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()