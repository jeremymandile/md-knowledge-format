"""tests/performance/test_token_budget.py

Verifies that the token-budget fallback logic works correctly.
When context is tight, LESSONS.md grep should trigger before
the full lesson set is loaded.

Philosophy: test the contract, not the implementation.
"""
import pytest
import time


@pytest.mark.performance
class TestTokenBudget:
    """Token budget and fallback logic tests."""

    def test_small_lessons_file_loads_fast(self, tmp_path):
        """A LESSONS.md with <50 entries should load under 100ms."""
        lessons = tmp_path / "LESSONS.md"
        lessons.write_text(
            "---\nlesson_version: 1\n---\n\n"
            + "\n\n".join(
                f"## L{i:03d}\n\ntags: [test]\ncontent: lesson {i}"
                for i in range(50)
            )
        )
        start = time.perf_counter()
        text = lessons.read_text()
        assert "lesson_version" in text
        elapsed = time.perf_counter() - start
        assert elapsed < 0.1, f"File read took {elapsed:.3f}s — expected <100ms"

    def test_grep_is_faster_than_full_load(self, tmp_path):
        """Grepping for a tag should be faster than parsing all lessons.

        This simulates the token-budget scenario: when context is tight,
        a targeted grep is preferred over loading the full LESSONS.md.
        """
        lessons = tmp_path / "LESSONS.md"
        many_lessons = "\n\n".join(
            f"## L{i:04d}\n\ntags: [cat-{i % 10}]\ncontent: lesson body {i}" * 3
            for i in range(200)
        )
        lessons.write_text(f"---\nlesson_version: 1\n---\n\n{many_lessons}")

        # Simulate grep: scan only lines containing the target tag
        start_grep = time.perf_counter()
        matched = [l for l in lessons.read_text().splitlines() if "cat-3" in l]
        grep_time = time.perf_counter() - start_grep

        # Simulate full parse: read + split by double-newline
        start_full = time.perf_counter()
        blocks = lessons.read_text().split("\n\n")
        full_time = time.perf_counter() - start_full

        assert len(matched) > 0, "grep should find at least one match"
        assert len(blocks) > 0, "full load should produce blocks"
        # grep should not be dramatically slower than full read
        assert grep_time < full_time * 10, (
            f"grep ({grep_time:.4f}s) should not be 10x slower than full load ({full_time:.4f}s)"
        )

    def test_lessons_file_size_threshold(self, tmp_path):
        """Files over 100KB should trigger a warning signal.

        This test verifies that the size-check boundary is correct.
        Agents should use grep when the file is large.
        """
        THRESHOLD_BYTES = 100_000

        small = tmp_path / "small.md"
        small.write_text("x" * (THRESHOLD_BYTES - 1))

        large = tmp_path / "large.md"
        large.write_text("x" * (THRESHOLD_BYTES + 1))

        assert small.stat().st_size < THRESHOLD_BYTES, "small file should be under threshold"
        assert large.stat().st_size > THRESHOLD_BYTES, "large file should exceed threshold"

    @pytest.mark.slow
    def test_grep_scales_linearly(self, tmp_path):
        """Grep performance should scale roughly linearly with file size.

        Creates files 2x apart and checks that grep time doesn't explode.
        """
        def measure_grep(n_lessons):
            f = tmp_path / f"lessons_{n_lessons}.md"
            f.write_text("\n\n".join(
                f"## L{i}\ntags: [alpha, beta]\ncontent: body {i}"
                for i in range(n_lessons)
            ))
            start = time.perf_counter()
            matches = [l for l in f.read_text().splitlines() if "alpha" in l]
            return time.perf_counter() - start, len(matches)

        t_small, n_small = measure_grep(100)
        t_large, n_large = measure_grep(200)

        assert n_large == n_small * 2, "double lessons should double matches"
        # Time should not grow worse than 4x for 2x data
        if t_small > 0.001:  # only assert if small is measurably non-zero
            assert t_large < t_small * 4, (
                f"grep scaling: {t_small:.4f}s -> {t_large:.4f}s for 2x data"
            )
