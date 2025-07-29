#!/usr/bin/env python3

"""Vocabulary Learning Application.

This application allows users to create vocabulary topics, add words with translations
and context sentences, and test their memorization through interactive quizzes.
"""

import json
import os
from typing import List, Optional, NoReturn
from dataclasses import dataclass, asdict, field

TOPICS_FOLDER = f"{os.path.dirname(os.path.abspath(__file__))}/topics"


@dataclass
class VocabularyItem:
    """Represents a vocabulary word with its metadata.

    Attributes:
        word: The target language word to learn
        translation: Native language translation of the word
        contexts: List of example sentences using the word
        memorization: Score (0.0-1.0) representing how well the word is memorized
    """

    word: str
    translation: str
    contexts: List[str] = field(default_factory=list)
    memorization: float = 0


class VocabularyFilesManager:
    """Handles persistence of vocabulary items to JSON files.

    Provides methods to create, read, update and delete vocabulary items
    organized by topics in JSON format.
    """

    @staticmethod
    def create_topic_path(topic: str) -> str:
        """Generate file path for a topic's vocabulary storage.

        Args:
            topic: Name of the vocabulary topic

        Returns:
            Absolute path to the topic's JSON file
        """
        return f"{TOPICS_FOLDER}/{topic}.json"

    def check_topic_existence(self, topic: str) -> bool:
        """Verify if a topic file exists.

        Args:
            topic: Name of vocabulary topic

        Returns:
            True if topic exists, False otherwise
        """
        return os.path.exists(self.create_topic_path(topic))

    def load_vocabulary_items(
        self, topic: str
    ) -> Optional[List[VocabularyItem]]:
        """Load vocabulary items from a topic file.

        Args:
            topic: Name of vocabulary topic

        Returns:
            List of VocabularyItem objects sorted by memorization score,
            or None if topic doesn't exist
        """
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

    def dump_vocabulary_items(
        self, topic: str, items: List[VocabularyItem]
    ) -> None:
        """Save vocabulary items to a topic file.

        Args:
            topic: Name of vocabulary topic
            items: List of VocabularyItem objects to save
        """
        if not self.check_topic_existence(topic):
            return
        topic_path = self.create_topic_path(topic)

        with open(topic_path, "w", encoding="utf-8") as t:
            json.dump(
                [asdict(item) for item in items],
                t,
                indent=4,
                ensure_ascii=False,
            )

    def add_item_to_topic(self, topic: str, item: VocabularyItem) -> None:
        """Add a new vocabulary item to a topic.

        Args:
            topic: Name of vocabulary topic
            item: VocabularyItem to add
        """
        items = self.load_vocabulary_items(topic) or []
        items.append(item)
        self.dump_vocabulary_items(topic, items)


class Application:
    """Main application class handling user interaction and vocabulary management."""

    def __init__(self) -> None:
        self.file_manager = VocabularyFilesManager()

    @staticmethod
    def list_options() -> None:
        """Display all available commands to the user."""
        print()
        print(" - [cr  <Topic> ]      - Create a new topic")
        print(" - [add <Topic> ]      - Add word to dictionary")
        print(" - [voc <Topic> ]      - Vocabulary test")
        print(" - [top         ]      - See all topics")
        print(" - [help        ]      - Print all options")
        print(" - [exit        ]      - Exit application\n")

    @staticmethod
    def print_padded(message: str) -> None:
        """Print message with vertical padding.

        Args:
            message: Text to display
        """
        print(f"\n{message}\n")

    def create_topic(self, topic: str) -> None:
        """Create a new vocabulary topic.

        Args:
            topic: Name of topic to create
        """
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
        """Add new vocabulary item to specified topic.

        Args:
            topic: Target topic name
        """
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
        """Conduct vocabulary test for specified topic.

        Args:
            topic: Topic name to test
        """
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
        """Display all available vocabulary topics."""
        if not os.path.exists(TOPICS_FOLDER):
            self.print_padded("No topics exist yet")
            return

        topics = [
            f[:-5] for f in os.listdir(TOPICS_FOLDER) if f.endswith(".json")
        ]
        if not topics:
            self.print_padded("No topics exist yet")
            return

        self.print_padded("Available topics:")
        for topic in topics:
            print(f"- {topic}")
        print()

    def exit_app(self) -> NoReturn:
        """Terminate application with goodbye message."""
        self.print_padded("Goodbye!")
        exit()

    def handle_user_input(self) -> None:
        """Process user commands from terminal input."""
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
        """Main application loop."""
        self.list_options()
        while True:
            self.handle_user_input()


def main() -> NoReturn:
    """Entry point for the vocabulary learning application."""
    app = Application()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Application.print_padded("Goodbye!")
