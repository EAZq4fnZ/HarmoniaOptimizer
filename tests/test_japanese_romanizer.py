from corpus_builder.japanese_romanizer import romanize_japanese_reading


def test_romanize_basic_reading() -> None:
    assert romanize_japanese_reading(
        "キョウハヨイテンキデス"
    ) == "kyouhayoitennkidesu"


def test_romanize_user_preferred_special_kana() -> None:
    assert romanize_japanese_reading(
        "シチツフジン"
    ) == "shititufujinn"


def test_romanize_sha_series() -> None:
    assert romanize_japanese_reading(
        "シャシュショ"
    ) == "shashusho"


def test_romanize_cha_series() -> None:
    assert romanize_japanese_reading(
        "チャチュチョ"
    ) == "chachucho"


def test_romanize_ja_series() -> None:
    assert romanize_japanese_reading(
        "ジャジュジョ"
    ) == "jajujo"


def test_romanize_small_tsu_doubles_next_consonant() -> None:
    assert romanize_japanese_reading(
        "カッタ"
    ) == "katta"

    assert romanize_japanese_reading(
        "キッテ"
    ) == "kitte"

    assert romanize_japanese_reading(
        "ザッシ"
    ) == "zasshi"

    assert romanize_japanese_reading(
        "マッチ"
    ) == "matti"


def test_romanize_small_tsu_before_digraph() -> None:
    assert romanize_japanese_reading(
        "マッチャ"
    ) == "maccha"

    assert romanize_japanese_reading(
        "イッショ"
    ) == "issho"


def test_romanize_long_vowel_mark_as_hyphen() -> None:
    assert romanize_japanese_reading(
        "コーヒー"
    ) == "ko-hi-"

    assert romanize_japanese_reading(
        "スーパー"
    ) == "su-pa-"


def test_romanize_foreign_sound_sequences() -> None:
    assert romanize_japanese_reading(
        "ティディ"
    ) == "thidhi"

    assert romanize_japanese_reading(
        "ファフィフェフォ"
    ) == "fafifefo"

    assert romanize_japanese_reading(
        "ウィウェウォ"
    ) == "wiweulo"

    assert romanize_japanese_reading(
        "ヴァヴィヴヴェヴォ"
    ) == "vavivuvevo"

    assert romanize_japanese_reading(
        "チェシェジェ"
    ) == "chesheje"

    assert romanize_japanese_reading(
        "ツァツィツェツォ"
    ) == "tulatulitule tulo".replace(
        " ",
        "",
    )

    assert romanize_japanese_reading(
        "トゥドゥ"
    ) == "toludolu"


def test_romanize_preserves_ascii() -> None:
    assert romanize_japanese_reading(
        "ABCキョウ"
    ) == "ABCkyou"

    assert romanize_japanese_reading(
        "Python3テスト"
    ) == "Python3tesuto"

    assert romanize_japanese_reading(
        "C++テスト"
    ) == "C++tesuto"


def test_romanize_preserves_non_ascii_symbols() -> None:
    assert romanize_japanese_reading(
        "キョウ。"
    ) == "kyou。"

    assert romanize_japanese_reading(
        "「テスト！」"
    ) == "「tesuto！」"

    assert romanize_japanese_reading(
        "：（）；"
    ) == "：（）；"
