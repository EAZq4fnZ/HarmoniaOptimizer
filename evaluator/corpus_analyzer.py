# evaluator/corpus_analyzer.py
from models.corpus import Corpus

from .transition_recorder import TransitionRecorder
from .transition_statistics import TransitionStatistics


class CorpusAnalyzer:
    """Analyze a corpus and produce transition statistics."""

    def __init__(self) -> None:
        self._recorder = TransitionRecorder()
        self._statistics = TransitionStatistics()

    def analyze(self, corpus: Corpus) -> TransitionStatistics:
        """Analyze all corpus entries."""
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