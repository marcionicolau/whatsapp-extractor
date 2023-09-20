from os import PathLike

from fire import Fire

from WAExtractor.main import WhatsAppExtractor


def main(config_path: str | PathLike[str]):
    """
    Module to export chat messages from WhatsApp decrypted database
    :param config_path: Path to the configuration file 'new-config.cfg'
    :return:
    """
    print("### WhatsApp Database Extractor ###")

    w_extractor = WhatsAppExtractor(config_path)
    w_extractor.load_and_export()
    print("[+] Finished")


if __name__ == "__main__":
    Fire(main)
