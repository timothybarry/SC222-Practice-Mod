"""Check Arena.galaxy against Blizzard's shipped API and game data.

The Galaxy parser only checks grammar. This catches the next class of Editor
compile errors without SC2: unknown functions, wrong argument counts, unknown
constants, and unit or upgrade IDs that do not exist in the multiplayer data.

Reference files come from tools/fetch_reference.py (kept out of git).
"""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "tools" / "_reference"
DATA_MODS = ["liberty", "libertymulti", "swarm", "swarmmulti", "void", "voidmulti"]
KEYWORDS = {"if", "while", "return", "else", "break", "continue", "include", "for", "sizeof"}
TYPES = r"(?:void|bool|int|fixed|string|text|unit|unitgroup|point|playergroup|order|abilcmd|trigger|bank|region|color|unitfilter|timer|wave|sound|actor|camerainfo)"


def strip_comments(source):
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    return re.sub(r"//[^\n]*", "", source)


def strip_strings(source):
    return re.sub(r'"(?:\\.|[^"\\])*"', '""', source)


def count_arguments(text):
    """Count top-level comma-separated arguments in a call's parentheses."""
    if not text.strip():
        return 0
    depth = 0
    count = 1
    for character in text:
        if character in "([":
            depth += 1
        elif character in ")]":
            depth -= 1
        elif character == "," and depth == 0:
            count += 1
    return count


def parameter_count(parameters):
    parameters = parameters.strip()
    return 0 if not parameters or parameters == "void" else parameters.count(",") + 1


def declarations(source):
    """Function name -> parameter count, and constant names, from Galaxy source."""
    source = strip_comments(source)
    functions = {}
    for match in re.finditer(r"(?:native\s+)?\b" + TYPES + r"\s+(\w+)\s*\(([^)]*)\)\s*[;{]", source):
        functions[match.group(1)] = parameter_count(match.group(2))
    constants = set(re.findall(r"\bconst\s+\w+\s+(\w+)\s*=", source))
    return functions, constants


def calls(source):
    """(name, argument count, line) for every call in the source."""
    clean = strip_strings(strip_comments(source))
    found = []
    for match in re.finditer(r"\b(\w+)\s*\(", clean):
        name = match.group(1)
        if name in KEYWORDS:
            continue
        # Skip definitions: "type Name (".
        before = clean[:match.start()].rstrip()
        if re.search(r"\b" + TYPES + r"$", before):
            continue
        depth = 1
        position = match.end()
        while depth:
            character = clean[position]
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
            position += 1
        line = clean.count("\n", 0, match.start()) + 1
        found.append((name, count_arguments(clean[match.end():position - 1]), line))
    return found


def data_ids(kind):
    ids = set()
    for mod in DATA_MODS:
        path = REFERENCE / f"{mod}_{kind}Data.xml"
        ids |= set(re.findall(r'<C' + kind + r' id="([^"]+)"', path.read_text(encoding="utf-8", errors="ignore")))
    return ids


def function_strings(source, name):
    """Every word inside string literals of one function."""
    match = re.search(r"\b" + TYPES + r"\s+" + name + r"\s*\([^)]*\)\s*\{", source)
    if not match:
        raise ValueError(f"{name} is missing from Arena.galaxy")
    depth = 1
    position = match.end()
    while depth:
        depth += {"{": 1, "}": -1}.get(source[position], 0)
        position += 1
    words = []
    for literal in re.findall(r'"([^"]*)"', source[match.start():position]):
        words += literal.split()
    return words


def reference_available():
    return (REFERENCE / "natives.galaxy").is_file() and (REFERENCE / "NativeLib_h.galaxy").is_file() and (REFERENCE / "voidmulti_UnitData.xml").is_file()


def check(path=ROOT / "src" / "Arena.galaxy"):
    source = Path(path).read_text(encoding="utf-8")
    natives, native_constants = declarations((REFERENCE / "natives.galaxy").read_text(encoding="utf-8", errors="ignore"))
    library, library_constants = declarations((REFERENCE / "NativeLib.galaxy").read_text(encoding="utf-8", errors="ignore"))
    _, header_constants = declarations((REFERENCE / "NativeLib_h.galaxy").read_text(encoding="utf-8", errors="ignore"))
    library_constants |= header_constants
    own, own_constants = declarations(source)
    known = {**natives, **library, **own}
    constants = native_constants | library_constants | own_constants
    errors = []

    for name, arguments, line in calls(source):
        if name not in known:
            errors.append(f"line {line}: unknown function {name}")
        elif known[name] != arguments:
            errors.append(f"line {line}: {name} takes {known[name]} arguments, called with {arguments}")

    for name in sorted(set(re.findall(r"\b(c_\w+|libNtve_ge_\w+)\b", strip_strings(strip_comments(source))))):
        if name not in constants:
            errors.append(f"unknown constant {name}")

    units = data_ids("Unit")
    unit_words = []
    for function in ["ArenaRosterUnits", "ArenaRosterBuildings", "ArenaBaseType"]:
        unit_words += function_strings(source, function)
    for function in ["ArenaMix"]:
        unit_words += [word for word in function_strings(source, function) if not word.isdigit()]
    for word in sorted(set(unit_words)):
        if word not in units:
            errors.append(f"unknown unit type {word}")

    upgrades = data_ids("Upgrade")
    for word in sorted(set(function_strings(source, "ArenaUpgradeList"))):
        if word not in upgrades:
            errors.append(f"unknown upgrade {word}")

    if errors:
        raise ValueError("\n".join(errors))
    return f"PASS: API calls, constants, {len(set(unit_words))} unit types and upgrades checked."


if __name__ == "__main__":
    if not reference_available():
        print("Reference files missing. Run: python tools/fetch_reference.py", file=sys.stderr)
        raise SystemExit(1)
    try:
        print(check(*sys.argv[1:]))
    except ValueError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
