"""Script for populating v2 data archive models."""

import asyncio
import logging
import os
from uuid import uuid4

from sqlalchemy import select

from prince_archiver.models import v1, v2
from prince_archiver.service_layer.uow import get_session_maker

logging.basicConfig(level=logging.INFO)


stmt = select(v1.DataArchiveEntry).distinct(v1.DataArchiveEntry.archive_path)

stmt2 = select(v1.DataArchiveEntry, v1.ObjectStoreEntry).join_from(
    v1.DataArchiveEntry,
    v1.ObjectStoreEntry,
    onclause=(v1.DataArchiveEntry.timestep_id == v1.ObjectStoreEntry.timestep_id),
)


async def main():
    logging.info("Populating data archive aggregate")

    sessionmaker = get_session_maker(os.getenv("POSTGRES_DSN"))
    async with sessionmaker() as session:
        archive_stream = await session.stream_scalars(stmt)
        async for item in archive_stream:
            archive_entry = v2.DataArchiveEntry(
                id=uuid4(),
                job_id=item.job_id,
                path=item.archive_path,
                created_at=item.created_at,
                updated_at=item.created_at,
            )
            session.add(archive_entry)

            member_stream = await session.stream(
                stmt2.where(v1.DataArchiveEntry.archive_path == item.archive_path),
            )

            async for item in member_stream:
                v1_archive_entry, object_store_entry = item
                assert isinstance(v1_archive_entry, v1.DataArchiveEntry)
                assert isinstance(object_store_entry, v1.ObjectStoreEntry)

                archive_member = v2.DataArchiveMember(
                    data_archive_entry_id=archive_entry.id,
                    member_key=object_store_entry.key.split("/")[-1],
                    src_key=object_store_entry.key,
                    created_at=archive_entry.created_at,
                    updated_at=archive_entry.updated_at,
                )

                session.add(archive_member)

        await session.commit()

    logging.info("Populated data archive aggregate")


if __name__ == "__main__":
    asyncio.run(main())
