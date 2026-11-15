# Farmer field to evidence-backed scenario

1. Farmer selects/draws a field and enters crop history, irrigation, soil, equipment, market and priorities.
2. API validates ownership/geometry and stores the EPSG:4326 boundary in PostGIS with audit metadata.
3. Dataset lookup identifies coverage/time among the six locked source families.
4. Local/object assets or NASA POWER/Meteomatics APIs are read with status, terms, resolution, units and observation time recorded.
5. Raw inputs remain immutable; checksums/manifests capture source metadata.
6. Source QA, CRS/NoData handling, Landsat masks/scale factors, and temporal aggregation produce interim and processed assets.
7. Zonal summaries/features retain pixel support, missingness, quality, lineage and feature schema.
8. Versioned inference runs only when inputs satisfy its feature contract; otherwise report availability/coverage limitations.
9. Agronomic hard constraints precede soft priorities/ranking. Compare baseline and at least two feasible alternatives only when evidence supports them.
10. UI presents evidence, benefit hypotheses, risks, uncertainty, limitations, confidence meaning and local expert review.

Each job is idempotent, bounded, observable and linked to source/model versions. Never emit fabricated values or unverified recommendations.
