import json
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from functools import wraps
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Callable


QUESTIONS_FILE = Path("questions.json")
RESULTS_FILE = Path("results.json")
DIFFICULTIES = ("easy", "medium", "hard")
OPTIONS_PER_QUESTION = 4
MAX_ATTEMPTS = 2
QUESTION_TIME_LIMIT = 15


def quiz_timer(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print("\nQuiz is starting...")
        start = time.time()

        result = func(*args, **kwargs)

        end = time.time()
        print(f"\nQuiz completed in {end - start:.2f} seconds.")
        return result

    return wrapper


@dataclass
class Question:
    text: str
    options: list[str]
    answer_index: int
    topic: str
    difficulty: str

    @property
    def answer(self) -> str:
        return self.options[self.answer_index]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["answer"] = self.answer
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Question | None":
        try:
            text = str(data["text"]).strip()
            options = [str(option).strip() for option in data["options"]]
            topic = str(data["topic"]).strip()
            difficulty = str(data["difficulty"]).strip().lower()

            if "answer_index" in data:
                answer_index = int(data["answer_index"])
            else:
                answer = str(data["answer"]).strip()
                answer_index = options.index(answer)

            if (
                not text
                or len(options) != OPTIONS_PER_QUESTION
                or any(not option for option in options)
                or not 0 <= answer_index < OPTIONS_PER_QUESTION
                or not topic
                or difficulty not in DIFFICULTIES
            ):
                return None

            return cls(text, options, answer_index, topic, difficulty)
        except (KeyError, TypeError, ValueError):
            return None


class QuestionBank:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.questions = self.load()

    def load(self) -> list[Question]:
        data = load_json_list(self.file_path)
        questions = []

        for item in data:
            if isinstance(item, dict):
                question = Question.from_dict(item)
                if question is not None:
                    questions.append(question)

        return questions

    def save(self) -> None:
        save_json_list(self.file_path, [question.to_dict() for question in self.questions])

    def add_question(self, question: Question) -> None:
        self.questions.append(question)
        self.save()

    def get_filtered(self, topic: str, difficulty: str) -> list[Question]:
        topic = topic.strip().lower()
        difficulty = difficulty.strip().lower()

        return [
            question
            for question in self.questions
            if question.topic.lower() == topic and question.difficulty == difficulty
        ]

    def topics(self) -> list[str]:
        return sorted({question.topic for question in self.questions}, key=str.lower)


class ResultsManager:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.results = self.load()

    def load(self) -> list[dict[str, Any]]:
        return [
            result
            for result in load_json_list(self.file_path)
            if isinstance(result, dict)
            and {"name", "score", "total", "percentage", "date"} <= set(result)
        ]

    def save(self) -> None:
        save_json_list(self.file_path, self.results)

    def add_result(self, name: str, score: int, total: int) -> None:
        if total <= 0:
            return

        result = {
            "name": name,
            "score": score,
            "total": total,
            "percentage": round((score / total) * 100, 2),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        self.results.append(result)
        self.save()

    def leaderboard(self) -> None:
        if not self.results:
            print("No results yet!")
            return

        sorted_results = sorted(
            self.results,
            key=lambda result: (result["percentage"], result["score"]),
            reverse=True,
        )

        print("\n--- LEADERBOARD ---")
        for index, result in enumerate(sorted_results[:10], 1):
            print(
                f"{index}. {result['name']} - {result['score']}/{result['total']} "
                f"({result['percentage']}%) on {result['date']}"
            )

    def statistics(self) -> None:
        if not self.results:
            print("No statistics available!")
            return

        total_attempts = len(self.results)
        average_score = sum(result["percentage"] for result in self.results) / total_attempts
        best_score = max(result["percentage"] for result in self.results)

        print("\n--- STATISTICS ---")
        print(f"Total Attempts: {total_attempts}")
        print(f"Average Score: {average_score:.2f}%")
        print(f"Best Score: {best_score:.2f}%")


class QuizEngine:
    def __init__(self, bank: QuestionBank, results_manager: ResultsManager):
        self.bank = bank
        self.results_manager = results_manager

    @quiz_timer
    def start(self) -> None:
        if not self.bank.questions:
            print("No questions available. Add questions first.")
            return

        name = prompt_required("Enter your name: ")
        topic = self.choose_topic()
        difficulty = prompt_choice("Choose difficulty", DIFFICULTIES)

        questions = self.bank.get_filtered(topic, difficulty)

        if not questions:
            print("No questions found for that topic and difficulty.")
            return

        random.shuffle(questions)
        score = 0

        for question_number, question in enumerate(questions, 1):
            if self.ask_question(question, question_number, len(questions)):
                score += 1

        percentage = round((score / len(questions)) * 100, 2)

        print("\n--- QUIZ COMPLETE ---")
        print(f"Final Score: {score}/{len(questions)}")
        print(f"Percentage: {percentage}%")

        self.results_manager.add_result(name, score, len(questions))

    def choose_topic(self) -> str:
        topics = self.bank.topics()

        if not topics:
            return prompt_required("Choose topic: ")

        print("\nAvailable topics:")
        for index, topic in enumerate(topics, 1):
            print(f"{index}. {topic}")

        while True:
            choice = input("Choose topic by number or name: ").strip()

            if choice.isdigit():
                topic_index = int(choice) - 1
                if 0 <= topic_index < len(topics):
                    return topics[topic_index]

            for topic in topics:
                if topic.lower() == choice.lower():
                    return topic

            print("Invalid topic. Please choose one from the list.")

    def ask_question(self, question: Question, question_number: int, total: int) -> bool:
        print(f"\nQuestion {question_number}/{total}: {question.text}")

        for index, option in enumerate(question.options, 1):
            print(f"{index}. {option}")

        start_time = time.time()
        attempts = 0

        while attempts < MAX_ATTEMPTS:
            remaining_time = QUESTION_TIME_LIMIT - int(time.time() - start_time)

            if remaining_time <= 0:
                print("Time is up!")
                break

            choice = prompt_int(
                f"Your answer (1-{OPTIONS_PER_QUESTION}) | "
                f"Attempts left: {MAX_ATTEMPTS - attempts} | "
                f"Time left: {remaining_time}s: ",
                1,
                OPTIONS_PER_QUESTION,
            )

            if choice - 1 == question.answer_index:
                print("Correct!")
                return True

            attempts += 1
            if attempts < MAX_ATTEMPTS:
                print("Wrong! Try again.")
            else:
                print("Wrong!")

        print(f"Correct answer: {question.answer}")
        return False


def load_json_list(file_path: Path) -> list[Any]:
    if not file_path.exists():
        return []

    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, JSONDecodeError) as error:
        print(f"Could not read {file_path}: {error}")
        return []

    if not isinstance(data, list):
        print(f"{file_path} must contain a JSON list. Starting with an empty list.")
        return []

    return data


def save_json_list(file_path: Path, data: list[Any]) -> None:
    try:
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except OSError as error:
        print(f"Could not save {file_path}: {error}")


def prompt_required(message: str) -> str:
    while True:
        value = input(message).strip()
        if value:
            return value
        print("This field cannot be empty.")


def prompt_choice(message: str, choices: tuple[str, ...]) -> str:
    formatted_choices = "/".join(choices)

    while True:
        value = input(f"{message} ({formatted_choices}): ").strip().lower()
        if value in choices:
            return value
        print(f"Choose one of: {formatted_choices}.")


def prompt_int(message: str, minimum: int, maximum: int) -> int:
    while True:
        try:
            value = int(input(message))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if minimum <= value <= maximum:
            return value

        print(f"Choose a number from {minimum} to {maximum}.")


def add_question_ui(bank: QuestionBank) -> None:
    print("\n--- ADD QUESTION ---")

    text = prompt_required("Question: ")
    options = [
        prompt_required(f"Option {index}: ")
        for index in range(1, OPTIONS_PER_QUESTION + 1)
    ]
    answer_index = prompt_int("Correct option (1-4): ", 1, OPTIONS_PER_QUESTION) - 1
    topic = prompt_required("Topic: ")
    difficulty = prompt_choice("Difficulty", DIFFICULTIES)

    question = Question(text, options, answer_index, topic, difficulty)
    bank.add_question(question)

    print("Question added successfully!")


def main() -> None:
    bank = QuestionBank(QUESTIONS_FILE)
    results = ResultsManager(RESULTS_FILE)
    quiz = QuizEngine(bank, results)

    menu_actions = {
        "1": quiz.start,
        "2": lambda: add_question_ui(bank),
        "3": results.leaderboard,
        "4": results.statistics,
    }

    while True:
        print("\n--- QUIZ SYSTEM ---")
        print("1. Start Quiz")
        print("2. Add Question")
        print("3. View Leaderboard")
        print("4. View Statistics")
        print("5. Exit")

        choice = input("Choose: ").strip()

        if choice == "5":
            print("Goodbye!")
            break

        action = menu_actions.get(choice)
        if action is None:
            print("Invalid choice!")
        else:
            action()


if __name__ == "__main__":
    main()
