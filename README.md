# Instant Arena

A StarCraft II custom arena for instant unit spawning and continuous combat.

The active build is **v0.2.0: favorites panel and 2v2 sides**. Pick a unit in one of
three favorite rows and press **10x**, **5x** or **1x**. You can spawn for yourself,
an AI ally, the enemy, or a second enemy AI. You can also spawn a realistic army,
match the other team's value, and save armies as loadouts.
Nothing has been published to Battle.net.

## Open and test

1. Exit the previous test game and close the old map in the Editor.
2. Double-click **Open Arena.cmd**. It finds the Editor in the default install or
   `S:\Games\StarCraft II`, and opens
   `src/InstantArena_Basic.SC2Map/ComponentList.SC2Components`.
3. Press **Ctrl+F9** to run the local test.
4. Follow [NEXT_SOLO_TEST.md](docs/NEXT_SOLO_TEST.md).

## The panel

~~~text
INSTANT ARENA
Team 1   You 16   Ally AI 0   value 2750
Team 2   Enemy 40   Enemy AI 0   value 2700
Spawn for: [Team 1: You          v]
[Marine      v] [10x] [5x] [1x] [Match]
[Void Ray    v] [10x] [5x] [1x] [Match]
[Queen       v] [10x] [5x] [1x] [Match]
[Clear side] [Reset arena] [Hide tools]
Game speed: Normal   (slider)
---------------------------------------- tools
[Terran mix] [Protoss mix] [Zerg mix]
[Loadout 1 v] [Save army] [Deploy]
[Max upgrades: ON] [Move spawn point]
~~~

| Control | What it does |
| --- | --- |
| **Spawn for** | The side every button acts on: **You**, **Ally AI** (team 1), **Enemy**, **Enemy AI** (team 2). |
| **Favorite rows** | Row 1 lists Terran, row 2 Protoss, row 3 Zerg: every multiplayer unit (now including the **Mothership**), then **[Building]** entries. Your picks are remembered between sessions. |
| **10x / 5x / 1x** | Spawn that many at the side's spawn point. For a building, the next left-click on the map places it (right-click cancels). |
| **Match** | Spawns enough of the row's unit to equal the other team's total mineral+gas cost. For example, with 5,550 on the other team, Match with Marines makes 111. |
| **Terran / Protoss / Zerg mix** | A realistic army picked at random from three compositions per race (bio, mech, sky; chargelot-immortal-archon, stalker-colossus, skytoss; roach-ravager-hydra, ling-bane-muta, ultra-ling-infestor). It is scaled to the other team's value, or 3,000 when that team is empty. |
| **Loadouts** | **Save army** stores the selected side's living army in slot 1, 2 or 3. **Deploy** spawns it again for the selected side. Saved between sessions. |
| **Max upgrades** | Toggles all 88 multiplayer researches and +3/+3/+3 for the selected side. On by default for every side. |
| **Move spawn point** | The next left-click sets the selected side's spawn point. |
| **Clear side / Reset arena** | Removes the selected side's units, or everyone's. Spawn points, picks and speed stay. |
| **Game speed** | Slider snapping to Slower, Slow, Normal, Fast, Faster for the whole match. |
| **Hotkeys** | Numpad **7 8 9** = row 1 at 10x/5x/1x, **4 5 6** = row 2, **1 2 3** = row 3. Numpad **0** cycles the side. |

Always on, for every side:

- **Infinite money and gas:** costs and supply are ignored, and the counters show 99,999.
- **Full energy:** casters spawn with full energy, for example a Queen at 200/200.
- **Workers can build:** with free resources, SCVs, Probes and Drones build anything their tech allows.

**2v2 sim:** the AI ally and the enemy sides attack-move toward the other team.
Support units such as Medivacs and Observers follow a fighter. Idle AI units look for
a new target every 2 seconds. You command your own units.

**Two players:** when a second human is in player slot 2, both see the panel. Each
has their own picks, side menu and loadouts, and player 2 starts on team 2. The map's
lobby has to offer that slot first; see [Not done yet](#not-done-yet).

Each side can have up to **200** living spawned units. Protoss buildings need a
Pylon's power, and Zerg buildings need creep, so place a Pylon or Hatchery first.
Enemy units receive attack-move or follow orders only; they do not cast spells.

| Row | Units | Buildings |
| --- | --- | --- |
| Terran | Marine, Marauder, Reaper, Ghost, Hellion, Hellbat, Widow Mine, Cyclone, Siege Tank, Thor, Viking, Medivac, Liberator, Banshee, Raven, Battlecruiser, SCV | Command Center, Planetary Fortress, Supply Depot, Barracks, Factory, Starport, Engineering Bay, Bunker, Missile Turret, Sensor Tower |
| Protoss | Zealot, Stalker, Sentry, Adept, High Templar, Dark Templar, Archon, Immortal, Colossus, Disruptor, Observer, Warp Prism, Phoenix, Void Ray, Oracle, Tempest, Carrier, **Mothership**, Probe | Nexus, Pylon, Gateway, Cybernetics Core, Forge, Photon Cannon, Shield Battery, Robotics Facility, Stargate |
| Zerg | Zergling, Baneling, Roach, Ravager, Hydralisk, Lurker, Infestor, Swarm Host, Ultralisk, Queen, Overlord, Overseer, Mutalisk, Corruptor, Brood Lord, Viper, Drone | Hatchery, Spawning Pool, Evolution Chamber, Roach Warren, Spine Crawler, Spore Crawler |

## What has been verified

Every item below ran in StarCraft II (build Base98310) through the SC2 API, using a
packed test copy of the map with a scripted harness. The harness lives only in
that test copy; the arena itself has no test code.

- The script compiles and runs in the game.
- All 53 units and all 25 buildings spawn.
- The 10x/5x/1x rows spawn the right counts.
- A saved loadout deploys the same 17 units for another side.
- **Match** produced 111 Marines against a 5,550-value team.
- The Terran, Protoss and Zerg mixes spawn scaled armies.
- The Mothership spawns.
- Minerals and gas read 99,999.
- 88 upgrades are researched.
- A Queen spawns at 200/200 energy.
- Enemy units advance and fight.
- Spawn points scale to the map: you at about (10, 13), the ally at about (10, 18.5).

Not verified yet, because these need a person at the keyboard:

- The mouse placement and the numpad hotkeys.
- How the panel looks.
- A second human in slot 2.
- **Reading** saved favorites and loadouts at the start of a session. Saving was
  confirmed, but under the SC2 API the bank is written and never read back. Ctrl+F9
  in the Editor is the real test.

## Not done yet

These items from the request need the SC2 Editor's map tools. No script can do them:

- **Bigger map / random terrain:** the map is 32x32. Change it with **Map > Map
  Size** and the terrain tools. Spawn points and the camera already scale to the
  playable area, so no code change is needed afterwards. Random terrain generation
  is not supported by SC2 scripting.
- **Two humans online:** the lobby has to offer a second user slot in player 2.
  Set this under the **Map** menu's player and game-variant settings, then test with
  two clients. The script already handles a second human.
- **Banks online:** if favorites or loadouts do not persist in online games, the
  bank `InstantArena` may need adding to the map's bank preload list.

## Project files

| Path | Purpose |
| --- | --- |
| `src/Arena.galaxy` | Arena source: panel, roster, sides, loadouts, mixes, AI orders |
| `src/InstantArena_Basic.SC2Map/` | The active editable map, including terrain and triggers |
| `tools/build_map.py` | Checks syntax before updating the map's script and triggers |
| `tools/validate_galaxy.py` | Runs the bundled Galaxy syntax parser |
| `tools/check_api.py` | Checks every API call, argument count, constant, unit and upgrade ID against Blizzard's data |
| `tools/fetch_reference.py` | Downloads that data into `tools/_reference/` (git-ignored) |
| `tools/pack_map.py` | Packs the component folder into one `.SC2Map` file without the Editor |
| `tests/` | Syntax, build, roster, API and packing checks |
| `backups/v0.1-marine-only/` | The original working source and trigger files |
| `experiments/race-menu-v0.2/` | The inactive menu attempt, retained for diagnosis |
| `maps/` | Destination for packed map files |

`InstantArena_Basic.SC2Map` is a component folder. Open its
`ComponentList.SC2Components` file in the Editor. To make a single packed map, run
`python tools/pack_map.py` (writes `maps/InstantArena.SC2Map`), or choose
**File > Save As** in the Editor. Use the Editor's save for Battle.net uploads,
because it compresses the archive.

## Build and validate

Close the active map before editing its files externally. Edit `src/Arena.galaxy`,
then run:

~~~powershell
python tools/fetch_reference.py      # once
python tools/check_api.py
python tools/build_map.py
python -m unittest discover -s tests -v
~~~

Reopen the map and test in SC2. The builder updates only code, trigger data, and
trigger names; it preserves terrain and map settings. `MapScript.galaxy` and
`Triggers` are generated files.

The syntax checker uses installed Node.js, or VS Code's bundled Node runtime when
Node is not on PATH. `check_api.py` catches unknown functions, wrong argument counts,
unknown constants, and unit or upgrade IDs missing from the multiplayer data. The SC2
compiler and an in-game test remain the final authority.

## References

Terrain is adapted from Blizzard's SC2 Editor tutorial
[021_Units_Layer.SC2Map](https://github.com/SC2Mapster/blizzard-tutorials/blob/master/docs/New_Tutorials/02_Terrain_Editor/maps/021_Units_Layer.SC2Map),
preserved by SC2Mapster. Its placed units were removed and its triggers replaced.

- [Blizzard's Trigger Module tutorial and local Test Document](https://s2editor-guides.readthedocs.io/Classic_Tutorials/02_Trigger_Module/1/)
- [Component-folder export](https://s2editor-guides.readthedocs.io/New_Tutorials/07_Lessons/083_Export_Game_Assets/)
- [Bundled parser provenance and MIT license](tools/galaxy_parser/README.md)
- [Blizzard's native API declarations](https://github.com/SC2Mapster/SC2GameData/blob/master/mods/core.sc2mod/base.sc2data/TriggerLibs/natives.galaxy)
- [Blizzard's standard Void multiplayer unit definitions](https://github.com/SC2Mapster/SC2GameData/blob/master/mods/voidmulti.sc2mod/base.sc2data/GameData/UnitData.xml)
- Upgrade list: the researchable upgrades in [python-sc2](https://github.com/BurnySc2/python-sc2)'s `upgrade_researched_from`, matched case-exactly to the game data
