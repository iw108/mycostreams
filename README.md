# Data lifecycle management

Code relating to the lifecycle management of *raw* image data — moving imaging output from
the microscope, into object storage, and on to long-term archival.

This is a monorepo of independent services; each has its own README with setup and usage.

## Services

| Service | Role |
|---|---|
| [`prince-archiver`](prince-archiver/README.md) | Moves local image data to S3-compatible object storage as soon as an imaging event is available (services: `mock-prince`, `exporter`, `purger`, `state-manager`). |
| [`surf-archiver`](surf-archiver/README.md) | CLI + remote client that copies daily data from S3, bundling it into per-experiment, per-day tar archives on the SURF Data Archive and emitting a RabbitMQ message when done. |
| [`export-ingester`](export-ingester/README.md) | Ingests an API payload and pipes it to an SFTP server (e.g. Snellius). |

## Infrastructure

[`infrastructure/`](infrastructure/) holds the shared supporting stack the services run
against: `alloy`, `object-store`, `redis`, and `traefik`.

## DevOps & contributing

See [DEVOPS.md](DEVOPS.md) for the contributing workflow (branch → PR → green CI → merge) and
operational runbook.
