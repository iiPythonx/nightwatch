# Copyright (c) 2024 iiPython

class User():
    def __init__(self, name: str, color: str) -> None:
        self.name, self.color = name, color

    def __repr__(self) -> str:
        return self.name

class Message():
    def __init__(self, user: User, text: str) -> None:
        self.user, self.text = user, text
