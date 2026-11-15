# ADR 0017: Landsat as MVP field-imagery source

Status: Accepted. Date: 2026-11-15.

Use USGS Landsat 8/9 Collection 2 Level-2 as the MVP satellite imagery source. It supplies surface reflectance, surface temperature and QA metadata. Apply product scale/offset and QA_PIXEL masks before interpreting imagery; retain source resolution and acquisition coverage. Do not claim labels or validated features before inspection.
