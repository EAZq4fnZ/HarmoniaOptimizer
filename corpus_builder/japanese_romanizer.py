from __future__ import annotations

from unicodedata import category

ROMAJI_MAP = {
    "ア": "a",
    "イ": "i",
    "ウ": "u",
    "エ": "e",
    "オ": "o",

    "カ": "ka",
    "キ": "ki",
    "ク": "ku",
    "ケ": "ke",
    "コ": "ko",

    "サ": "sa",
    "シ": "shi",
    "ス": "su",
    "セ": "se",
    "ソ": "so",

    "タ": "ta",
    "チ": "ti",
    "ツ": "tu",
    "テ": "te",
    "ト": "to",

    "ナ": "na",
    "ニ": "ni",
    "ヌ": "nu",
    "ネ": "ne",
    "ノ": "no",

    "ハ": "ha",
    "ヒ": "hi",
    "フ": "fu",
    "ヘ": "he",
    "ホ": "ho",

    "マ": "ma",
    "ミ": "mi",
    "ム": "mu",
    "メ": "me",
    "モ": "mo",

    "ヤ": "ya",
    "ユ": "yu",
    "ヨ": "yo",

    "ラ": "ra",
    "リ": "ri",
    "ル": "ru",
    "レ": "re",
    "ロ": "ro",

    "ワ": "wa",
    "ヲ": "wo",
    "ン": "nn",
    "ヴ": "vu",
    "ー": "-",

    "ガ": "ga",
    "ギ": "gi",
    "グ": "gu",
    "ゲ": "ge",
    "ゴ": "go",

    "ザ": "za",
    "ジ": "ji",
    "ズ": "zu",
    "ゼ": "ze",
    "ゾ": "zo",

    "ダ": "da",
    "ヂ": "di",
    "ヅ": "du",
    "デ": "de",
    "ド": "do",

    "バ": "ba",
    "ビ": "bi",
    "ブ": "bu",
    "ベ": "be",
    "ボ": "bo",

    "パ": "pa",
    "ピ": "pi",
    "プ": "pu",
    "ペ": "pe",
    "ポ": "po",
}


DIGRAPH_MAP = {
    "キャ": "kya",
    "キュ": "kyu",
    "キョ": "kyo",

    "シャ": "sha",
    "シュ": "shu",
    "ショ": "sho",

    "チャ": "cha",
    "チュ": "chu",
    "チョ": "cho",

    "ニャ": "nya",
    "ニュ": "nyu",
    "ニョ": "nyo",

    "ヒャ": "hya",
    "ヒュ": "hyu",
    "ヒョ": "hyo",

    "ミャ": "mya",
    "ミュ": "myu",
    "ミョ": "myo",

    "リャ": "rya",
    "リュ": "ryu",
    "リョ": "ryo",

    "ギャ": "gya",
    "ギュ": "gyu",
    "ギョ": "gyo",

    "ジャ": "ja",
    "ジュ": "ju",
    "ジョ": "jo",

    "ビャ": "bya",
    "ビュ": "byu",
    "ビョ": "byo",

    "ピャ": "pya",
    "ピュ": "pyu",
    "ピョ": "pyo",

    "ティ": "thi",
    "ディ": "dhi",

    "ファ": "fa",
    "フィ": "fi",
    "フェ": "fe",
    "フォ": "fo",

    "ウィ": "wi",
    "ウェ": "we",
    "ウォ": "ulo",

    "ヴァ": "va",
    "ヴィ": "vi",
    "ヴェ": "ve",
    "ヴォ": "vo",

    "チェ": "che",
    "シェ": "she",
    "ジェ": "je",

    "ツァ": "tula",
    "ツィ": "tuli",
    "ツェ": "tule",
    "ツォ": "tulo",

    "トゥ": "tolu",
    "ドゥ": "dolu",
}


def _romanize_unit(
    text: str,
    index: int,
) -> tuple[str, int]:
    digraph = text[
        index:index + 2
    ]

    if digraph in DIGRAPH_MAP:
        return (
            DIGRAPH_MAP[digraph],
            2,
        )

    char = text[index]

    if char not in ROMAJI_MAP:
        raise ValueError(
            f"Unsupported katakana: {char}"
        )

    return (
        ROMAJI_MAP[char],
        1,
    )


def romanize_japanese_reading(
    text: str,
) -> str:
    result: list[str] = []
    index = 0

    while index < len(text):
        char = text[index]

        if char.isascii():
            result.append(char)
            index += 1
            continue

        if category(char).startswith("P"):
            result.append(char)
            index += 1
            continue

        if char == "ッ":
            next_index = index + 1

            if next_index >= len(text):
                raise ValueError(
                    "Small tsu must be followed by katakana"
                )

            next_romaji, _ = _romanize_unit(
                text,
                next_index,
            )

            first = next_romaji[0]

            if first in "aeiou":
                raise ValueError(
                    "Small tsu must be followed by a consonant"
                )

            result.append(first)
            index += 1
            continue

        romaji, consumed = _romanize_unit(
            text,
            index,
        )

        result.append(romaji)
        index += consumed

    return "".join(result)
