from os import PathLike, path
from typing import Optional
from fire import Fire

from WAExtractor.main import WhatsAppExtractor

PathType = str | PathLike[str]


def main(wa_db: Optional[PathType] = None,
        msg_db: PathType = path.join('data', 'db', 'msgstore.db'),
        output_path: PathType = path.join('outputs', 'chats_txt')):
    """
    Module to export chat messages from WhatsApp decrypted database
    :param output_path: Path to output chat text folder [default: 'outputs/chats_txt']
    :param wa_db: Path to the contacts database [Optional]
    :param msg_db: Path to the WhatsApp message database [default: 'data/db/msgstore.db']
    :return:
    """
    print("### WhatsApp Extractor ###")

    w_extractor = WhatsAppExtractor(wa_db, msg_db, output_path)
    w_extractor.load_and_export()
    print("[+] Finished")


if __name__ == "__main__":
    Fire(main)
