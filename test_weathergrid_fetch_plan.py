import json
import unittest
from pathlib import Path

from weathergrid_coverage import CoverageError
from weathergrid_fetch_plan import (
    build_scoped_fetch_plan,
    nomads_bbox_for_plan,
)


class WeatherGridFetchPlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parent
        cls.catalog = json.loads(
            (root / "runtime_catalog_v004_r4_2.json").read_text(encoding="utf-8")
        )
        cls.registry = json.loads(
            (root / "weathergrid_coverage_registry_r4_2.json").read_text(encoding="utf-8")
        )

    def test_complete_opportunity_produces_nomads_fetch_bbox(self):
        plan = build_scoped_fetch_plan(
            self.catalog,
            self.registry,
            opportunity_id="tw-036-P03",
        )
        self.assertTrue(plan.complete, plan.to_dict())
        bbox = nomads_bbox_for_plan(plan)

        self.assertLess(bbox["leftlon"], 121.62717)
        self.assertGreater(bbox["rightlon"], 121.62717)
        self.assertLess(bbox["bottomlat"], 24.031426)
        self.assertGreater(bbox["toplat"], 24.15)

        # Fetch bbox includes viewport + one GFS-cell interpolation halo.
        self.assertLess(plan.fetch_bbox["west"], plan.viewport_bbox["west"])
        self.assertGreater(plan.fetch_bbox["east"], plan.viewport_bbox["east"])
        self.assertLess(plan.fetch_bbox["south"], plan.viewport_bbox["south"])
        self.assertGreater(plan.fetch_bbox["north"], plan.viewport_bbox["north"])

    def test_needs_research_opportunity_refuses_scoped_fetch(self):
        plan = build_scoped_fetch_plan(
            self.catalog,
            self.registry,
            opportunity_id="tw-082-P01",
        )
        self.assertFalse(plan.complete)
        self.assertIsNone(plan.fetch_bbox)
        self.assertTrue(
            any("scoped provider fetch refused" in e for e in plan.errors),
            plan.to_dict(),
        )
        with self.assertRaises(CoverageError):
            nomads_bbox_for_plan(plan)

    def test_unmigrated_opportunity_refuses_scoped_fetch(self):
        plan = build_scoped_fetch_plan(
            self.catalog,
            self.registry,
            opportunity_id="tw-036-P01",
        )
        self.assertFalse(plan.complete)
        self.assertTrue(
            any("has not migrated" in e for e in plan.errors),
            plan.to_dict(),
        )

    def test_place_scope_requires_all_active_topics(self):
        plan = build_scoped_fetch_plan(
            self.catalog,
            self.registry,
            spot_id="tw-036",
        )
        self.assertFalse(plan.complete)
        self.assertIsNone(plan.fetch_bbox)
        self.assertTrue(
            any("not all active Opportunities" in e for e in plan.errors),
            plan.to_dict(),
        )

    def test_exactly_one_scope_is_required(self):
        with self.assertRaises(CoverageError):
            build_scoped_fetch_plan(self.catalog, self.registry)
        with self.assertRaises(CoverageError):
            build_scoped_fetch_plan(
                self.catalog,
                self.registry,
                opportunity_id="tw-036-P03",
                spot_id="tw-036",
            )


if __name__ == "__main__":
    unittest.main()
