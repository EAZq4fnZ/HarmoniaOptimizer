# evaluator/character_analyzer.py

from collections import Counter

from models.corpus import Corpus

from .character_statistics import CharacterStatistics


class CharacterAnalyzer:
    """
    Analyze character frequencies in a corpus.

    Character counts are case-insensitive.
    CorpusEntry weights are applied to weighted statistics.
    """

    def analyze(
        self,
        corpus: Corpus,
    ) -> CharacterStatistics:
        """
        Analyze all entries in a corpus.

        Returns
        -------
        CharacterStatistics
            Raw and weighted character frequencies.
        """

        statistics = CharacterStatistics()

        for entry in corpus.entries:
            counts = Counter(entry.text.lower())

            statistics.add(
                dict(counts),
                weight=entry.weight,
            )

        return statistics