import os.path
import sqlite3
from multiprocessing import cpu_count
from os import PathLike
from sqlite3 import Connection, Cursor, Error, OperationalError
from typing import Dict, Optional, Tuple

from tqdm.contrib.concurrent import process_map

from .models.chat import Chat
from .models.message import Message


class WhatsAppExtractor:
    KeyType = Tuple[str, str | None, int]
    PathType = str | PathLike[str]

    def __init__(self, wa_db: Optional[PathType], msg_db: PathType,
                 output_path: PathType):

        self.wa_db = wa_db
        self.use_wa_db = wa_db is not None
        self.msg_db = msg_db
        self.txt_path = output_path
        self.export2txt = output_path is not None
        self._get_contacts()
        self.chats = []

    def _db_messages_type(self, cur: Cursor):
        """
        Check the WhatsApp database type
        :param cur: SQLite Cursor
        :return:
        """
        # Check which table to use: Older databases use the table "messages", newer ones the table "message"
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")

        self.older_databases = cur.fetchone() is not None

    def _db_connection(self, contact: bool = False) -> Connection:
        """ create a database connection to the SQLite database
        :param contact: Choose between contacts and messages database from WhastApp [default: False]
        :return: Connection object or None
        """
        conn = None

        try:
            conn = sqlite3.connect(self.msg_db if not contact else self.wa_db)
        except Error as e:
            print(e)

        return conn

    def _get_contacts(self):
        self.contacts = self._contacts_from_db() if self.use_wa_db else {}

    def _contacts_from_db(self) -> Dict[str, Optional[str]]:
        contacts = {}
        con = self._db_connection(True)
        cur = con.cursor()
        for jid, wa_name, display_name in cur.execute("SELECT jid, wa_name, display_name from wa_contacts"):
            if display_name:
                contacts[jid] = display_name
            elif wa_name:
                contacts[jid] = wa_name
        con.close()

        return contacts

    def _process_chats(self):
        conn = self._db_connection()
        query = "SELECT raw_string_jid as key_remote_jid, subject, sort_timestamp FROM chat_view WHERE sort_timestamp IS NOT NULL ORDER BY sort_timestamp DESC"
        chat_ids = conn.execute(query).fetchall()

        cur = conn.cursor()
        self._db_messages_type(cur)
        print("[+] Using table 'messages'") if self.older_databases else print("[+] Using table 'message'")
        conn.close()

        print(f"[+] Reading messages from {len(chat_ids)} chats.")

        process_map(self._load_single_chat, chat_ids,
                    desc='Parsing [Chats] ...', chunksize=int(cpu_count() // 2))

    def _load_single_chat(self, key: KeyType):
        conn = self._db_connection()

        if self.older_databases:
            query = """
                    SELECT received_timestamp, remote_resource, key_from_me, data, media_caption, media_wa_type 
                    FROM messages 
                    WHERE key_remote_jid =:key_remote_jid
                    ORDER BY max(receipt_server_timestamp, received_timestamp)
                    """
        else:
            query = """
                     SELECT
                        m.timestamp,
                        jid.raw_string,
                        m.from_me,
                        CASE
                            WHEN mr.revoked_key_id > 1 THEN '[Deleted]'
                            ELSE m.text_data
                        END AS text,
                        m.message_type
                    FROM message AS m
                    LEFT JOIN chat_view AS cv ON m.chat_row_id = cv._id
                    LEFT JOIN jid ON m.sender_jid_row_id = jid._id
                    LEFT JOIN message_revoked AS mr ON m._id = mr.message_row_id
                    WHERE cv.raw_string_jid =:key_remote_jid
                    ORDER BY max(receipt_server_timestamp, received_timestamp)
                   """

        try:
            with conn:
                messages_from_key = conn.execute(query, {"key_remote_jid": key[0]}).fetchall()
        except OperationalError as e:
            print(e)
        finally:
            conn.close()
            k_id, sub, s_timestamp = key
            list_of_messages = [Message(timestamp, remote_jid, from_me, data, data, message_type,
                                        self.contacts.get(remote_jid, None)) for
                                timestamp, remote_jid, from_me, data, message_type in messages_from_key]
            last_chat = Chat(k_id, sub, s_timestamp, self.contacts.get(k_id, None), list_of_messages)
            if self.export2txt:
                self._chat2txt(last_chat)

    def load_and_export(self):
        if self.export2txt:
            if not os.path.exists(self.txt_path):
                os.makedirs(self.txt_path)

        self._process_chats()

    def _chat2txt(self, actual_chat: Chat):
        messages = "\n".join([str(message) for message in actual_chat.messages])
        with open(f"{self.txt_path}/{actual_chat.key_remote_jid}.txt", "w", encoding="utf-8") as file:
            file.write(messages)
