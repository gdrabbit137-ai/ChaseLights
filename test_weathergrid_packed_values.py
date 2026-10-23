"""Round-trip tests for the packed WeatherGrid value arrays."""
import unittest

from weathergrid_packed_values import (
    NULL_SENTINEL,
    is_packed_entry,
    pack_int16_gz,
    unpack_int16_gz,
)


class PackInt16GzTests(unittest.TestCase):
    def test_round_trip_preserves_values_and_missing(self):
        values = [0, 1, -5, 300, None, 359, None]
        entry = pack_int16_gz(values)
        self.assertTrue(is_packed_entry(entry))
        self.assertEqual(entry["enc"], "i16gz")
        self.assertEqual(entry["null_cells"], 2)
        self.assertEqual(unpack_int16_gz(entry), values)

    def test_empty_array_round_trips(self):
        self.assertEqual(unpack_int16_gz(pack_int16_gz([])), [])

    def test_sentinel_range_value_is_rejected(self):
        with self.assertRaises(ValueError):
            pack_int16_gz([NULL_SENTINEL])

    def test_out_of_range_value_is_rejected(self):
        with self.assertRaises(ValueError):
            pack_int16_gz([40000])
        with self.assertRaises(ValueError):
            pack_int16_gz([-40000])

    def test_entry_is_json_serializable_and_ascii(self):
        import json
        entry = pack_int16_gz([1, 2, 3, None])
        text = json.dumps(entry)
        self.assertTrue(text.isascii())

    def test_unknown_encoding_is_rejected_on_unpack(self):
        with self.assertRaises(ValueError):
            unpack_int16_gz({"enc": "zzz", "data": ""})


if __name__ == "__main__":
    unittest.main()
