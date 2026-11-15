# ADR 0005: Redis and Celery

Status: Accepted. Date: 2026-11-14.

Use Redis as broker/cache and Celery for bounded asynchronous provider, processing, and inference jobs. Tasks must be idempotent, observable, rate-aware, and retry only transient failures. Reassess broker choice if workload guarantees require stronger durability.
