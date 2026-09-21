from sqlalchemy.exc import IntegrityError

from src.riot_scraper.job_scheduler import JobScheduler


class TestSummarizeException:
    def test_surfaces_driver_detail_for_db_errors(self):
        orig = Exception(
            'duplicate key value violates unique constraint "games_pkey"\n'
            "DETAIL: Key (id)=(112233) already exists."
        )
        exc = IntegrityError("INSERT INTO games ...", {"id": "112233"}, orig)

        summary = JobScheduler._summarize_exception(exc)

        assert "IntegrityError" in summary
        assert "Driver error:" in summary
        assert "DETAIL: Key (id)=(112233) already exists." in summary

    def test_surfaces_cause_chain(self):
        try:
            try:
                raise ValueError("root cause")
            except ValueError as e:
                raise RuntimeError("wrapper") from e
        except RuntimeError as e:
            summary = JobScheduler._summarize_exception(e)

        assert "RuntimeError: wrapper" in summary
        assert "Caused by: ValueError: root cause" in summary

    def test_simple_exception_summary(self):
        summary = JobScheduler._summarize_exception(ValueError("boom"))
        assert summary == "ValueError: boom"
