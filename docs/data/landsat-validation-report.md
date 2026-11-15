# Landsat Validation & Processing Report (Step 2A)

## 1. Executive Summary

This report documents the validation, radiometrical calibration, QA_PIXEL masking, and spectral/thermal index generation for the Landsat Collection 2 Level-2 imagery covering the Hyderabad pilot study region in Sindh, Pakistan.

---

## 2. Scene Identification & Provenance

- **Discovered Scene ID**: `LC09_L2SP_151043_20250930_20251001_02_T1`
- **Satellite / Sensor**: Landsat 9 / Operational Land Imager 2 (OLI-2) & Thermal Infrared Sensor 2 (TIRS-2)
- **Acquisition Datetime**: `2025-09-30T05:51:13.2784450Z`
- **WRS-2 Coordinates**: Path 151, Row 043
- **Native Projection**: UTM Zone 42N (EPSG:32642), WGS84 Datum
- **Grid Resolution**: 30.0 meters $\times$ 30.0 meters
- **Full Scene Dimensions**: 7,621 columns $\times$ 7,761 rows
- **Discrepancy / Missing Scene Note**:
  The project catalog previously referenced `LC08_L2SP_151043_20250922_20250930_02_T1` with status "user reports downloaded or being organized, local files not located". Physical scan confirmed the archive downloaded on machine is Landsat 9 `LC09_L2SP_151043_20250930_20251001_02_T1.tar` (exact same WRS-2 footprint, acquired 8 days later on 2025-09-30). LC08 is cataloged as MISSING, while LC09 is validated and used with zero data fabrication.

---

## 3. Radiometric Calibration & Scaling Laws

Scaling parameters parsed directly from `LC09_L2SP_151043_20250930_20251001_02_T1_MTL.json`:

1. **Surface Reflectance ($SR$)**:
   $$\text{Reflectance} = \text{DN} \times 0.0000275 - 0.2$$
   Applied across Bands 2 (Blue), 3 (Green), 4 (Red), 5 (NIR), 6 (SWIR1), 7 (SWIR2).
2. **Surface Temperature ($ST$)**:
   $$T_{\text{Kelvin}} = \text{DN}_{\text{B10}} \times 0.00341802 + 149.0$$
   $$T_{^{\circ}\text{C}} = T_{\text{Kelvin}} - 273.15$$

---

## 4. Pixel Quality Assessment (QA_PIXEL)

Bitmask flags decoded over the Hyderabad pilot area (`[68.20°E, 25.20°N, 68.55°E, 25.55°N]`):
- **Bit 0 (Fill)**: 691,539 pixels (off-swath scene edge)
- **Bit 1 (Dilated Cloud)**: 3,983 pixels
- **Bit 2 (Cirrus)**: 0 pixels
- **Bit 3 (Cloud)**: 1,971 pixels
- **Bit 4 (Cloud Shadow)**: 5,233 pixels
- **Bit 7 (Water)**: 24,252 pixels (Indus River channel and major irrigation canals)
- **On-Swath Cloud-Free Pixels**: 828,513
- **Cloud-Free Fraction (On-Swath)**: **98.76%** (0.9876)

---

## 5. Spectral & Thermal Output Statistics

Processed over the pilot area ($1,297 \times 1,180$ grid cells, $828,513$ valid cloud-free observations):

| Variable | File Name | Units | Valid Count | Min | Max | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NDVI** | `data/processed/landsat/ndvi.tif` | index $[-1, 1]$ | 828,512 | -1.0000 | 1.0000 | 0.4481 | 0.2342 |
| **NDMI** | `data/processed/landsat/ndmi.tif` | index $[-1, 1]$ | 828,513 | -1.0000 | 0.9649 | 0.1997 | 0.1772 |
| **BSI** | `data/processed/landsat/bsi.tif` | index $[-1, 1]$ | 828,513 | -0.7363 | 1.0000 | -0.0792 | 0.1552 |
| **LST** | `data/processed/landsat/surface_temperature_c.tif` | $^{\circ}\text{C}$ | 828,513 | 23.94 | 52.98 | 39.30 | 3.90 |
| **Mask** | `data/processed/landsat/cloud_free_mask.tif` | binary $\{0, 1\}$ | 1,530,460 | 0 | 1 | 0.5413 | 0.4983 |

---

## 6. Scientific Limitations

1. **Single Acquisition Date**: Represents late-Kharif seasonal conditions on 2025-09-30; does not capture year-round phenology.
2. **Thermal Resolution**: While resampled to 30 m in Collection 2, TIRS-2 native spatial resolution is 100 m.
3. **Off-Swath Western Margin**: The WRS-2 Path 151 scene boundary intersects the western portion of the bounding box; pixels west of the swath boundary are correctly preserved as NoData ($691,539$ pixels).
