"""Download Blizzard's API declarations and multiplayer data for tools/check_api.py.

Source: SC2Mapster's mirror of the shipped game data. Files go to tools/_reference,
which git ignores. Run once, or again after a game patch.
"""

from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "tools" / "_reference"
BASE = "https://raw.githubusercontent.com/SC2Mapster/SC2GameData/master/mods/"
FILES = {
    "natives.galaxy": "core.sc2mod/base.sc2data/TriggerLibs/natives.galaxy",
    "NativeLib.galaxy": "core.sc2mod/base.sc2data/TriggerLibs/NativeLib.galaxy",
    "NativeLib_h.galaxy": "core.sc2mod/base.sc2data/TriggerLibs/NativeLib_h.galaxy",
}
for mod in ["liberty", "libertymulti", "swarm", "swarmmulti", "void", "voidmulti"]:
    for kind in ["Unit", "Upgrade"]:
        FILES[f"{mod}_{kind}Data.xml"] = f"{mod}.sc2mod/base.sc2data/GameData/{kind}Data.xml"


def fetch():
    REFERENCE.mkdir(parents=True, exist_ok=True)
    for name, remote in FILES.items():
        with urllib.request.urlopen(BASE + remote, timeout=60) as response:
            (REFERENCE / name).write_bytes(response.read())
        print("Fetched", name)


if __name__ == "__main__":
    fetch()
