"""Build the arena map. Syntax must pass before map files are changed."""

from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

from validate_galaxy import validate

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "src" / "InstantArena_Basic.SC2Map"

WRAPPER = '''include "TriggerLibs/NativeLib"

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


def source_code():
    return (ROOT / "src" / "Arena.galaxy").read_text(encoding="utf-8")


def build():
    if not (MAP / "ComponentList.SC2Components").is_file():
        raise ValueError("The Basic component-folder map is missing.")
    script = source_code()
    generated = WRAPPER.format(script=script)
    # A failed check leaves the existing playable map untouched.
    with tempfile.TemporaryDirectory(prefix="instant_arena_check_") as directory:
        authored = Path(directory) / "Arena.galaxy"
        entrypoint = Path(directory) / "MapScript.galaxy"
        authored.write_text(script, encoding="utf-8")
        entrypoint.write_text(generated, encoding="utf-8")
        print(validate(authored, entrypoint))

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
    (MAP / "MapScript.galaxy").write_text(generated, encoding="utf-8")
    (MAP / "enUS.SC2Data/LocalizedData/TriggerStrings.txt").write_text(
        "Trigger/Name/A0000001=Instant Arena Code\n"
        "Trigger/Name/A0000002=Initialize Instant Arena\n",
        encoding="utf-8",
    )
    print("Built Basic map:", MAP / "ComponentList.SC2Components")


if __name__ == "__main__":
    build()
