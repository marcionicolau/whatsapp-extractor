import time


class Message:
    def __init__(self, received_timestamp, remote_resource, key_from_me, data, media_caption, media_wa_type, sender):
        self.received_timestamp = received_timestamp
        self.remote_resource = remote_resource
        self.key_from_me = key_from_me
        self.data = data
        self.media_caption = media_caption
        self.media_wa_type = media_wa_type
        self.received_timestamp_str = self._timestamp_to_str(received_timestamp)
        self.sender = sender

    @classmethod
    def _timestamp_to_str(cls, timestamp: str) -> str:
        ts = int(timestamp) / 1000.0
        return time.strftime('%d.%m.%Y %H:%M', time.localtime(ts))

    def get_content(self) -> str:
        media_caption = self.media_caption if self.media_caption is not None else ""

        if self.media_wa_type == 0:
            return self.data
        elif self.media_wa_type == 1:
            return f"[IMAGE] {media_caption}"
        elif self.media_wa_type == 2:
            return f"[AUDIO] {media_caption}"
        elif self.media_wa_type == 3:
            return f"[VIDEO] {media_caption}"
        elif self.media_wa_type == 5:
            return f"[Location] {media_caption}"
        elif self.media_wa_type == 7:
            return f"[System Message] {media_caption}"
        elif self.media_wa_type == 9:
            return f"[Document] {media_caption}"
        elif self.media_wa_type == 16:
            return f"[Live Location] {media_caption}"
        else:
            return self.data

    def get_sender_name(self) -> str:
        if self.sender:
            return self.sender
        elif self.remote_resource:
            return self.remote_resource.split("@")[0]
        else:
            return self.remote_resource

    def __str__(self) -> str:
        if self.key_from_me:
            return f"> {self.received_timestamp_str} - {self.get_content()}"
        else:
            return f"< {self.received_timestamp_str} - {self.get_content()}"
