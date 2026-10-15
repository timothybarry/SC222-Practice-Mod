"""Pack the component-folder map into a single .SC2Map file without the Editor.

Writes an uncompressed MPQ (format 1), the archive format .SC2Map files use.
The result opens in SC2 and can be launched through the SC2 API. For a
Battle.net upload, save from the Editor instead so it can compress the archive.

    python tools/pack_map.py [component-folder] [output.SC2Map]
"""

from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "src" / "InstantArena_Basic.SC2Map"
DEFAULT_OUTPUT = ROOT / "maps" / "InstantArena.SC2Map"

HASH_OFFSET, HASH_A, HASH_B, HASH_KEY = 0, 1, 2, 3
FILE_EXISTS = 0x80000000
FILE_SINGLE_UNIT = 0x01000000
SECTOR_SHIFT = 3
HEADER_SIZE = 32


def _crypt_table():
    table = [0] * 0x500
    seed = 0x00100001
    for index1 in range(0x100):
        index2 = index1
        for _ in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            high = (seed & 0xFFFF) << 16
            seed = (seed * 125 + 3) % 0x2AAAAB
            table[index2] = high | (seed & 0xFFFF)
            index2 += 0x100
    return table


CRYPT = _crypt_table()


def hash_string(name, kind):
    seed1, seed2 = 0x7FED7FED, 0xEEEEEEEE
    for character in name.upper():
        value = ord(character)
        seed1 = CRYPT[(kind << 8) + value] ^ ((seed1 + seed2) & 0xFFFFFFFF)
        seed2 = (value + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
    return seed1


def encrypt(data, key):
    seed = 0xEEEEEEEE
    words = struct.unpack(f"<{len(data) // 4}I", data)
    out = []
    for word in words:
        seed = (seed + CRYPT[0x400 + (key & 0xFF)]) & 0xFFFFFFFF
        out.append(word ^ ((key + seed) & 0xFFFFFFFF))
        key = ((~key << 0x15) + 0x11111111 | key >> 0x0B) & 0xFFFFFFFF
        seed = (word + seed + (seed << 5) + 3) & 0xFFFFFFFF
    return struct.pack(f"<{len(out)}I", *out)


def archive_files(source):
    files = {}
    for path in sorted(source.rglob("*")):
        if path.is_file():
            files[str(path.relative_to(source)).replace("/", "\\")] = path.read_bytes()
    files["(listfile)"] = "\r\n".join(files).encode("utf-8") + b"\r\n"
    return files


def pack(source=DEFAULT_SOURCE, output=DEFAULT_OUTPUT):
    source, output = Path(source), Path(output)
    if not (source / "ComponentList.SC2Components").is_file():
        raise ValueError(f"{source} is not a component-folder map.")
    files = archive_files(source)
    table_size = 16
    while table_size < len(files) * 2:
        table_size *= 2

    body = bytearray()
    blocks = []
    for name, data in files.items():
        blocks.append((HEADER_SIZE + len(body), len(data), len(data), FILE_EXISTS | FILE_SINGLE_UNIT))
        body += data

    empty = 0xFFFFFFFF
    hashes = [(empty, empty, 0xFFFF, 0xFFFF, empty)] * table_size
    for index, name in enumerate(files):
        slot = hash_string(name, HASH_OFFSET) % table_size
        while hashes[slot][4] != empty:
            slot = (slot + 1) % table_size
        hashes[slot] = (hash_string(name, HASH_A), hash_string(name, HASH_B), 0, 0, index)

    hash_table = encrypt(b"".join(struct.pack("<IIHHI", *entry) for entry in hashes), hash_string("(hash table)", HASH_KEY))
    block_table = encrypt(b"".join(struct.pack("<IIII", *entry) for entry in blocks), hash_string("(block table)", HASH_KEY))
    hash_offset = HEADER_SIZE + len(body)
    block_offset = hash_offset + len(hash_table)
    size = block_offset + len(block_table)
    header = struct.pack("<4sIIHHIIII", b"MPQ\x1a", HEADER_SIZE, size, 0, SECTOR_SHIFT,
                         hash_offset, block_offset, table_size, len(blocks))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(header + bytes(body) + hash_table + block_table)
    return output, len(files) - 1


if __name__ == "__main__":
    written, count = pack(*sys.argv[1:3])
    print(f"Packed {count} map files into {written}")
