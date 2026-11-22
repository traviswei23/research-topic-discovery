"""Regression tests for topic selection, with deliberately fictional records."""
import sys
import json
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from topic_run import check, digest, render


class TopicRunTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        (self.root / "trace.md").write_text("Synthetic record", encoding="utf-8")
        paper = dict(id="P1", citation="Fictional paper", source="provided locally", level="original",
                     locator="Figure A", observation="Known mechanism", note="trace.md", query_id="Q1")
        base = dict(id="I1", question="Does T separate the mechanisms?", lens="diagnostic",
                    mechanism="source drift", prediction="opposite sign", status="selected",
                    reason="Can be distinguished", prior="P1", comparison="Different observable",
                    baseline="hold T fixed", rival="sensor drift", observable="difference",
                    falsifier="indistinguishable readings", resources="CPU", value="identify failure",
                    next="test the limiting case",
                    pilot=dict(status="unavailable", reason="missing input", alternative="derive bound"))
        other = dict(id="I2", question="Can a new run answer it?", lens="control", mechanism="scale",
                     prediction="threshold", status="parked", reason="needs a verified noise model")
        self.data = dict(version=1, direction="Fictional system", constraints="simulation", scope="online",
                         target=1, ideas=[base, other], papers=[paper], selected=["I1"],
                         queries=[dict(id=q, source=s, operation="search", status="ok", screened=1,
                                       date="2025-10-02", query="public words", trace="trace.md")
                                  for q, s in (("Q1", "Library A"), ("Q2", "Library B"))],
                         review=dict(mode="self", attack="common cause", answer="need control", trace="trace.md"),
                         rounds=[dict(trigger="correlated errors", evidence="bound", decision="deepen",
                                      change="added control")], decision="shortlist", stop="identified test",
                         next_step="implement control")

    def test_shortlist_renders_all_decisions(self):
        cards = check(self.data, self.root)
        report = render(self.data, cards)
        for value in ("I1", "I2", "Figure A", "missing input", "common cause"):
            self.assertIn(value, report)

    def test_lookup_is_not_discovery(self):
        self.data["queries"][1]["operation"] = "lookup"
        with self.assertRaisesRegex(ValueError, "两个"):
            check(self.data, self.root)

    def test_raw_export_controls_reported_screening(self):
        original = {"action": "search", "parameters": {"public_query": "public words"},
                    "providers": {"library a": {"status": "ok", "candidates": ["one"]}}}
        (self.root / "request.json").write_text(json.dumps(original), encoding="utf-8")
        self.data["queries"][0].update(trace="request.json", screened=2)
        with self.assertRaisesRegex(ValueError, "筛读数超过"):
            check(self.data, self.root)

    def test_failed_or_unread_source_cannot_raise_coverage(self):
        self.data["queries"][1].update(screened=0)
        with self.assertRaises(ValueError):
            check(self.data, self.root)

    def test_selected_count_cannot_ignore_user_target(self):
        self.data["target"] = 5
        with self.assertRaisesRegex(ValueError, "少于"):
            check(self.data, self.root)
        self.data["decision"] = "partial"
        check(self.data, self.root)

    def test_covered_requires_original_not_abstract(self):
        self.data["ideas"][1].update(status="covered", prior="P2", comparison="same method")
        paper = dict(self.data["papers"][0], id="P2", level="abstract")
        self.data["papers"].append(paper)
        with self.assertRaisesRegex(ValueError, "原文"):
            check(self.data, self.root)

    def test_merged_cannot_point_to_self(self):
        self.data["ideas"][1].update(status="merged", merged_into="I2")
        with self.assertRaisesRegex(ValueError, "合并"):
            check(self.data, self.root)

    def test_duplicate_predictions_do_not_create_independent_options(self):
        self.data["ideas"][1].update(mechanism="source drift", prediction="opposite sign")
        with self.assertRaisesRegex(ValueError, "完全相同"):
            check(self.data, self.root)

    def test_pilot_change_invalidates_result(self):
        for name in ("spec.md", "result.md"):
            (self.root / name).write_text(name, encoding="utf-8")
        pilot = dict(status="run", protocol="spec.md", result="result.md",
                     protocol_sha256=digest(self.root / "spec.md"), result_sha256=digest(self.root / "result.md"),
                     signal="informative_null", observation="null", implication="rank lower", limits="toy")
        self.data["ideas"][0]["pilot"] = pilot
        check(self.data, self.root)
        (self.root / "result.md").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "结果文件已变"):
            check(self.data, self.root)

    def test_rejects_absolute_receipt(self):
        self.data["review"]["trace"] = str(self.root / "trace.md")
        with self.assertRaisesRegex(ValueError, "相对路径"):
            check(self.data, self.root)

    def test_physics_study_cannot_omit_model(self):
        self.data["study_type"] = "physics"
        with self.assertRaisesRegex(ValueError, "物理最小模型"):
            check(self.data, self.root)

    def test_pairwise_result_must_be_from_actual_pair(self):
        self.data["pairs"] = [dict(left="I1", right="I2", choice="I3", basis="cost", reversal="new measurement")]
        with self.assertRaisesRegex(ValueError, "本场候选"):
            check(self.data, self.root)


if __name__ == "__main__":
    unittest.main()
