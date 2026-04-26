from backend.app.services.oracle import Oracle


def test_oracle_missing_repository_returns_uncertain_answer():
    class DB:
        def get(self, *_):
            return None

    answer, evidence = Oracle().answer(DB(), 404, "why")
    assert "could not find" in answer.lower()
    assert evidence == []
