from corpus_builder.japanese_audit import (
    audit_japanese_morphemes,
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
