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


def test_romanize_preserves_unicode_symbols() -> None:
    assert romanize_japanese_reading(
        "★♪→♡"
    ) == "★♪→♡"

    assert romanize_japanese_reading(
        "テスト×テスト"
    ) == "tesuto×tesuto"


def test_romanize_supports_small_kana_explicitly() -> None:
    assert (
        romanize_japanese_reading(
            "ァ"
        )
        == "la"
    )


def test_romanize_deyu_as_delyu() -> None:
    assert romanize_japanese_reading(
        "デュ"
    ) == "delyu"

    assert romanize_japanese_reading(
        "エデュケーション"
    ) == "edelyuke-shonn"

    assert romanize_japanese_reading(
        "デュカス"
    ) == "delyukasu"


def test_romanize_japanese_reading_supports_small_kana_sequences() -> None:
    from corpus_builder.japanese_romanizer import (
        romanize_japanese_reading,
    )

    cases = (
        ("ナァ", "nala"),
        ("ネェ", "nele"),
        ("ルビィ", "rubili"),
    )

    for reading, expected in cases:
        assert (
            romanize_japanese_reading(
                reading
            )
            == expected
        )


def test_romanize_japanese_reading_supports_terminal_small_tsu() -> None:
    from corpus_builder.japanese_romanizer import (
        romanize_japanese_reading,
    )

    cases = (
        ("アッ", "altu"),
        ("ナッ", "naltu"),
        ("ポチッ", "potiltu"),
    )

    for reading, expected in cases:
        assert (
            romanize_japanese_reading(
                reading
            )
            == expected
        )


def test_romanize_japanese_reading_supports_foreign_small_kana_digraphs() -> None:
    from corpus_builder.japanese_romanizer import (
        romanize_japanese_reading,
    )

    cases = (
        (
            "フューチャー",
            "fulyu-cha-",
        ),
        (
            "スィーツ",
            "suli-tu",
        ),
        (
            "クォーツ",
            "kulo-tu",
        ),
    )

    for reading, expected in cases:
        assert (
            romanize_japanese_reading(
                reading
            )
            == expected
        )


def test_romanize_small_tsu_before_japanese_punctuation_as_explicit_ltu() -> None:
    assert romanize_japanese_reading(
        "アッ！"
    ) == "altu！"


def test_romanize_small_tsu_before_ascii_punctuation_as_explicit_ltu() -> None:
    assert romanize_japanese_reading(
        "ポチッ."
    ) == "potiltu."


def test_romanize_small_tsu_before_closing_quote_as_explicit_ltu() -> None:
    assert romanize_japanese_reading(
        "ポチッ」"
    ) == "potiltu」"


def test_romanize_small_tsu_before_symbol_as_explicit_ltu() -> None:
    assert romanize_japanese_reading(
        "アッ☆"
    ) == "altu☆"

def test_romanize_preserves_embedded_cyrillic() -> None:
    assert romanize_japanese_reading(
        "「ПM」ニヨルト"
    ) == "「ПM」niyoruto"


def test_romanize_preserves_cyrillic_word() -> None:
    assert romanize_japanese_reading(
        "ロシアゴ:галина"
    ) == "roshiago:галина"


def test_romanize_preserves_isolated_cyrillic_in_japanese_text() -> None:
    assert romanize_japanese_reading(
        "タチバナОシテ"
    ) == "tatibanaОshite"


def test_romanize_preserves_accented_latin_text() -> None:
    assert romanize_japanese_reading(
        "カトリックCathédraleデス"
    ) == "katorikkuCathédraledesu"


def test_romanize_preserves_greek_text() -> None:
    assert romanize_japanese_reading(
        "コレハτάμαデス"
    ) == "korehaτάμαdesu"



def test_romanize_maps_ideographic_zero_inside_reading() -> None:
    assert romanize_japanese_reading(
        "スケ〇ギョサイテン"
    ) == "sukemarugyosaitenn"


def test_romanize_maps_leading_ideographic_zero() -> None:
    assert romanize_japanese_reading(
        "〇トウオンシミンハナビ"
    ) == "marutouonnshiminnhanabi"



def test_romanize_collapses_repeated_small_tsu_before_consonant() -> None:
    assert romanize_japanese_reading(
        "アッッタリ"
    ) == "attari"


def test_romanize_collapses_mixed_repeated_small_tsu_before_consonant() -> None:
    assert romanize_japanese_reading(
        "タッっックサン"
    ) == "takkusann"


def test_romanize_collapses_repeated_small_tsu_before_punctuation() -> None:
    assert romanize_japanese_reading(
        "キテクレマシタッッ！！"
    ) == "kitekuremashitaltu！！"


def test_romanize_uses_explicit_small_tsu_before_vowel() -> None:
    assert romanize_japanese_reading(
        "ギャッアナル"
    ) == "gyaltuanaru"


def test_romanize_uses_explicit_small_tsu_before_vowel_in_sentence() -> None:
    assert romanize_japanese_reading(
        "マスッイガイ"
    ) == "masultuigai"



def test_romanize_preserves_non_ascii_number_symbols() -> None:
    assert romanize_japanese_reading(
        "➊ト➋"
    ) == "➊to➋"


def test_romanize_ideographic_zero_uses_explicit_harmonia_mapping() -> None:
    assert romanize_japanese_reading(
        "〇"
    ) == "maru"
