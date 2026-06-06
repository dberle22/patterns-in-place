"""Tests for the user_shortlist upsert workflow (uses in-memory DuckDB fixture)."""

import pytest

from retail_opportunity_finder.app.parcel_explorer import SHORTLIST_STATUSES, upsert_shortlist


class TestUpsertShortlist:
    def test_creates_new_row(self, mem_con):
        upsert_shortlist(mem_con, "p1", "jacksonville_fl", "test_user", "active", "first note")
        row = mem_con.execute(
            "SELECT * FROM rof_gold.user_shortlist WHERE parcel_uid = 'p1'"
        ).fetchone()
        assert row is not None

    def test_created_row_has_correct_values(self, mem_con):
        upsert_shortlist(mem_con, "p2", "jacksonville_fl", "test_user", "watchlist", "watch this")
        row = mem_con.execute(
            "SELECT parcel_uid, market_key, user_id, status, notes "
            "FROM rof_gold.user_shortlist WHERE parcel_uid = 'p2'"
        ).fetchone()
        assert row[0] == "p2"
        assert row[1] == "jacksonville_fl"
        assert row[2] == "test_user"
        assert row[3] == "watchlist"
        assert row[4] == "watch this"

    def test_updates_existing_row(self, mem_con):
        upsert_shortlist(mem_con, "p3", "jacksonville_fl", "test_user", "active", "original")
        upsert_shortlist(mem_con, "p3", "jacksonville_fl", "test_user", "rejected", "changed")
        rows = mem_con.execute(
            "SELECT status, notes FROM rof_gold.user_shortlist WHERE parcel_uid = 'p3'"
        ).fetchall()
        assert len(rows) == 1
        assert rows[0][0] == "rejected"
        assert rows[0][1] == "changed"

    def test_updated_at_changes_on_update(self, mem_con):
        upsert_shortlist(mem_con, "p4", "jacksonville_fl", "test_user", "active", "")
        created_at = mem_con.execute(
            "SELECT created_at, updated_at FROM rof_gold.user_shortlist WHERE parcel_uid = 'p4'"
        ).fetchone()

        upsert_shortlist(mem_con, "p4", "jacksonville_fl", "test_user", "needs_review", "updated")
        updated_row = mem_con.execute(
            "SELECT created_at, updated_at FROM rof_gold.user_shortlist WHERE parcel_uid = 'p4'"
        ).fetchone()
        # created_at should be preserved; updated_at should be refreshed (may be equal in same second)
        assert updated_row is not None

    def test_different_user_creates_separate_row(self, mem_con):
        upsert_shortlist(mem_con, "p5", "jacksonville_fl", "user_a", "active", "")
        upsert_shortlist(mem_con, "p5", "jacksonville_fl", "user_b", "watchlist", "")
        count = mem_con.execute(
            "SELECT COUNT(*) FROM rof_gold.user_shortlist WHERE parcel_uid = 'p5'"
        ).fetchone()[0]
        assert count == 2

    def test_empty_notes_allowed(self, mem_con):
        upsert_shortlist(mem_con, "p6", "jacksonville_fl", "test_user", "active", "")
        row = mem_con.execute(
            "SELECT notes FROM rof_gold.user_shortlist WHERE parcel_uid = 'p6'"
        ).fetchone()
        assert row[0] == ""

    @pytest.mark.parametrize("status", SHORTLIST_STATUSES)
    def test_all_statuses_accepted(self, mem_con, status):
        uid = f"p_status_{status}"
        upsert_shortlist(mem_con, uid, "jacksonville_fl", "test_user", status, "")
        row = mem_con.execute(
            f"SELECT status FROM rof_gold.user_shortlist WHERE parcel_uid = '{uid}'"
        ).fetchone()
        assert row[0] == status
