from os import PathLike

from fire import Fire

from wa_extractor.extractor import WhatsAppExtractor


def main(config_path: str | PathLike[str]):
    print("### WhatsApp Database Extractor ###")

    w_extractor = WhatsAppExtractor(config_path)
    w_extractor.load_and_export()
    print("[+] Finished")


if __name__ == "__main__":
    Fire(main)
