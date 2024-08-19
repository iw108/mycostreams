from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum, Uuid

from prince_archiver.definitions import Algorithm, EventType, System

from .v1 import Base

uuid_pk = Annotated[
    UUID,
    mapped_column(Uuid(native_uuid=False), default=uuid4, primary_key=True),
]


class DataArchiveEntry(Base):
    __tablename__ = "data_archive_entries"

    id: Mapped[uuid_pk]
    type: Mapped[EventType] = mapped_column(
        Enum(EventType, native_enum=False),
    )
    experiment_id: Mapped[str]
    path: Mapped[str]


class DataArchiveMember(Base):
    __tablename__ = "data_archive_members"

    id: Mapped[uuid_pk]
    member_key: Mapped[str]
    job_id: Mapped[UUID | None] = mapped_column(Uuid(native_uuid=False))

    data_archive_entry_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_archive_entries.id"),
    )
    imaging_event_id: Mapped[UUID] = mapped_column(
        ForeignKey("imaging_events.id"),
    )


class ObjectStoreEntry(Base):
    __tablename__ = "object_store_entries"

    id: Mapped[uuid_pk]
    key: Mapped[str]
    uploaded_at: Mapped[datetime]

    imaging_event_id: Mapped[UUID] = mapped_column(
        ForeignKey("imaging_events.id"),
    )


class ArchiveChecksum(Base):
    __tablename__ = "archive_checksums"

    id: Mapped[uuid_pk]
    hex: Mapped[str]
    algorithm: Mapped[Algorithm] = mapped_column(
        Enum(Algorithm, native_enum=False),
    )

    event_archive_id: Mapped[UUID] = mapped_column(
        ForeignKey("event_archives.id"),
    )


class EventArchive(Base):
    __tablename__ = "event_archives"

    id: Mapped[uuid_pk]
    size: Mapped[int]
    img_count: Mapped[int]

    imaging_event_id: Mapped[UUID] = mapped_column(
        ForeignKey("imaging_events.id"),
    )


class ImagingEvent(Base):
    __tablename__ = "imaging_events"

    id: Mapped[uuid_pk]
    ref_id: Mapped[UUID] = mapped_column(Uuid(native_uuid=False))
    type: Mapped[EventType] = mapped_column(
        Enum(EventType, native_enum=False),
    )
    experiment_id: Mapped[str]
    local_path: Mapped[str]
    timestamp: Mapped[datetime]

    # TODO: remove these if not needed.
    system: Mapped[System | None] = mapped_column(
        Enum(System, native_enum=False), nullable=True
    )
    system_position: Mapped[int | None]