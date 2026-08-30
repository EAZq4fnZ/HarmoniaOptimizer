# evaluator/corpus_analyzer.py

from models.corpus import Corpus

from .transition_recorder import TransitionRecorder
from .transition_statistics import TransitionStatistics
from .trigram_recorder import TrigramRecorder
from .trigram_statistics import TrigramStatistics


class CorpusAnalyzer:
    """
    Analyze a corpus and produce n-gram statistics.

    The existing analyze() method continues to return bigram
    transition statistics for backward compatibility.

    Trigram statistics are available through analyze_trigrams().
    """

    def __init__(self) -> None:
        self._recorder = TransitionRecorder()
        self._statistics = TransitionStatistics()

        self._trigram_recorder = TrigramRecorder()

    def analyze(
        self,
        corpus: Corpus,
    ) -> TransitionStatistics:
        """
        Analyze all corpus entries and return transition statistics.
        """

        self._recorder.clear()
        self._statistics.clear()

        for entry in corpus.entries:
            self._recorder.clear()
            self._recorder.record_entry(entry)

            self._statistics.add(
                self._recorder.transitions(),
                weight=entry.weight,
            )

        return self._statistics

    def analyze_trigrams(
        self,
        corpus: Corpus,
    ) -> TrigramStatistics:
        """
        Analyze all corpus entries and return trigram statistics.

        Each corpus entry's weight is applied to every recorded
        trigram occurrence.
        """

        statistics = TrigramStatistics()

        for entry in corpus.entries:
            self._trigram_recorder.record(
                entry.text,
                statistics,
                weight=entry.weight,
            )

        return statistics
