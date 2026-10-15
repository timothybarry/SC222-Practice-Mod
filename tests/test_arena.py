"""Checks for the v0.2 arena: roster, mixes, upgrades, API use and map packing."""

from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_map
import check_api
import pack_map

SOURCE = build_map.source_code()


def words(function):
    return check_api.function_strings(SOURCE, function)


def roster_block(function, race):
    """The words returned for one race (1 Terran, 2 Protoss, 3 Zerg)."""
    body = SOURCE[SOURCE.index(function + " (int race) {"):]
    body = body[body.index(f"if (race == {race})"):]
    return body[body.index('"') + 1:body.index('";')].split()


class RosterTests(unittest.TestCase):
    def test_rows_match_the_sketch_defaults(self):
        for race, default in [(1, "Marine"), (2, "VoidRay"), (3, "Queen")]:
            self.assertIn(default, roster_block("ArenaRosterUnits", race))
        self.assertIn('ArenaFillRow(1, "Marine")', SOURCE)
        self.assertIn('ArenaFillRow(2, "VoidRay")', SOURCE)
        self.assertIn('ArenaFillRow(3, "Queen")', SOURCE)

    def test_roster_sizes(self):
        units = [len(roster_block("ArenaRosterUnits", race)) for race in (1, 2, 3)]
        buildings = [len(roster_block("ArenaRosterBuildings", race)) for race in (1, 2, 3)]
        self.assertEqual(units, [17, 19, 17])
        self.assertEqual(buildings, [10, 9, 6])
        self.assertIn("Mothership", roster_block("ArenaRosterUnits", 2))

    def test_no_duplicate_roster_entries(self):
        for race in (1, 2, 3):
            entries = roster_block("ArenaRosterUnits", race) + roster_block("ArenaRosterBuildings", race)
            self.assertEqual(len(entries), len(set(entries)), race)

    def test_mixes_use_roster_units_in_pairs(self):
        roster = set()
        for race in (1, 2, 3):
            roster |= set(roster_block("ArenaRosterUnits", race))
        mix = words("ArenaMix")
        types = [word for word in mix if not word.isdigit()]
        counts = [word for word in mix if word.isdigit()]
        self.assertEqual(len(types), len(counts))
        body = SOURCE[SOURCE.index("string ArenaMix (int race"):SOURCE.index("int ArenaMixValue")]
        self.assertEqual(body.count('return "'), 9)
        self.assertLessEqual(set(types), roster)
        # The unique Mothership is never scaled up inside a mix.
        self.assertNotIn("Mothership", types)

    def test_upgrade_list_is_complete_and_unique(self):
        upgrades = words("ArenaUpgradeList")
        self.assertEqual(len(upgrades), 88)
        self.assertEqual(len(upgrades), len(set(upgrades)))
        for line in ["TerranInfantryWeaponsLevel3", "ProtossShieldsLevel3", "ZergFlyerArmorsLevel3", "Stimpack", "Charge"]:
            self.assertIn(line, upgrades)

    def test_hotkeys_cover_all_nine_buttons_and_side(self):
        for key in range(10):
            self.assertIn(f"c_keyNumPad{key}, true", SOURCE)


@unittest.skipUnless(check_api.reference_available(), "run tools/fetch_reference.py first")
class ApiTests(unittest.TestCase):
    def test_api_calls_constants_and_ids_exist(self):
        self.assertIn("PASS", check_api.check())

    def test_checker_rejects_bad_calls(self):
        broken = SOURCE.replace("UnitSetPropertyFixed(spawned, c_unitPropEnergyPercent, 100.0)",
                                "UnitSetPropertyFixed(spawned, 100.0)").replace("Mothership Probe", "Mothersheep Probe")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Arena.galaxy"
            path.write_text(broken, encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                check_api.check(path)
        self.assertIn("UnitSetPropertyFixed takes 3", str(caught.exception))
        self.assertIn("Mothersheep", str(caught.exception))


def decrypt(data, key):
    seed = 0xEEEEEEEE
    out = []
    for word in struct.unpack(f"<{len(data) // 4}I", data):
        seed = (seed + pack_map.CRYPT[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        plain = word ^ ((key + seed) & 0xFFFFFFFF)
        key = ((~key << 0x15) + 0x11111111 | key >> 0x0B) & 0xFFFFFFFF
        seed = (plain + seed + (seed << 5) + 3) & 0xFFFFFFFF
        out.append(plain)
    return struct.pack(f"<{len(out)}I", *out)


def read_archive_file(archive, name):
    """Minimal MPQ reader, enough to read back pack_map's uncompressed output."""
    _, _, _, _, _, hash_offset, block_offset, hash_count, block_count = struct.unpack("<4sIIHHIIII", archive[:32])
    hashes = decrypt(archive[hash_offset:hash_offset + hash_count * 16], pack_map.hash_string("(hash table)", 3))
    blocks = decrypt(archive[block_offset:block_offset + block_count * 16], pack_map.hash_string("(block table)", 3))
    slot = pack_map.hash_string(name, 0) % hash_count
    while True:
        a, b, _, _, index = struct.unpack("<IIHHI", hashes[slot * 16:slot * 16 + 16])
        if index == 0xFFFFFFFF:
            raise KeyError(name)
        if a == pack_map.hash_string(name, 1) and b == pack_map.hash_string(name, 2):
            offset, size, _, _ = struct.unpack("<IIII", blocks[index * 16:index * 16 + 16])
            return archive[offset:offset + size]
        slot = (slot + 1) % hash_count


class PackTests(unittest.TestCase):
    def test_packed_map_contains_the_built_script(self):
        with tempfile.TemporaryDirectory() as directory:
            output, count = pack_map.pack(output=Path(directory) / "Arena.SC2Map")
            archive = output.read_bytes()
        self.assertEqual(archive[:4], b"MPQ\x1a")
        self.assertGreater(count, 20)
        script = (build_map.MAP / "MapScript.galaxy").read_bytes()
        self.assertEqual(read_archive_file(archive, "MapScript.galaxy"), script)
        listed = read_archive_file(archive, "(listfile)").decode("utf-8").split()
        self.assertIn("enUS.SC2Data\\LocalizedData\\TriggerStrings.txt", listed)

    def test_known_hash_value(self):
        # Published StormLib value for the hash-table key.
        self.assertEqual(pack_map.hash_string("(hash table)", 3), 0xC3AF3770)


if __name__ == "__main__":
    unittest.main()
