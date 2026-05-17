import json
import random
import time
from datetime import datetime

QUESTIONS_FILE = "questions.json"
RESULTS_FILE = "results.json"

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

    def add_question(self, question):
        self.questions.append(question.to_dict())
        self.save()

    def get_filtered(self, topic, difficulty):
        return [
            q for q in self.questions
            if q["topic"].lower() == topic.lower()
            and q["difficulty"].lower() == difficulty.lower()
        ]

class ResultsManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.results = self.load()

    def load(self):
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except:
            return []

    def save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.results, f, indent=4)

    def add_result(self, name, score, total):
        result = {
            "name": name,
            "score": score,
            "total": total,
            "percentage": round((score / total) * 100, 2),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.results.append(result)
        self.save()

    def leaderboard(self):
        if not self.results:
            print("No results yet!")
            return

        sorted_results = sorted(
            self.results,
            key=lambda x: x["percentage"],
            reverse=True
        )

        print("\n--- LEADERBOARD ---")
        for i, r in enumerate(sorted_results[:10], 1):
            print(
                f"{i}. {r['name']} - {r['score']}/{r['total']} "
                f"({r['percentage']}%) on {r['date']}"
            )

    def statistics(self):
        if not self.results:
            print("No statistics available!")
            return

        total_attempts = len(self.results)
        avg_score = sum(r["percentage"] for r in self.results) / total_attempts
        best_score = max(r["percentage"] for r in self.results)

        print("\n--- STATISTICS ---")
        print(f"Total Attempts: {total_attempts}")
        print(f"Average Score: {avg_score:.2f}%")
        print(f"Best Score: {best_score:.2f}%")

class QuizEngine:
    def __init__(self, bank, results_manager):
        self.bank = bank
        self.results_manager = results_manager

    def start(self):
        name = input("Enter your name: ")
        topic = input("Choose topic: ")
        difficulty = input("Choose difficulty (easy/medium/hard): ")

        questions = self.bank.get_filtered(topic, difficulty)

        if not questions:
            print("No questions found!")
            return

        random.shuffle(questions)

        score = 0
        max_attempts = 2
        time_limit = 15

        for q in questions:
            print("\n" + q["text"])

            for i, option in enumerate(q["options"], 1):
                print(f"{i}. {option}")

            attempts = 0
            answered_correctly = False

            start_time = time.time()

            while attempts < max_attempts:
                elapsed = time.time() - start_time

                if elapsed > time_limit:
                    print("Time is up!")
                    break

                try:
                    choice = int(
                        input(
                            f"Your answer (1-4) | Attempts left: "
                            f"{max_attempts - attempts}: "
                        )
                    )

                    if not 1 <= choice <= 4:
                        print("Choose between 1 and 4.")
                        continue

                    if q["options"][choice - 1] == q["answer"]:
                        print("Correct!")
                        score += 1
                        answered_correctly = True
                        break
                    else:
                        print("Wrong!")
                        attempts += 1

                except:
                    print("Invalid input!")

            if not answered_correctly:
                print(f"Correct answer: {q['answer']}")

        percentage = round((score / len(questions)) * 100, 2)

        print("\n--- QUIZ COMPLETE ---")
        print(f"Final Score: {score}/{len(questions)}")
        print(f"Percentage: {percentage}%")

        self.results_manager.add_result(name, score, len(questions))

def add_question_ui(bank):
    print("\n--- ADD QUESTION ---")

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

        print("Invalid choice!")

    topic = input("Topic: ")
    difficulty = input("Difficulty (easy/medium/hard): ")

    question = Question(text, options, answer, topic, difficulty)
    bank.add_question(question)

    print("Question added successfully!")

def main():
    bank = QuestionBank(QUESTIONS_FILE)
    results = ResultsManager(RESULTS_FILE)
    quiz = QuizEngine(bank, results)

    while True:
        print("\n--- QUIZ SYSTEM ---")
        print("1. Start Quiz")
        print("2. Add Question")
        print("3. View Leaderboard")
        print("4. View Statistics")
        print("5. Exit")

        choice = input("Choose: ")

        if choice == "1":
            quiz.start()

        elif choice == "2":
            add_question_ui(bank)

        elif choice == "3":
            results.leaderboard()

        elif choice == "4":
            results.statistics()

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()