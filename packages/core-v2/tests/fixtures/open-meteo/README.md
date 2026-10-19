# Synthetic Open-Meteo-shaped input

`synthetic-hourly.json` is a generated 72-row, ten-field **all-zero test input**,
not weather observations, a provider capture or a validated grid. It explicitly
marks itself synthetic. The adapter always labels caller-supplied fixtures
TEST_FIXTURE. Mutations in tests exercise invalid/missing values and provenance;
none may be cited as real source acceptance. Real manual evidence is kept
separately with its transport receipt and original response SHA256.
