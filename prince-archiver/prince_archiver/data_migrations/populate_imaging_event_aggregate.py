"""Script for populating v2 models available via imaging timestep aggregate root."""

import asyncio
import logging
import os
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from prince_archiver.definitions import EventType, System
from prince_archiver.models import v1, v2
from prince_archiver.service_layer.uow import get_session_maker

logging.basicConfig(level=logging.INFO)


stmt = select(v1.Timestep).options(joinedload(v1.Timestep.object_store_entry))


async def main():
    logging.info("Populating imaging event aggregate")

    sessionmaker = get_session_maker(os.getenv("POSTGRES_DSN"))

    async with sessionmaker() as session:
        result = await session.stream_scalars(stmt)
        async for timestep in result:
            imaging_event = v2.ImagingEvent(
                id=uuid4(),
                ref_id=timestep.timestep_id,
                created_at=timestep.created_at,
                updated_at=timestep.updated_at,
                timestamp=timestep.timestamp,
                experiment_id=timestep.experiment_id,
                type=EventType.STITCH,
                system=System.PRINCE,
            )

            session.add(imaging_event)

            src_dir = v2.SrcDirInfo(
                local_path=Path(timestep.local_dir),
                staging_path=None,
                img_count=timestep.img_count,
                raw_metadata={},
                imaging_event_id=imaging_event.id,
            )

            session.add(src_dir)

            if object_store_entry := timestep.object_store_entry:
                object_store_entry = v2.ObjectStoreEntry(
                    key=object_store_entry.key,
                    imaging_event_id=imaging_event.id,
                    uploaded_at=object_store_entry.created_at,
                    created_at=object_store_entry.created_at,
                    updated_at=object_store_entry.updated_at,
                )

                session.add(object_store_entry)

        await session.commit()

    logging.info("Populated imaging event aggregate")


if __name__ == "__main__":
    asyncio.run(main())
