# reporting/optimization_reporter.py

from __future__ import annotations

from models.optimization_result import OptimizationResult


class OptimizationReporter:
    """
    Format optimization results for human-readable output.
    """

    def format(
        self,
        result: OptimizationResult,
    ) -> str:
        """
        Return a human-readable optimization report.
        """

        lines = [
            "Optimization Result",
            "===================",
            "",
            f"Initial score: {self._format_score(result.initial_score)}",
            f"Final score:   {self._format_score(result.final_score)}",
            f"Improvement:   {self._format_score(result.improvement)}",
            f"Iterations:    {result.iteration_count}",
        ]

        if result.steps:
            lines.extend(
                [
                    "",
                    "Accepted moves",
                    "--------------",
                ]
            )

            for step in result.steps:
                lines.append(
                    f"{step.iteration}. "
                    f"{step.move.first_letter} <-> "
                    f"{step.move.second_letter}    "
                    f"score: {self._format_score(step.score)}"
                )
        else:
            lines.extend(
                [
                    "",
                    "Accepted moves",
                    "--------------",
                    "None",
                ]
            )

        return "\n".join(lines)

    @staticmethod
    def _format_score(
        value: float | None,
    ) -> str:
        if value is None:
            return "N/A"

        return f"{value:.6f}"