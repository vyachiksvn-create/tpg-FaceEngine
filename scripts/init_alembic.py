from __future__ import annotations

import sys
from pathlib import Path

from feature.config import ConfigManager
from feature.database.database import DatabaseManager


def init_alembic() -> None:
    project_root = Path(__file__).parent.parent
    alembic_ini = project_root / "alembic.ini"
    alembic_dir = project_root / "alembic"

    ConfigManager.reset()
    config = ConfigManager.get_instance()
    config.create_workspace(config.paths)
    db = DatabaseManager.get_instance()
    db.init_db(create_tables=True)

    alembic_ini_content = f"""[alembic]
script_location = alembic
sqlalchemy.url = {db.engine.url}

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

    with open(alembic_ini, "w", encoding="utf-8") as f:
        f.write(alembic_ini_content)

    print(f"alembic.ini создан: {alembic_ini}")
    print("Для создания миграции выполните: alembic revision --autogenerate -m 'init'")


if __name__ == "__main__":
    init_alembic()
