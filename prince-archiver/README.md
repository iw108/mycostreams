# Introduction

This project provides a mechanism for moving local Prince image data to an s3 supported
object storage backend as soon as a timestep is available. 

Broadly speaking, it consists of the following components:
- watcher
- upload worker
- data archive worker
- data archive subscriber


# Input directory structure

The input directory structure is assumed to have the form:

```
|- events:
|   |-- *.json
|-- <timestamp>-<Prince position>
|   |-- Img
|   |   |-- *.tif
```

The `*.json` files contain meta data relating to an imaging event. They have the form:
```
{
    timestep_id: UUID
    plate: int
    cross_date: date
    position: int
    timestamp: datetime
    img_count: int
    img_dir: str
}
```
Where `img_dir` is the relative path to directory containing the images.


# Running via docker compose

First run the migraitons. To do this run:

```bash
docker compose run -ti db-migrations
```

This executes the migrations. Now you can get all services started with:

```bash
docker compose -f compose.yml -f compose.dev.yml up
```

The `prince` container will generate a new mock timestep folder every minute. 
Both the `watcher` and `prince` containers have shared volumes. This allows the 
`watcher` container to detect newly added timesteps.


# Local development

The project uses [poetry](https://python-poetry.org/) for dependendancy managment.
To install the project run:

```bash
poetry install
```

Before running the project


Ensure that a `.env` is created appropriately.

Get the dependent services running:

```bash
docker compose -f compose.yml -f compose.dev.yml up db redis s3
```

Now Start the file watcher:

```bash
poetry run watch
```

In a seperate terminal, run the worker:

```bash
poetry run arq prince_archiver.upload_worker.WorkerSettings
```


Generate a timestep with:
```bash
poetry run cli --data-dir <...>
``` 
