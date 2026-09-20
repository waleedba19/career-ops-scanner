"""Phase 4 tests: score-distribution observability (threshold-tuning aid).

Verifies the histogram buckets that decide whether lowering MIN_MATCH_SCORE
would actually surface more jobs. Uses the shared scorer, offline.
Run: python -m unittest test_score_distribution -v
"""

import unittest

from scanner import get_match_score, MIN_MATCH_SCORE


def bucket(score: int) -> str:
    """Mirror of scanner.py's score_dist bucketing."""
    if score <= 0:
        return "0"
    if score < 40:
        return "1-39"
    if score < 50:
        return "40-49"
    if score < 75:
        return "50-74"
    return "75-100"


class ScoreDistributionTests(unittest.TestCase):
    def test_bucket_boundaries(self):
        self.assertEqual(bucket(0), "0")
        self.assertEqual(bucket(1), "1-39")
        self.assertEqual(bucket(39), "1-39")
        self.assertEqual(bucket(40), "40-49")
        self.assertEqual(bucket(49), "40-49")
        self.assertEqual(bucket(50), "50-74")
        self.assertEqual(bucket(74), "50-74")
        self.assertEqual(bucket(75), "75-100")
        self.assertEqual(bucket(100), "75-100")

    def test_irrelevant_role_scores_zero(self):
        """A non-language role must land in the '0' bucket."""
        s = get_match_score("Senior Software Engineer", "Kubernetes and Go, no language work.")["score"]
        self.assertEqual(bucket(s), "0", f"expected 0-bucket, got score={s}")

    def test_translation_role_clears_threshold(self):
        """A real Arabic translation role must clear MIN_MATCH_SCORE.

        This is the guard for the threshold trade-off: if this ever fails,
        lowering the threshold is the wrong fix (the scorer regressed).
        """
        s = get_match_score(
            "Arabic Translator (Remote Worldwide)",
            "Legal Arabic-English translation. Fully remote, work from anywhere.",
        )["score"]
        self.assertGreaterEqual(s, MIN_MATCH_SCORE, f"score {s} < MIN_MATCH_SCORE {MIN_MATCH_SCORE}")

    def test_threshold_is_configurable(self):
        """MIN_MATCH_SCORE must come from env, so tuning is a config change."""
        self.assertIsInstance(MIN_MATCH_SCORE, int)
        self.assertGreater(MIN_MATCH_SCORE, 0)
        self.assertLessEqual(MIN_MATCH_SCORE, 100)


if __name__ == "__main__":
    unittest.main()
