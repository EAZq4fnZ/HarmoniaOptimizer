from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from .sudachi_reader import make_default_sudachi_tokenizer


@dataclass(frozen=True, slots=True)
class JapaneseReader:
    tokenizer: Callable[[str], Iterable[str]]

    def __call__(
        self,
        text: str,
    ) -> str:
        return "".join(
            self.tokenizer(text)
        )



def make_default_japanese_reader() -> JapaneseReader:
    return JapaneseReader(
        tokenizer=make_default_sudachi_tokenizer()
    )
