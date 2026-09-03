from corpus_builder.document_sampler import (
    sample_documents,
)


def test_sample_documents_is_deterministic() -> None:
    documents = (
        "alpha",
        "bravo",
        "charlie",
        "delta",
        "echo",
    )

    first = sample_documents(
        documents,
        sample_size=3,
        seed=20260904,
    )
    second = sample_documents(
        documents,
        sample_size=3,
        seed=20260904,
    )

    assert first == second
    assert len(first) == 3


def test_sample_documents_removes_blank_documents() -> None:
    documents = (
        "alpha",
        "",
        "   ",
        "\n",
        "bravo",
    )

    result = sample_documents(
        documents,
        sample_size=10,
        seed=1,
    )

    assert set(result) == {
        "alpha",
        "bravo",
    }


def test_sample_documents_removes_duplicates() -> None:
    documents = (
        "alpha",
        "bravo",
        "alpha",
        "charlie",
        "bravo",
    )

    result = sample_documents(
        documents,
        sample_size=10,
        seed=1,
    )

    assert len(result) == 3
    assert set(result) == {
        "alpha",
        "bravo",
        "charlie",
    }


def test_sample_documents_limits_sample_size() -> None:
    documents = (
        "alpha",
        "bravo",
        "charlie",
        "delta",
    )

    result = sample_documents(
        documents,
        sample_size=2,
        seed=1,
    )

    assert len(result) == 2


def test_sample_documents_returns_all_when_sample_is_large() -> None:
    documents = (
        "alpha",
        "bravo",
    )

    result = sample_documents(
        documents,
        sample_size=10,
        seed=1,
    )

    assert set(result) == {
        "alpha",
        "bravo",
    }


def test_sample_documents_rejects_zero_sample_size() -> None:
    try:
        sample_documents(
            ("alpha",),
            sample_size=0,
            seed=1,
        )
    except ValueError as error:
        assert str(error) == (
            "sample_size must be greater than 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_sample_documents_rejects_negative_sample_size() -> None:
    try:
        sample_documents(
            ("alpha", "bravo"),
            sample_size=-1,
            seed=1,
        )
    except ValueError as error:
        assert str(error) == (
            "sample_size must be greater than 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_sample_documents_is_independent_of_input_order() -> None:
    first = sample_documents(
        (
            "alpha",
            "bravo",
            "charlie",
            "delta",
            "echo",
        ),
        sample_size=3,
        seed=20260904,
    )

    second = sample_documents(
        (
            "echo",
            "charlie",
            "alpha",
            "delta",
            "bravo",
        ),
        sample_size=3,
        seed=20260904,
    )

    assert first == second
