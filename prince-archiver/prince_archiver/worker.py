import asyncio
import tarfile
from concurrent.futures import Executor, ProcessPoolExecutor
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator
import os
import logging

from arq.connections import RedisSettings
import aiofiles
import aiofiles.os
import cv2
import s3fs

from .config import Settings, get_settings
from .dto import TimestepDTO
from .logging import configure_logging


LOGGER = logging.getLogger(__name__)

def compress(src: Path, target: Path):
    LOGGER.info("Compressing %s", src)
    
    img = cv2.imread(str(src))
    cv2.imwrite(
        str(target),
        img,
        params=(cv2.IMWRITE_TIFF_COMPRESSION, 5),
    )

    LOGGER.info("Compressed %s", src)


async def acompress(src: Path, target: Path, executor: Executor):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, compress, src, target)


def tar(src: Path, target: Path):
    LOGGER.info("Tarring %s", src)

    target.parent.mkdir(exist_ok=True)
    with tarfile.open(target, "w") as tar:
        tar.add(src, arcname=".")
    
    LOGGER.info("Tarred %s", src)


async def atar(src: Path, target: Path, executor: Executor):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, tar, src, target)

 
async def workflow(ctx: dict, input_data: dict):

    data = TimestepDTO.model_validate(input_data)

    settings: Settings = ctx["settings"]
    s3: s3fs.S3FileSystem = ctx["s3"]
    pool: ProcessPoolExecutor = ctx["pool"]

    archive_path = settings.ARCHIVE_DIR / data.key

    img_dir = settings.DATA_DIR / data.timestep_dir_name / data.img_dir_name
    files = map(lambda path: img_dir / path, await aiofiles.os.listdir(img_dir))

    async with aiofiles.tempfile.TemporaryDirectory() as _temp_dir:
        temp_dir = Path(_temp_dir)

        await asyncio.gather(
            *(acompress(file, temp_dir / file.name, pool) for file in files),
        )
        await atar(temp_dir, archive_path, pool)

    await s3._put_file(archive_path, f"{settings.AWS_BUCKET_NAME}/{data.key}")


@asynccontextmanager
async def managed_file_system(
    settings: Settings,
) -> AsyncGenerator[s3fs.S3FileSystem, None]:
    s3 = s3fs.S3FileSystem(
        key=settings.AWS_ACCESS_KEY_ID,
        secret=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_ENDPOINT_URL,
        asynchronous=True,
    )

    session = await s3.set_session()

    yield s3

    await session.close()


async def startup(ctx):
    configure_logging()

    settings = get_settings()
    ctx["settings"] = settings

    exit_stack = await AsyncExitStack().__aenter__()
    ctx["exit_stack"] = exit_stack

    ctx["pool"] = exit_stack.enter_context(ProcessPoolExecutor())
    ctx["s3"] = await exit_stack.enter_async_context(managed_file_system(settings))


async def shutdown(ctx: dict):
    exit_stack: AsyncExitStack = ctx["exit_stack"]
    await exit_stack.aclose()


class WorkerSettings:

    functions = [workflow]
    on_startup = startup
    on_shutdown = shutdown

    redis_settings = RedisSettings.from_dsn(
        os.getenv("REDIS_DSN", "redis://localhost:6379"),
    )
