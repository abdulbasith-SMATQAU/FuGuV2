import unittest

from fugu_logic import filter_programs, load_json, score_programs, validate_records


class TestFuGuLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.programs = load_json("programs.json")

    def test_dataset_has_unique_ids_and_required_fields(self):
        self.assertEqual(validate_records(self.programs), [])

    def test_search_finds_informatika(self):
        results = filter_programs(self.programs, query="informatika")
        self.assertGreaterEqual(len(results), 3)
        self.assertTrue(all("informatika" in (p["program_name"] + " " + p["university"] + " " + p["summary"] + " " + " ".join(p["interests"])).casefold() for p in results))

    def test_filter_by_province(self):
        results = filter_programs(self.programs, province="DI Yogyakarta")
        self.assertGreater(len(results), 0)
        self.assertTrue(all(p["province"] == "DI Yogyakarta" for p in results))

    def test_filter_by_category(self):
        results = filter_programs(self.programs, categories=["Bisnis"])
        self.assertGreater(len(results), 0)
        self.assertTrue(all(p["category"] == "Bisnis" for p in results))

    def test_recommendation_scores_are_bounded_and_sorted(self):
        ranked = score_programs(
            self.programs,
            interests=["Teknologi & Komputer"],
            skills=["Analitis"],
            preferred_province="Jawa Tengah",
        )
        self.assertEqual(len(ranked), len(self.programs))
        self.assertTrue(all(0 <= p["score"] <= 100 for p in ranked))
        self.assertEqual([p["score"] for p in ranked], sorted([p["score"] for p in ranked], reverse=True))
        self.assertTrue(any(p["province"] == "Jawa Tengah" for p in ranked[:4]))

    def test_empty_interest_returns_no_recommendations(self):
        self.assertEqual(score_programs(self.programs, interests=[]), [])

    def test_reasons_explain_interest_matches(self):
        ranked = score_programs(self.programs, interests=["Bisnis & Ekonomi"])
        management = next(p for p in ranked if p["program_name"] == "Manajemen" and "UGM" in p["university"])
        self.assertIn("Bisnis & Ekonomi", " ".join(management["reasons"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
