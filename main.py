import json
import os
from typing import List
from dataclasses import dataclass, asdict, field

TOPICS_FOLDER = "topics"


@dataclass
class VocabularyItem:
    word: str
    translation: str
    contexts: List[str] = field(default_factory=list)
    memorising: float = 0


class VocabularyFilesManager:

    def create_topic_path(self, topic: str) -> str:
        return f"{TOPICS_FOLDER}/{topic}.json"

    def check_topic_existance(self, topic: str) -> bool:
        return os.path.exists(self.create_topic_path(topic))

    def load_vocabulary_items(self, topic: str) -> List[VocabularyItem]:
        topic_path = self.create_topic_path(topic)
        if not self.check_topic_existance(topic):
            return

        try:
            with open(topic_path, "r", encoding="utf-8") as t:
                data = json.load(t)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        items = [VocabularyItem(**item) for item in data]
        items.sort(key=lambda x: x.memorising, reverse=True)

        return items

    def dump_vocabulary_items(self, topic: str, items: List[VocabularyItem]) -> None:
        topic_path = self.create_topic_path(topic)
        if not self.check_topic_existance(topic):
            return

        with open(topic_path, "w", encoding="utf-8") as t:
            json.dump([asdict(item) for item in items], t, indent=4, ensure_ascii=False)

    def add_item_to_topic(self, topic: str, item: VocabularyItem) -> None:
        topic_path = self.create_topic_path(topic)
        items = self.load_vocabulary_items(topic)
        items.append(asdict(item))
        with open(topic_path, "w", encoding="utf-8") as t:
            json.dump(items, t, indent=4, ensure_ascii=False)


class Application:
    def __init__(self):
        self.file_manager = VocabularyFilesManager()

    @staticmethod
    def print_options() -> None:
        print()
        print(" - [cr  <Topic> ]     - Create a new topic")
        print(" - [add <Topic>]      - Add word to dictionary")
        print(" - [voc <Topic>]      - Vocabulary test")
        print(" - [top        ]      - See all topics")
        print(" - [help       ]      - Print all options\n")

    def create_topic(self, topic: str):
        if not topic.strip():
            print("Error: Topic name cannot be empty\n")
            return

        if self.file_manager.check_topic_existance(topic):
            print(f"Error: Topic '{topic}' already exists\n")
            return

        try:
            os.makedirs(TOPICS_FOLDER, exist_ok=True)
        except OSError as e:
            print(f"Error creating topics folder: {e}\n")
            return

        topic_path = self.file_manager.create_topic_path(topic)
        try:
            with open(topic_path, "w", encoding="utf-8") as t:
                json.dump([], t)
            print(f"Topic '{topic}' created successfully!\n")
        except IOError as e:
            print(f"Error creating topic file: {e}\n")
        except Exception as e:
            print(f"Unexpected error: {e}\n")

    def add_item(self, topic: str):
        if not self.file_manager.check_topic_existance(topic):
            print("This topic does not exist yet\n")
            return

        word = input("Enter the word: ").strip()
        if not word:
            print("Word cannot be empty")
            return

        translation = input("Enter the translation: ").strip()

        if not translation:
            print("Translation cannot be empty")
            return

        item = VocabularyItem(
            word=word,
            translation=translation,
        )

        context = input("Enter context for the word (empty to finish): ").strip()
        while context:
            context = input("Enter context for the word (empty to finish): ").strip()
            item.contexts.append(context)

        self.file_manager.add_item_to_topic(topic, item)

    def vocabulary_test(self, topic: str):
        if not self.file_manager.check_topic_existance(topic):
            print("This topic does not exist yet\n")
            return
        items = self.file_manager.load_vocabulary_items(topic)
        for ind_item, item in enumerate(items):

            for ind_context, context in enumerate(item.contexts):
                print(f"{ind_context + 1}. {context}\n")

            print(f"Word: {item.word}")

            user_translation = input("Provide a correct translation: ")
            correct_translation = item.translation.lower()

            if user_translation == correct_translation:
                print("CORRECT!")
                items[ind_item].memorising = min(1.0, item.memorising + 0.1)
            else:
                print(f"WRONG! Correct: {item.translation}")
                items[ind_item].memorising = max(0.0, item.memorising - 0.1)
            print()
        self.file_manager.dump_vocabulary_items(topic, items)

    def print_all_topics(self):
        if not os.path.exists(TOPICS_FOLDER):
            print("No topics exist yet\n")
            return

        topics = [f[:-5] for f in os.listdir(TOPICS_FOLDER) if f.endswith(".json")]
        if not topics:
            print("No topics exist yet\n")
            return

        print("\nAvailable topics:")
        for topic in topics:
            print(f"- {topic}")
        print()

    def handle_user_input(self):
        user_input = input("> ").strip().lower()
        parts = user_input.split()
        cmd = parts[0]
        args = parts[1:]

        try:
            if cmd == "cr" and args:
                self.create_topic(args[0])
            elif cmd == "add" and args:
                self.add_item(args[0])
            elif cmd == "voc" and args:
                self.vocabulary_test(args[0])
            elif cmd == "top":
                self.list_topics()
            elif cmd == "help":
                self.print_options()
            else:
                print("Invalid command. Type 'help' for options.")
        except IndexError:
            print("Not enough arguments for the command\n")

    def run(self):
        self.print_options()
        while True:
            self.handle_user_input()


def main():
    app = Application()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGood Bye!\n")
