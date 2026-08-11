# tests/test_loader.py
from pathlib import Path

from loader.config_loader import ConfigLoader


def main():

    loader = ConfigLoader(Path("config"))

    keyboard = loader.load_jsonc(
        loader.config_root /
        "keyboards" /
        "k04mini.jsonc"
    )

    print(keyboard)


if __name__ == "__main__":
    main()