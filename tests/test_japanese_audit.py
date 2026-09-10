from corpus_builder.japanese_audit import (
    audit_japanese_morphemes,
    audit_japanese_text,
)


class FakeMorpheme:
    def __init__(
        self,
        *,
        surface: str,
        reading: str,
        part_of_speech: str = "名詞",
    ) -> None:
        self._surface = surface
        self._reading = reading
        self._part_of_speech = part_of_speech

    def surface(self) -> str:
        return self._surface

    def reading_form(self) -> str:
        return self._reading

    def part_of_speech(self) -> tuple[str, ...]:
        return (
            self._part_of_speech,
            "*",
            "*",
            "*",
            "*",
            "*",
        )

    def is_oov(self) -> bool:
        return False


def test_audit_japanese_morphemes_collects_romanizer_failure() -> None:
    morphemes = (
        FakeMorpheme(
            surface="今日",
            reading="キョウ",
        ),
        FakeMorpheme(
            surface="未知",
            reading="ㇰ",
        ),
        FakeMorpheme(
            surface="。",
            reading="。",
            part_of_speech="補助記号",
        ),
    )

    result = audit_japanese_morphemes(
        morphemes,
        romanizer=lambda text: (
            "kyou"
            if text == "キョウ"
            else (
                "。"
                if text == "。"
                else (_ for _ in ()).throw(
                    ValueError(
                        "Unsupported katakana: ㇰ"
                    )
                )
            )
        ),
        context="今日は未知。",
    )

    assert result.total_morphemes == 3
    assert result.successful_morphemes == 2
    assert result.failed_morphemes == 1

    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.surface == "未知"
    assert issue.reading == "ㇰ"
    assert issue.part_of_speech == "名詞"
    assert issue.context == "今日は未知。"
    assert issue.error == "Unsupported katakana: ㇰ"
    assert issue.count == 1


def test_audit_japanese_morphemes_preserves_symbol_surface() -> None:
    morphemes = (
        FakeMorpheme(
            surface="：",
            reading="キゴウ",
            part_of_speech="補助記号",
        ),
    )

    received: list[str] = []

    def fake_romanizer(text: str) -> str:
        received.append(text)
        return text

    result = audit_japanese_morphemes(
        morphemes,
        romanizer=fake_romanizer,
        context="：",
    )

    assert received == ["："]
    assert result.total_morphemes == 1
    assert result.successful_morphemes == 1
    assert result.failed_morphemes == 0
    assert result.issues == ()


def test_audit_japanese_morphemes_aggregates_duplicate_failures() -> None:
    morphemes = (
        FakeMorpheme(
            surface="未知",
            reading="ㇰ",
        ),
        FakeMorpheme(
            surface="未知",
            reading="ㇰ",
        ),
        FakeMorpheme(
            surface="未知",
            reading="ㇰ",
        ),
    )

    def failing_romanizer(text: str) -> str:
        raise ValueError(
            f"Unsupported katakana: {text}"
        )

    result = audit_japanese_morphemes(
        morphemes,
        romanizer=failing_romanizer,
        context="未知未知未知",
    )

    assert result.total_morphemes == 3
    assert result.successful_morphemes == 0
    assert result.failed_morphemes == 3

    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.surface == "未知"
    assert issue.reading == "ㇰ"
    assert issue.count == 3


def test_audit_japanese_morphemes_skips_whitespace() -> None:
    morphemes = (
        FakeMorpheme(
            surface="ABC",
            reading="エービーシー",
        ),
        FakeMorpheme(
            surface=" ",
            reading="キゴウ",
        ),
        FakeMorpheme(
            surface="今日",
            reading="キョウ",
        ),
    )

    received: list[str] = []

    def fake_romanizer(text: str) -> str:
        received.append(text)
        return text

    result = audit_japanese_morphemes(
        morphemes,
        romanizer=fake_romanizer,
        context="ABC 今日",
    )

    assert received == [
        "ABC",
        "キョウ",
    ]

    assert result.total_morphemes == 2
    assert result.successful_morphemes == 2
    assert result.failed_morphemes == 0
    assert result.issues == ()


def test_audit_japanese_text_tokenizes_source_text() -> None:
    from corpus_builder.japanese_audit import (
        audit_japanese_text,
    )

    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ) -> tuple[FakeMorpheme, ...]:
            assert text == "今日は未知。"

            return (
                FakeMorpheme(
                    surface="今日",
                    reading="キョウ",
                ),
                FakeMorpheme(
                    surface="は",
                    reading="ハ",
                    part_of_speech="助詞",
                ),
                FakeMorpheme(
                    surface="未知",
                    reading="ㇰ",
                ),
                FakeMorpheme(
                    surface="。",
                    reading="。",
                    part_of_speech="補助記号",
                ),
            )

    def fake_romanizer(text: str) -> str:
        if text == "ㇰ":
            raise ValueError(
                "Unsupported katakana: ㇰ"
            )

        return text

    result = audit_japanese_text(
        "今日は未知。",
        tokenizer=FakeTokenizer(),
        romanizer=fake_romanizer,
    )

    assert result.total_morphemes == 4
    assert result.successful_morphemes == 3
    assert result.failed_morphemes == 1

    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.surface == "未知"
    assert issue.reading == "ㇰ"
    assert issue.context == "今日は未知。"
    assert issue.count == 1



def test_audit_japanese_text_normalizes_source_before_tokenizing() -> None:
    from corpus_builder.japanese_audit import (
        audit_japanese_text,
    )

    received: list[str] = []

    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ) -> tuple[FakeMorpheme, ...]:
            received.append(text)

            return (
                FakeMorpheme(
                    surface="今日",
                    reading="キョウ",
                ),
            )

    result = audit_japanese_text(
        (
            "\ufeff"
            "今日は"
            "\u200b"
            "晴れ"
            "\ufe0e"
            "。"
            "\ufe0f"
        ),
        tokenizer=FakeTokenizer(),
        romanizer=lambda text: text,
    )

    assert received == [
        "今日は晴れ。",
    ]

    assert result.total_morphemes == 1
    assert result.successful_morphemes == 1
    assert result.failed_morphemes == 0
    assert result.issues == ()

def test_audit_japanese_text_normalizes_fullwidth_ascii_before_tokenizing() -> None:
    from corpus_builder.japanese_audit import (
        audit_japanese_text,
    )

    received: list[str] = []

    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ) -> tuple[FakeMorpheme, ...]:
            received.append(text)

            return (
                FakeMorpheme(
                    surface="TEST",
                    reading="TEST",
                ),
            )

    result = audit_japanese_text(
        "ＡＺａｚ０９",
        tokenizer=FakeTokenizer(),
        romanizer=lambda text: text,
    )

    assert received == [
        "AZaz09",
    ]

    assert result.total_morphemes == 1
    assert result.successful_morphemes == 1
    assert result.failed_morphemes == 0
    assert result.issues == ()


def test_merge_japanese_audit_results_aggregates_counts_and_issues() -> None:
    from corpus_builder.japanese_audit import (
        JapaneseAuditIssue,
        JapaneseAuditResult,
        merge_japanese_audit_results,
    )

    first = JapaneseAuditResult(
        total_morphemes=3,
        successful_morphemes=2,
        failed_morphemes=1,
        issues=(
            JapaneseAuditIssue(
                surface="未知",
                reading="ㇰ",
                part_of_speech="名詞",
                context="今日は未知。",
                error="Unsupported katakana: ㇰ",
                count=1,
            ),
        ),
    )

    second = JapaneseAuditResult(
        total_morphemes=4,
        successful_morphemes=2,
        failed_morphemes=2,
        issues=(
            JapaneseAuditIssue(
                surface="未知",
                reading="ㇰ",
                part_of_speech="名詞",
                context="未知の語です。",
                error="Unsupported katakana: ㇰ",
                count=2,
            ),
        ),
    )

    result = merge_japanese_audit_results(
        (
            first,
            second,
        )
    )

    assert result.total_morphemes == 7
    assert result.successful_morphemes == 4
    assert result.failed_morphemes == 3

    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.surface == "未知"
    assert issue.reading == "ㇰ"
    assert issue.part_of_speech == "名詞"
    assert issue.error == "Unsupported katakana: ㇰ"
    assert issue.count == 3

    # 最初に遭遇した文脈を保持する。
    assert issue.context == "今日は未知。"


def test_merge_japanese_audit_results_accepts_empty_input() -> None:
    from corpus_builder.japanese_audit import (
        merge_japanese_audit_results,
    )

    result = merge_japanese_audit_results(
        ()
    )

    assert result.total_morphemes == 0
    assert result.successful_morphemes == 0
    assert result.failed_morphemes == 0
    assert result.issues == ()


def test_audit_japanese_texts_merges_multiple_texts() -> None:
    from corpus_builder.japanese_audit import (
        audit_japanese_texts,
    )

    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ) -> tuple[FakeMorpheme, ...]:
            if text == "今日は未知。":
                return (
                    FakeMorpheme(
                        surface="今日",
                        reading="キョウ",
                    ),
                    FakeMorpheme(
                        surface="未知",
                        reading="ㇰ",
                    ),
                )

            if text == "未知の語。":
                return (
                    FakeMorpheme(
                        surface="未知",
                        reading="ㇰ",
                    ),
                    FakeMorpheme(
                        surface="語",
                        reading="ゴ",
                    ),
                )

            raise AssertionError(
                f"unexpected text: {text}"
            )

    def fake_romanizer(text: str) -> str:
        if text == "ㇰ":
            raise ValueError(
                "Unsupported katakana: ㇰ"
            )

        return text

    result = audit_japanese_texts(
        (
            "今日は未知。",
            "未知の語。",
        ),
        tokenizer=FakeTokenizer(),
        romanizer=fake_romanizer,
    )

    assert result.total_morphemes == 4
    assert result.successful_morphemes == 2
    assert result.failed_morphemes == 2

    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.surface == "未知"
    assert issue.reading == "ㇰ"
    assert issue.count == 2
    assert issue.context == "今日は未知。"


def test_audit_japanese_texts_skips_blank_texts() -> None:
    from corpus_builder.japanese_audit import (
        audit_japanese_texts,
    )

    tokenized_texts: list[str] = []

    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ) -> tuple[FakeMorpheme, ...]:
            tokenized_texts.append(text)

            return (
                FakeMorpheme(
                    surface="今日",
                    reading="キョウ",
                ),
            )

    def fake_romanizer(text: str) -> str:
        return text

    result = audit_japanese_texts(
        (
            "",
            "   ",
            "\t",
            "\n",
            "今日は晴れ。",
        ),
        tokenizer=FakeTokenizer(),
        romanizer=fake_romanizer,
    )

    assert tokenized_texts == [
        "今日は晴れ。",
    ]

    assert result.total_morphemes == 1
    assert result.successful_morphemes == 1
    assert result.failed_morphemes == 0
    assert result.issues == ()


def test_audit_japanese_morphemes_joins_trailing_small_tsu_with_next_reading() -> None:
    morphemes = (
        FakeMorpheme(
            surface="なっ",
            reading="ナッ",
            part_of_speech="動詞",
        ),
        FakeMorpheme(
            surface="た",
            reading="タ",
            part_of_speech="助動詞",
        ),
    )

    received: list[str] = []

    def fake_romanizer(
        text: str,
    ) -> str:
        received.append(
            text
        )

        if text.endswith("ッ"):
            raise ValueError(
                "Small tsu must be followed by katakana"
            )

        return text

    result = audit_japanese_morphemes(
        morphemes,
        romanizer=fake_romanizer,
        context="なった",
    )

    assert received == [
        "ナッタ",
    ]

    assert result.total_morphemes == 2
    assert result.successful_morphemes == 2
    assert result.failed_morphemes == 0
    assert result.issues == ()


def test_audit_japanese_morphemes_uses_reading_for_empty_surface() -> None:
    received: list[str] = []

    morphemes = (
        FakeMorpheme(
            surface="",
            reading="テスト",
            part_of_speech="名詞",
        ),
    )

    def fake_romanizer(text: str) -> str:
        received.append(text)
        return text

    result = audit_japanese_morphemes(
        morphemes,
        romanizer=fake_romanizer,
        context="テスト",
    )

    assert received == ["テスト"]
    assert result.total_morphemes == 1
    assert result.successful_morphemes == 1
    assert result.failed_morphemes == 0
    assert result.issues == ()


def test_split_sudachi_text_chunks_keeps_chunks_within_byte_limit() -> None:
    from corpus_builder.japanese_audit import (
        split_sudachi_text_chunks,
    )

    text = "\n".join(
        (
            "あ" * 100,
            "い" * 100,
            "う" * 100,
        )
    )

    chunks = split_sudachi_text_chunks(
        text,
        max_bytes=700,
    )

    assert "".join(chunks) == text

    assert all(
        len(
            chunk.encode("utf-8")
        )
        <= 700
        for chunk in chunks
    )

    assert len(chunks) == 2


def test_split_sudachi_text_chunks_rejects_single_oversized_line() -> None:
    from corpus_builder.japanese_audit import (
        split_sudachi_text_chunks,
    )

    text = "あ" * 100

    try:
        split_sudachi_text_chunks(
            text,
            max_bytes=100,
        )
    except ValueError as error:
        assert str(error) == (
            "Single line exceeds Sudachi byte limit"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_audit_japanese_morphemes_ignores_foreign_symbol_morpheme() -> None:
    morphemes = (
        FakeMorpheme(
            surface="(*´ω｀*)",
            reading="(*´ω｀*)",
            part_of_speech="補助記号",
        ),
    )

    result = audit_japanese_morphemes(
        morphemes,
        romanizer=lambda text: (_ for _ in ()).throw(
            ValueError("must not be called")
        ),
        context="顔文字",
    )

    assert result.total_morphemes == 0
    assert result.successful_morphemes == 0
    assert result.failed_morphemes == 0
    assert result.issues == ()


def test_audit_japanese_morphemes_keeps_japanese_small_kana_candidate() -> None:
    morphemes = (
        FakeMorpheme(
            surface="あぁ",
            reading="アァ",
            part_of_speech="感動詞",
        ),
    )

    result = audit_japanese_morphemes(
        morphemes,
        romanizer=lambda text: (
            (_ for _ in ()).throw(
                ValueError("Unsupported katakana: ァ")
            )
            if "ァ" in text
            else text
        ),
        context="あぁ",
    )

    assert result.total_morphemes == 1
    assert result.successful_morphemes == 0
    assert result.failed_morphemes == 1
    assert len(result.issues) == 1


def test_audit_japanese_morphemes_ignores_standalone_halfwidth_semivoiced_mark() -> None:
    morphemes = (
        FakeMorpheme(
            surface="ﾟ",
            reading="゚",
            part_of_speech="名詞",
        ),
    )

    result = audit_japanese_morphemes(
        morphemes,
        romanizer=lambda text: (
            (_ for _ in ()).throw(
                ValueError("must not be called")
            )
        ),
        context="(ﾟ∀ﾟ)",
    )

    assert result.total_morphemes == 0
    assert result.successful_morphemes == 0
    assert result.failed_morphemes == 0
    assert result.issues == ()


def test_audit_japanese_morphemes_ignores_symbol_readings() -> None:
    for symbol in (
        "×",
        "△",
        "□",
        "㈱",
    ):
        morphemes = (
            FakeMorpheme(
                surface=symbol,
                reading=symbol,
                part_of_speech="補助記号",
            ),
        )

        result = audit_japanese_morphemes(
            morphemes,
            romanizer=lambda text: (
                (_ for _ in ()).throw(
                    ValueError("must not be called")
                )
            ),
            context=symbol,
        )

        assert result.total_morphemes == 0
        assert result.successful_morphemes == 0
        assert result.failed_morphemes == 0
        assert result.issues == ()


def test_audit_japanese_text_salvages_cjk_oov_after_ideographic_zero() -> None:
    class OovMorpheme(FakeMorpheme):
        def is_oov(
            self,
        ) -> bool:
            return True

    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ):
            if text == "〇魚菜店":
                return (
                    OovMorpheme(
                        surface="〇魚菜店",
                        reading="〇魚菜店",
                        part_of_speech="名詞",
                    ),
                )

            if text == "魚菜店":
                return (
                    FakeMorpheme(
                        surface="魚",
                        reading="サカナ",
                        part_of_speech="名詞",
                    ),
                    FakeMorpheme(
                        surface="菜",
                        reading="ナ",
                        part_of_speech="名詞",
                    ),
                    FakeMorpheme(
                        surface="店",
                        reading="テン",
                        part_of_speech="名詞",
                    ),
                )

            raise AssertionError(
                f"Unexpected tokenize input: {text!r}"
            )

    received: list[str] = []

    def fake_romanizer(
        reading: str,
    ) -> str:
        received.append(reading)

        mapping = {
            "〇": "maru",
            "サカナ": "sakana",
            "ナ": "na",
            "テン": "tenn",
        }

        return mapping[reading]

    result = audit_japanese_text(
        "〇魚菜店",
        tokenizer=FakeTokenizer(),
        romanizer=fake_romanizer,
    )

    assert received == [
        "〇",
        "サカナ",
        "ナ",
        "テン",
    ]
    assert result.failed_morphemes == 0
    assert result.issues == ()


def test_audit_japanese_morphemes_skips_ignored_combining_readings() -> None:
    received: list[str] = []

    def fake_romanizer(
        reading: str,
    ) -> str:
        received.append(reading)
        return "ignored"

    result = audit_japanese_morphemes(
        (
            FakeMorpheme(
                surface="ﾟﾟ",
                reading="゚゚",
                part_of_speech="名詞",
            ),
            FakeMorpheme(
                surface="",
                reading=" ̆",
                part_of_speech="補助記号",
            ),
        ),
        romanizer=fake_romanizer,
        context="test",
    )

    assert received == []
    assert result.total_morphemes == 0
    assert result.successful_morphemes == 0
    assert result.failed_morphemes == 0
    assert result.issues == ()


def test_audit_japanese_morphemes_audits_ideographic_zero() -> None:
    received: list[str] = []

    morphemes = (
        FakeMorpheme(
            surface="〇",
            reading="〇",
            part_of_speech="補助記号",
        ),
    )

    def fake_romanizer(text: str) -> str:
        received.append(text)

        if text == "〇":
            return "maru"

        raise ValueError(
            f"Unexpected reading: {text}"
        )

    result = audit_japanese_morphemes(
        morphemes,
        romanizer=fake_romanizer,
        context="〇",
    )

    assert received == ["〇"]
    assert result.total_morphemes == 1
    assert result.successful_morphemes == 1
    assert result.failed_morphemes == 0
    assert result.issues == ()


def test_audit_japanese_morphemes_keeps_small_kana_and_tsu() -> None:
    for surface, reading in (
        ("ぁ", "ァ"),
        ("ぃ", "ィ"),
        ("ぇ", "ェ"),
        ("っ", "ッ"),
    ):
        morphemes = (
            FakeMorpheme(
                surface=surface,
                reading=reading,
                part_of_speech="補助記号",
            ),
        )

        result = audit_japanese_morphemes(
            morphemes,
            romanizer=lambda text: (
                (_ for _ in ()).throw(
                    ValueError(
                        f"Unsupported katakana: {text}"
                    )
                )
            ),
            context=surface,
        )

        assert result.total_morphemes == 1
        assert result.successful_morphemes == 0
        assert result.failed_morphemes == 1
        assert len(result.issues) == 1


def test_audit_japanese_text_chunks_before_whitespace_normalization() -> None:
    from corpus_builder.japanese_audit import (
        audit_japanese_text,
    )

    class RecordingTokenizer:
        def __init__(self) -> None:
            self.inputs: list[str] = []

        def tokenize(
            self,
            text: str,
        ) -> tuple[FakeMorpheme, ...]:
            self.inputs.append(text)
            return ()

    tokenizer = RecordingTokenizer()

    line = "あ" * 10_000

    text = f"{line}\n{line}"

    result = audit_japanese_text(
        text,
        tokenizer=tokenizer,
        romanizer=lambda value: value,
    )

    assert result.total_morphemes == 0
    assert result.successful_morphemes == 0
    assert result.failed_morphemes == 0

    assert len(tokenizer.inputs) == 2

    assert all(
        "\n" not in value
        for value in tokenizer.inputs
    )
