from pathlib import Path

from tools.audit_japanese_corpus import (
    audit_file,
)


def test_audit_file_reads_nonblank_lines(
    tmp_path: Path,
) -> None:
    source = tmp_path / "sample.txt"

    source.write_text(
        "今日は晴れ。\n"
        "\n"
        "未知の語です。\n",
        encoding="utf-8",
    )

    seen_texts: list[str] = []

    def fake_auditor(
        texts: object,
    ) -> str:
        seen_texts.extend(texts)
        return "result"

    result = audit_file(
        source,
        auditor=fake_auditor,
    )

    assert seen_texts == [
        "今日は晴れ。\n",
        "\n",
        "未知の語です。\n",
    ]

    assert result == "result"


def test_audit_default_file_builds_default_auditor(
    tmp_path: Path,
) -> None:
    from tools.audit_japanese_corpus import (
        audit_default_file,
    )

    source = tmp_path / "sample.txt"

    source.write_text(
        "今日は晴れ。\n",
        encoding="utf-8",
    )

    seen_texts: list[str] = []

    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ) -> tuple[object, ...]:
            raise AssertionError(
                "tokenize should not be called directly here"
            )

    fake_tokenizer = FakeTokenizer()

    def fake_tokenizer_factory() -> FakeTokenizer:
        return fake_tokenizer

    def fake_romanizer(text: str) -> str:
        return text

    def fake_audit_texts(
        texts: object,
        *,
        tokenizer: object,
        romanizer: object,
    ) -> str:
        seen_texts.extend(texts)

        assert tokenizer is fake_tokenizer
        assert romanizer is fake_romanizer

        return "result"

    result = audit_default_file(
        source,
        tokenizer_factory=fake_tokenizer_factory,
        romanizer=fake_romanizer,
        audit_texts=fake_audit_texts,
    )

    assert seen_texts == [
        "今日は晴れ。\n",
    ]

    assert result == "result"


def test_audit_default_file_with_real_pipeline(
    tmp_path: Path,
) -> None:
    from tools.audit_japanese_corpus import (
        audit_default_file,
    )

    source = tmp_path / "sample.txt"

    source.write_text(
        "今日は晴れ。\n"
        "本を読む。\n",
        encoding="utf-8",
    )

    result = audit_default_file(
        source
    )

    assert result.total_morphemes > 0
    assert result.successful_morphemes > 0
    assert result.failed_morphemes == 0
    assert result.issues == ()


def test_main_prints_audit_summary(
    tmp_path: Path,
    capsys: object,
) -> None:
    from tools.audit_japanese_corpus import (
        main,
    )

    source = tmp_path / "sample.txt"

    source.write_text(
        "今日は晴れ。\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            str(source),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "total_morphemes:" in captured.out
    assert "successful_morphemes:" in captured.out
    assert "failed_morphemes:" in captured.out
    assert "issues:" in captured.out


def test_main_prints_issue_details(
    tmp_path: Path,
    capsys: object,
    monkeypatch: object,
) -> None:
    import tools.audit_japanese_corpus as tool
    from corpus_builder.japanese_audit import (
        JapaneseAuditIssue,
        JapaneseAuditResult,
    )

    source = tmp_path / "sample.txt"

    source.write_text(
        "未知の語です。\n",
        encoding="utf-8",
    )

    result = JapaneseAuditResult(
        total_morphemes=3,
        successful_morphemes=2,
        failed_morphemes=1,
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

    monkeypatch.setattr(
        tool,
        "audit_default_file",
        lambda path: result,
    )

    exit_code = tool.main(
        [
            str(source),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "surface: 未知" in captured.out
    assert "reading: ㇰ" in captured.out
    assert "part_of_speech: 名詞" in captured.out
    assert "count: 2" in captured.out
    assert "context: 未知の語です。" in captured.out
    assert "error: Unsupported katakana: ㇰ" in captured.out


def test_main_prints_issues_by_count_descending(
    tmp_path: Path,
    capsys: object,
    monkeypatch: object,
) -> None:
    import tools.audit_japanese_corpus as tool
    from corpus_builder.japanese_audit import (
        JapaneseAuditIssue,
        JapaneseAuditResult,
    )

    source = tmp_path / "sample.txt"

    source.write_text(
        "sample\n",
        encoding="utf-8",
    )

    result = JapaneseAuditResult(
        total_morphemes=7,
        successful_morphemes=2,
        failed_morphemes=5,
        issues=(
            JapaneseAuditIssue(
                surface="少数",
                reading="ㇰ",
                part_of_speech="名詞",
                context="少数",
                error="error-a",
                count=1,
            ),
            JapaneseAuditIssue(
                surface="多数",
                reading="ㇱ",
                part_of_speech="名詞",
                context="多数",
                error="error-b",
                count=4,
            ),
        ),
    )

    monkeypatch.setattr(
        tool,
        "audit_default_file",
        lambda path: result,
    )

    exit_code = tool.main(
        [
            str(source),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out.index(
        "surface: 多数"
    ) < captured.out.index(
        "surface: 少数"
    )
