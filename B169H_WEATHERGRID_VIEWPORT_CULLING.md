# B169h WeatherGrid viewport culling

Date: 2026-10-01

High-resolution environment grids such as VIIRS can contain far more cells than ordinary forecast grids. The canvas renderer previously scanned every grid cell on each redraw and rejected off-screen cells only inside the nested loop.

B169h derives padded row/column index ranges from the latitude/longitude axes before drawing. Nearest-cell and bilinear rendering then iterate only the viewport slice. This is a presentation/runtime optimization only:
- no source values are changed;
- no WeatherGrid resolution or provenance changes;
- no scoring changes;
- one-cell padding preserves edge cells and interpolation context.

The optimization applies provider-independently, so existing GFS/JMA/CWA/ICON/CAMS grids also benefit when the map is zoomed in.
