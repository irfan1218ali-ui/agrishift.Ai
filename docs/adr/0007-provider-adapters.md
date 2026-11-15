# ADR 0007: Six-source adapter boundaries

Status: Accepted. Date: 2026-11-15.

Keep typed adapter boundaries for SMAP, GPM IMERG, Landsat, terrain, NASA POWER and Meteomatics. The first four consume local/object-store assets; only POWER and Meteomatics require active runtime API adapters. Normalize metadata/errors and inject transport/config. Do not retain inactive integration stubs for excluded providers.
