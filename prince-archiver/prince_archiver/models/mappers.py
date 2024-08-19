"""Definition of mappers."""

from typing import Type

from sqlalchemy import ColumnElement
from sqlalchemy.orm import registry, relationship

from prince_archiver.domain import models as domain_models
from prince_archiver.domain import value_objects as vo

from . import v2 as data_models


def get_exclude_fields(model_cls: Type[data_models.Base]) -> list[ColumnElement]:
    return [
        model_cls.created_at.expression,
        model_cls.updated_at.expression,
    ]


def init_mappers():
    mapper_registry = registry()

    mapper_registry.map_imperatively(
        domain_models.DataArchiveEntry,
        data_models.DataArchiveEntry.__table__,
        exclude_properties=get_exclude_fields(data_models.DataArchiveEntry),
    )

    data_archive_member_mapper = mapper_registry.map_imperatively(
        domain_models.DataArchiveMember,
        data_models.DataArchiveMember.__table__,
        properties={
            "_imaging_event_id": (
                data_models.DataArchiveMember.imaging_event_id.expression
            )
        },
        exclude_properties=get_exclude_fields(data_models.DataArchiveMember),
    )

    object_store_entry_mapper = mapper_registry.map_imperatively(
        domain_models.ObjectStoreEntry,
        data_models.ObjectStoreEntry.__table__,
        properties={
            "_imaging_event_id": (
                data_models.ObjectStoreEntry.imaging_event_id.expression
            )
        },
        exclude_properties=get_exclude_fields(data_models.ObjectStoreEntry),
    )

    archive_checksum_mapper = mapper_registry.map_imperatively(
        vo.Checksum,
        data_models.ArchiveChecksum.__table__,
        properties={
            "_event_archive_id": (
                data_models.ArchiveChecksum.event_archive_id.expression
            ),
        },
        exclude_properties=[
            data_models.ArchiveChecksum.id,
            *get_exclude_fields(data_models.ArchiveChecksum),
        ],
    )

    event_archive_mapper = mapper_registry.map_imperatively(
        domain_models.EventArchive,
        data_models.EventArchive.__table__,
        properties={
            "checksum": relationship(
                archive_checksum_mapper,
                uselist=False,
            ),
        },
        exclude_properties=get_exclude_fields(data_models.EventArchive),
    )

    mapper_registry.map_imperatively(
        domain_models.ImagingEvent,
        data_models.ImagingEvent.__table__,
        properties={
            "event_archive": relationship(
                event_archive_mapper,
                uselist=False,
            ),
            "object_store_entry": relationship(
                object_store_entry_mapper,
                uselist=False,
            ),
            "data_archive_member": relationship(
                data_archive_member_mapper,
                uselist=False,
            ),
        },
        exclude_properties=[
            data_models.ImagingEvent.system,
            data_models.ImagingEvent.system_position,
            *get_exclude_fields(data_models.ImagingEvent),
        ],
    )
