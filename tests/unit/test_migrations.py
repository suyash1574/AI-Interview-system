import pytest
from alembic.config import Config
from alembic import script

def test_alembic_migrations_chain():
    cfg = Config("alembic.ini")
    script_dir = script.ScriptDirectory.from_config(cfg)
    revisions = [rev.revision for rev in script_dir.walk_revisions()]
    assert "0001" in revisions
    assert "0002" in revisions
    assert revisions[0] == "0002"
    assert revisions[1] == "0001"
