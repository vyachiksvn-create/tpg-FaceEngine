from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterator

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from feature.config import ConfigManager
from feature.storage.models import Base, ImportStatus


class DatabaseManager:
    _instance: DatabaseManager | None = None

    def __init__(self, database_url: str | None = None) -> None:
        if DatabaseManager._instance is not None:
            raise RuntimeError("DatabaseManager уже инициализирован. Используйте get_instance()")

        self._database_url = database_url or self._build_database_url()
        self._engine = self._create_engine()
        self._session_factory = sessionmaker(
            bind=self._engine, expire_on_commit=False, autoflush=False
        )
        self._initialized = False

    @classmethod
    def get_instance(cls, database_url: str | None = None) -> DatabaseManager:
        if cls._instance is None:
            cls._instance = cls(database_url)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        if cls._instance and cls._instance._engine:
            cls._instance._engine.dispose()
        cls._instance = None

    def _build_database_url(self) -> str:
        config = ConfigManager.get_instance()
        db_path = Path(config.paths.workspace) / "storage" / "faces.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"

    def _create_engine(self) -> Engine:
        config = ConfigManager.get_instance()
        engine = create_engine(
            self._database_url,
            echo=config.database.echo,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},
        )
        return engine

    def init_db(self, create_tables: bool = True) -> None:
        if self._initialized:
            logger.debug("База данных уже инициализирована")
            return

        if create_tables:
            logger.info("Создание таблиц базы данных")
            Base.metadata.create_all(self._engine)
            logger.info("Таблицы созданы успешно")
        else:
            logger.debug("Проверка существующих таблиц")
            Base.metadata.reflect(bind=self._engine)

        self._initialized = True
        logger.info(f"База данных инициализирована: {self._database_url}")

    def drop_all_tables(self) -> None:
        logger.warning("Удаление всех таблиц")
        Base.metadata.drop_all(self._engine)
        self._initialized = False
        logger.info("Все таблицы удалены")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session_factory(self) -> sessionmaker[Session]:
        return self._session_factory

    @property
    def engine(self) -> Engine:
        return self._engine

    def dispose(self) -> None:
        self._engine.dispose()
        logger.debug("Соединения с базой данных закрыты")


@contextmanager
def get_session() -> Iterator[Session]:
    db = DatabaseManager.get_instance()
    with db.get_session() as session:
        yield session