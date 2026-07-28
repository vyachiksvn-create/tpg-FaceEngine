from __future__ import annotations

import sys
from pathlib import Path

import click
import cv2
from loguru import logger

from feature.config import AppConfig, ConfigManager
from feature.database.database import DatabaseManager
from feature.database.logger import setup_logger
from feature.database.models import Embedding, Identity, Photo
from feature.import_.importer import PhotoImporter
from feature.recognition.engine import RecognitionEngine


@click.group()
@click.option("--config", "config_path", type=click.Path(exists=False), help="Путь к конфигурационному файлу")
@click.option("--profile", type=str, help="Активный профиль")
@click.pass_context
def main(ctx: click.Context, config_path: str | None, profile: str | None) -> None:
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path
    ctx.obj["profile"] = profile
    ConfigManager.reset()
    config = ConfigManager.get_instance(config_path)
    if profile:
        config.active_profile = profile
    setup_logger(config)
    DatabaseManager.get_instance()
    ctx.obj["config"] = config
    logger.info(f"FaceArchive v0.1.0-alpha запущен. Профиль: {config.active_profile}")


@main.command()
@click.option("--base-photos", type=click.Path(exists=True), help="Путь к основной базе фотографий")
@click.option("--incoming", type=click.Path(exists=True), help="Путь к папке с новыми фотографиями")
@click.pass_context
def init(ctx: click.Context, base_photos: str | None, incoming: str | None) -> None:
    config: AppConfig = ctx.obj["config"]
    if base_photos:
        config.paths.base_photos = str(Path(base_photos).resolve())
    if incoming:
        config.paths.incoming = str(Path(incoming).resolve())
    config.create_workspace(config.paths)
    DatabaseManager.get_instance().init_db(create_tables=True)
    config.save_config(config)
    click.echo(f"Рабочее пространство создано: {config.paths.workspace}")
    click.echo(f"База фотографий: {config.paths.base_photos}")
    click.echo(f"Входящие: {config.paths.incoming}")


@main.command()
@click.argument("folder_path", type=click.Path(exists=True))
@click.pass_context
def import_(ctx: click.Context, folder_path: str) -> None:
    config: AppConfig = ctx.obj["config"]
    importer = PhotoImporter(config)
    folder = Path(folder_path)

    def progress_callback(progress: Any) -> None:
        click.echo(
            f"\rИмпортировано: {progress.processed}/{progress.total} "
            f"({progress.percent:.1f}%) - {progress.current_file}",
            nl=False,
        )

    try:
        result = importer.import_folder(folder, progress_callback=progress_callback)
        click.echo()
        click.echo(f"Импорт завершен: {result.imported} импортировано, {result.skipped} пропущено, {result.errors} ошибок")
    except Exception as e:
        logger.error(f"Ошибка импорта: {e}")
        click.echo(f"Ошибка: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--top-k", default=5, help="Количество результатов")
@click.pass_context
def search(ctx: click.Context, image_path: str, top_k: int) -> None:
    config: AppConfig = ctx.obj["config"]
    engine = RecognitionEngine(config)
    image = cv2.imread(image_path)
    if image is None:
        click.echo(f"Не удалось прочитать изображение: {image_path}", err=True)
        sys.exit(1)
    faces = engine.detect_faces(image)
    if not faces:
        click.echo("Лица не обнаружены", err=True)
        sys.exit(1)
    embedding = engine.get_embedding(image, faces[0])
    click.echo(f"Embedding получен, размерность: {embedding.shape}")
    click.echo("Поиск в базе данных...")


@main.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    config: AppConfig = ctx.obj["config"]
    db = DatabaseManager.get_instance()
    db.init_db(create_tables=False)
    with db.get_session() as session:
        identity_count = session.query(Identity).count()
        photo_count = session.query(Photo).count()
        embedding_count = session.query(Embedding).count()
    click.echo(f"Профиль: {config.active_profile}")
    click.echo(f"Идентичности: {identity_count}")
    click.echo(f"Фотографии: {photo_count}")
    click.echo(f"Embeddings: {embedding_count}")


@main.command()
@click.argument("profile_name")
@click.pass_context
def profile_use(ctx: click.Context, profile_name: str) -> None:
    config: AppConfig = ctx.obj["config"]
    if profile_name not in config.profiles:
        click.echo(f"Профиль '{profile_name}' не найден", err=True)
        sys.exit(1)
    config.active_profile = profile_name
    config.save_config(config)
    click.echo(f"Активный профиль: {profile_name}")


if __name__ == "__main__":
    main()
