#!/usr/bin/env python3

import json
import os
from typing import List, Optional, NoReturn
from dataclasses import dataclass, asdict, field

TOPICS_FOLDER = f"{os.path.dirname(os.path.abspath(__file__))}/topics"


@dataclass
class VocabularyItem:
    word: str
    translation: str
    contexts: List[str] = field(default_factory=list)
    memorization: float = 0


class VocabularyFilesManager:

    @staticmethod
    def create_topic_path(topic: str) -> str:
        return f"{TOPICS_FOLDER}/{topic}.json"

    def check_topic_existence(self, topic: str) -> bool:
        return os.path.exists(self.create_topic_path(topic))

    def load_vocabulary_items(self, topic: str) -> Optional[List[VocabularyItem]]:

        if not self.check_topic_existence(topic):
            return

        topic_path = self.create_topic_path(topic)
        try:
            with open(topic_path, "r", encoding="utf-8") as t:
                data = json.load(t)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        items = [VocabularyItem(**item) for item in data]
        items.sort(key=lambda x: x.memorization, reverse=True)
        return items

    def dump_vocabulary_items(self, topic: str, items: List[VocabularyItem]) -> None:
        if not self.check_topic_existence(topic):
            return
        topic_path = self.create_topic_path(topic)

        with open(topic_path, "w", encoding="utf-8") as t:
            json.dump([asdict(item) for item in items], t, indent=4, ensure_ascii=False)

    def add_item_to_topic(self, topic: str, item: VocabularyItem) -> None:
        items = self.load_vocabulary_items(topic) or []
        items.append(item)
        self.dump_vocabulary_items(topic, items)


class Application:
    def __init__(self) -> None:
        self.file_manager = VocabularyFilesManager()

    @staticmethod
    def list_options() -> None:
        print()
        print(" - [cr  <Topic> ]      - Create a new topic")
        print(" - [add <Topic> ]      - Add word to dictionary")
        print(" - [voc <Topic> ]      - Vocabulary test")
        print(" - [top         ]      - See all topics")
        print(" - [help        ]      - Print all options")
        print(" - [exit        ]      - Exit application\n")

    @staticmethod
    def print_padded(message: str) -> None:
        print(f"\n{message}\n")

    def create_topic(self, topic: str) -> None:
        if not topic.strip():
            self.print_padded("Error: Topic name cannot be empty")
            return

        if self.file_manager.check_topic_existence(topic):
            self.print_padded(f"Error: Topic {topic} already exists")
            return

        try:
            os.makedirs(TOPICS_FOLDER, exist_ok=True)
        except OSError as e:
            self.print_padded("Error creating topics folder: {e}")
            return

        topic_path = self.file_manager.create_topic_path(topic)
        try:
            with open(topic_path, "w", encoding="utf-8") as t:
                json.dump([], t)
            self.print_padded(f"Topic {topic} created successfully!")
        except IOError as e:
            self.print_padded(f"Error creating topic file: {e}")
        except Exception as e:
            self.print_padded(f"Unexpected error: {e}")

    def add_item(self, topic: str) -> None:
        if not self.file_manager.check_topic_existence(topic):
            self.print_padded("This topic does not exist yet")
            return

        word = input("Enter the word: ").strip()
        if not word:
            self.print_padded("Word cannot be empty")
            return

        translation = input("Enter the translation: ").strip()

        if not translation:
            self.print_padded("Translation cannot be empty")
            return

        item = VocabularyItem(
            word=word,
            translation=translation,
        )

        print("Enter context for the word (empty to finish):")
        while context := input("> ").strip():
            item.contexts.append(context)

        self.file_manager.add_item_to_topic(topic, item)

        self.print_padded("Vocabulary item has been added successfully")

    def vocabulary_test(self, topic: str) -> None:
        if not self.file_manager.check_topic_existence(topic):
            self.print_padded("This topic does not exist yet")
            return

        items = self.file_manager.load_vocabulary_items(topic)

        if not items:
            self.print_padded("No vocabulary items in this topic")
            return

        for index, item in enumerate(items):

            for i, context in enumerate(item.contexts):
                print(f"{i + 1}. {context}\n")

            print(f"Word: {item.word}")

            user_translation = input("Provide a correct translation: ")
            correct_translation = item.translation.lower()

            if user_translation == correct_translation:
                print("CORRECT!")
                items[index].memorization = min(1.0, item.memorization + 0.1)
            else:
                print(f"WRONG! Correct: {item.translation}")
                items[index].memorization = max(0.0, item.memorization - 0.1)
            print()

        self.file_manager.dump_vocabulary_items(topic, items)

    def list_topics(self) -> None:
        if not os.path.exists(TOPICS_FOLDER):
            self.print_padded("No topics exist yet")
            return

        topics = [f[:-5] for f in os.listdir(TOPICS_FOLDER) if f.endswith(".json")]
        if not topics:
            self.print_padded("No topics exist yet")
            return

        self.print_padded("Available topics:")
        for topic in topics:
            print(f"- {topic}")
        print()

    def exit_app(self) -> NoReturn:
        self.print_padded("Goodbye!")
        exit()

    def handle_user_input(self) -> None:
        user_input = input("> ").strip().lower()
        if not user_input:
            return

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
                self.list_options()
            elif cmd == "exit":
                self.exit_app()
            else:
                self.print_padded("Invalid command. Type 'help' for options.")
        except IndexError:
            self.print_padded("Not enough arguments for the command")

    def run(self) -> NoReturn:
        self.list_options()
        while True:
            self.handle_user_input()


def main() -> NoReturn:
    app = Application()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Application.print_padded("Good Bye!")
