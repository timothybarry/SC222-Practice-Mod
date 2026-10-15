"""Embed Arena.galaxy in the editable SC2 map. Run with the Editor map closed."""

from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "src" / "InstantArena.SC2Map"


def source_code():
    script = (ROOT / "src" / "Arena.galaxy").read_text(encoding="utf-8")
    roster = json.loads((ROOT / "src" / "units.json").read_text(encoding="utf-8"))
    if [race["race"] for race in roster] != ["Terran", "Protoss", "Zerg"]:
        raise ValueError("Roster must contain Terran, Protoss, and Zerg, in that order.")
    code = ["void ArenaInitRoster () {"]
    index = 0
    seen = set()
    for race_index, race in enumerate(roster):
        count = len(race["units"])
        if not 1 <= count <= 15:
            raise ValueError("Each race must fit in the 15-slot submenu.")
        code.append(f'    arenaRaceNames[{race_index}] = {json.dumps(race["race"])};')
        code.append(f"    arenaRaceFirstUnit[{race_index}] = {index};")
        code.append(f"    arenaRaceUnitCounts[{race_index}] = {count};")
        for unit in race["units"]:
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", unit["id"]) or unit["id"] in seen:
                raise ValueError(f'Invalid or duplicate unit id: {unit["id"]}')
            if not unit["icon"].startswith("Assets\\Textures\\") or not unit["icon"].endswith(".dds"):
                raise ValueError("Unit icons must use built-in local texture paths.")
            seen.add(unit["id"])
            for field, value in [("Types", unit["id"]), ("Names", unit["name"]), ("Icons", unit["icon"])]:
                code.append(f"    arenaUnit{field}[{index}] = {json.dumps(value)};")
            index += 1
    if index > 64:
        raise ValueError("Unit roster exceeds the Galaxy array capacity.")
    code.append("}")
    marker = "// @ARENA_ROSTER@"
    if script.count(marker) != 1:
        raise ValueError("Missing or duplicate roster insertion point.")
    return script.replace(marker, "\n".join(code))


def build():
    if not (MAP / "ComponentList.SC2Components").is_file():
        raise SystemExit("The component-folder terrain is missing.")
    script = source_code()
    root = ET.Element("TriggerData")
    items = ET.SubElement(root, "Root")
    ET.SubElement(items, "Item", Type="CustomScript", Id="A0000001")
    ET.SubElement(items, "Item", Type="Trigger", Id="A0000002")
    custom = ET.SubElement(root, "Element", Type="CustomScript", Id="A0000001")
    ET.SubElement(custom, "ScriptCode").text = "\n" + script
    init = ET.SubElement(root, "Element", Type="Trigger", Id="A0000002")
    ET.SubElement(init, "Event", Type="FunctionCall", Id="A0000003")
    ET.SubElement(init, "Action", Type="FunctionCall", Id="A0000004")
    event = ET.SubElement(root, "Element", Type="FunctionCall", Id="A0000003")
    ET.SubElement(event, "FunctionDef", Type="FunctionDef", Library="Ntve", Id="00000120")
    action = ET.SubElement(root, "Element", Type="FunctionCall", Id="A0000004")
    ET.SubElement(action, "FunctionDef", Type="FunctionDef", Library="Ntve", Id="00000123")
    ET.SubElement(action, "ScriptCode").text = "ArenaInit();"
    ET.indent(root, space="    ")
    ET.ElementTree(root).write(MAP / "Triggers", encoding="utf-8", xml_declaration=True)
    strings = MAP / "enUS.SC2Data" / "LocalizedData" / "TriggerStrings.txt"
    strings.write_text(
        "Trigger/Name/A0000001=Instant Arena Code\n"
        "Trigger/Name/A0000002=Initialize Instant Arena\n",
        encoding="utf-8",
    )
    wrapper = '''include "TriggerLibs/NativeLib"

{script}

bool ArenaMapInit (bool testConds, bool runActions) {{
    if (runActions) {{
        ArenaInit();
    }}
    return true;
}}

void InitMap () {{
    trigger init;
    libNtve_InitLib();
    init = TriggerCreate("ArenaMapInit");
    TriggerAddEventMapInit(init);
}}
'''
    (MAP / "MapScript.galaxy").write_text(wrapper.format(script=script), encoding="utf-8")
    print("Updated editable map:", MAP / "ComponentList.SC2Components")


if __name__ == "__main__":
    build()
