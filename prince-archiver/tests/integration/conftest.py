from datetime import UTC, datetime
from typing import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from prince_archiver.definitions import Algorithm, EventType, System
from prince_archiver.models import v2 as data_models

CONNECTION_URL = "postgresql+asyncpg://postgres:postgres@localhost:5431/postgres"


@pytest.fixture(name="conn")
async def fixture_conn() -> AsyncGenerator[AsyncConnection, None]:
    engine = create_async_engine(CONNECTION_URL)
    async with engine.connect() as conn:
        yield conn


@pytest.fixture(name="sessionmaker")
async def fixture_sessionmaker(
    conn: AsyncConnection,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    async with conn.begin() as trans:
        sessionmaker = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=conn,
        )

        yield sessionmaker

        await trans.rollback()


@pytest.fixture(name="session")
async def fixture_session(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session


@pytest.fixture(name="imaging_event")
def fixture_imaging_event() -> data_models.ImagingEvent:
    return data_models.ImagingEvent(
        id=uuid4(),
        ref_id=uuid4(),
        type=EventType.STITCH,
        experiment_id="test_experiment_id",
        local_path="/test/path/",
        system=System.PRINCE,
        system_position=3,
        timestamp=datetime(2000, 1, 1, tzinfo=UTC),
    )


@pytest.fixture(name="data_archive_member")
def fixture_data_archive_member(
    imaging_event: data_models.ImagingEvent,
) -> data_models.DataArchiveMember:
    return data_models.DataArchiveMember(
        key="test_key",
        member_key="test_member_key",
        job_id=uuid4(),
        imaging_event_id=imaging_event.id,
    )


@pytest.fixture(name="object_store_entry")
def fixture_object_store_entry(
    imaging_event: data_models.ImagingEvent,
) -> data_models.ObjectStoreEntry:
    return data_models.ObjectStoreEntry(
        key="test_key",
        uploaded_at=datetime(2001, 1, 1, tzinfo=UTC),
        imaging_event_id=imaging_event.id,
    )


@pytest.fixture(name="event_archive")
def fixture_event_archive(
    imaging_event: data_models.ImagingEvent,
) -> data_models.EventArchive:
    return data_models.EventArchive(
        id=uuid4(),
        size=3,
        img_count=10,
        imaging_event_id=imaging_event.id,
    )


@pytest.fixture(name="checksum")
def fixture_checksum(event_archive: data_models.EventArchive):
    return data_models.ArchiveChecksum(
        hex="test_hex",
        algorithm=Algorithm.SHA256,
        event_archive_id=event_archive.id,
    )
