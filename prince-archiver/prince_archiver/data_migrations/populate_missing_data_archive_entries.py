import asyncio
import logging
import os
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import func, select, Select
from sqlalchemy.orm import contains_eager

from prince_archiver.models import v1
from prince_archiver.service_layer.uow import get_session_maker

logging.basicConfig(level=logging.INFO)


upload_dates_subquery = (
    select(func.date(v1.Timestep.created_at).label("date"))
    .join_from(
        v1.ObjectStoreEntry,
        v1.Timestep,
        onclause=v1.ObjectStoreEntry.timestep_id == v1.Timestep.timestep_id,
    )
    .where(
        func.date(v1.Timestep.created_at) >= date(2024, 7, 23),
        func.date(v1.Timestep.created_at) < date.today(),
    )
    .subquery()
)


archive_dates_subquery = (
    select(func.date(v1.Timestep.created_at).label("date"))
    .join_from(
        v1.DataArchiveEntry,
        v1.Timestep,
        onclause=v1.DataArchiveEntry.timestep_id == v1.Timestep.timestep_id,
    )
    .subquery()
)


missing_dates_stmt: Select[tuple[date]] = (
    select(upload_dates_subquery.c.date)
    .join_from(
        upload_dates_subquery,
        archive_dates_subquery,
        onclause=upload_dates_subquery.c.date == archive_dates_subquery.c.date,
        isouter=True,
    )
    .where(archive_dates_subquery.c.date.is_(None))
    .order_by(upload_dates_subquery.c.date)
    .distinct(upload_dates_subquery.c.date)
)


stmt = (
    select(v1.Timestep)
    .join(v1.ObjectStoreEntry)
    .options(contains_eager(v1.Timestep.object_store_entry))
)


async def main():
    logging.info("Populating missing data archive entries")

    sessionmaker = get_session_maker(
        os.getenv(
            "POSTGRES_DSN", 
            "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        )
    )

    job_id_mapping = defaultdict[date, UUID](uuid4)

    async with sessionmaker() as session:
        result = await session.scalars(missing_dates_stmt)

        missing_dates: set[date] = set(result.all())

        for date_ in sorted(missing_dates):
            result = await session.stream_scalars(
                stmt.where(func.date(v1.Timestep.timestamp) == date_),
            )

            ts = date_ + timedelta(days=1)
            mocked_ts = datetime(ts.year, ts.month, ts.day, 3, tzinfo=UTC)

            async for timestep in result:
                entry = v1.DataArchiveEntry(
                    timestep_id=timestep.timestep_id,
                    job_id=job_id_mapping[date_],
                    file=timestep.object_store_entry.key,
                    archive_path=f"{timestep.experiment_id}/{date_.isoformat()}.tar",
                    created_at=mocked_ts,
                    updated_at=mocked_ts,
                )
                session.add(entry)

        await session.commit()

    logging.info("Populated missing data archive entries")


if __name__ == "__main__":
    asyncio.run(main())
