from typing import List

from .message import Message


class Chat:
    def __init__(self, key_remote_jid, subject: str, sort_timestamp, name: str, messages: List[Message]):
        self.key_remote_jid = key_remote_jid
        self.subject = subject
        self.sort_timestamp = sort_timestamp
        self.name = name
        self.phone_number = key_remote_jid.split("@")[0]
        self.title = self.__get_chat_title()
        self.messages = messages

    def __str__(self) -> str:
        return f"{self.key_remote_jid} {self.title}"

    def __get_chat_title(self):
        if self.subject is not None:
            return self.subject
        elif self.name is not None:
            return self.name
        else:
            return self.phone_number
