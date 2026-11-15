# Database architecture

Owner: Database and DevOps (Area C). Inputs: reviewed API, asset, field, job and model contracts. Outputs: incremental PostGIS schema, migrations, dictionary and diagrams. Do not store raster binaries, credentials, real farmer exports or unverified source measurements. Application SQLAlchemy/session code belongs under apps/api/app/db.

Must not store: credentials, raw scientific source files outside designated raw folders, or private farmer data in public samples.
