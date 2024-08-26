from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from aio_pika.abc import AbstractIncomingMessage

from prince_archiver.adapters.repository import AbstractTimestepRepo
from prince_archiver.data_archive.handlers import (
    SubscriberMessageHandler,
    add_data_archive_entries,
)
from prince_archiver.models import Timestep
from prince_archiver.service_layer.external_dto import Archive, UpdateArchiveEntries
from prince_archiver.service_layer.messagebus import MessageBus
from prince_archiver.service_layer.uow import AbstractUnitOfWork


@pytest.fixture(name="update_archive_entries_msg")
def fixture_update_archive_entries_msg() -> UpdateArchiveEntries:
    return UpdateArchiveEntries(
        job_id=uuid4(),
        date=date(2000, 1, 1),
        archives=[
            Archive(
                path="test_path",
                src_keys=["test/a", "test/b"],
            )
        ],
    )


async def test_subscriber_handler(update_archive_entries_msg: UpdateArchiveEntries):
    messagebus = AsyncMock(MessageBus)
    handler = SubscriberMessageHandler(messagebus_factory=lambda: messagebus)

    incoming_message = AsyncMock(
        AbstractIncomingMessage,
        body=update_archive_entries_msg.model_dump_json().encode(),
    )

    await handler(incoming_message)
    messagebus.handle.assert_awaited_once_with(update_archive_entries_msg)


async def test_add_data_archive_entries_handler(
    update_archive_entries_msg: UpdateArchiveEntries,
    archived_timestep: Timestep,
    unarchived_timestep: Timestep,
):
    repo = AsyncMock(AbstractTimestepRepo)
    repo.get_by_date.return_value = [archived_timestep, unarchived_timestep]

    uow = AsyncMock(AbstractUnitOfWork, timestamps=repo)

    assert (existing_archive_entry := archived_timestep.data_archive_entry)

    await add_data_archive_entries(update_archive_entries_msg, uow=uow)

    assert unarchived_timestep.data_archive_entry
    assert archived_timestep.data_archive_entry == existing_archive_entry

    uow.commit.assert_awaited_once_with()
