# Next solo test: v0.2.0

Version **0.2.0** replaces the race/unit/spawn dropdowns with three favorite rows
(10x / 5x / 1x / Match). It adds four sides for a 2v2 sim, realistic armies,
loadouts, upgrades, free resources, building placement and numpad hotkeys.
The scripted checks already passed in SC2; see "What has been verified" in the
[README](../README.md). This checklist covers what needs a person.

1. Close any old test game. Open the map with **Open Arena.cmd** and press **Ctrl+F9**.
2. **Panel.** Two boxes in the top-left: the main panel, with the tools panel below
   it. The rows should show **Marine**, **Void Ray** and **Queen**. Check that no
   text is clipped. **Hide tools** should hide and show the lower box.
3. **Rows.** Press **10x** on Marine, **5x** on Void Ray and **1x** on Queen. The
   team-1 count should read 16. The Queen should have full energy (200/200).
4. **Hotkeys.** Press numpad **7**: 10 Marines. Press **5**: 5 of row 2. Press **3**:
   1 of row 3. Press **0** a few times; the side menu should cycle and a message
   should name the side.
5. **Enemy and Match.** Set **Spawn for** to **Team 2: Enemy**. Pick a unit in
   row 3 and press **Match**. A message should show the count and both values.
   The team-2 value should come close to team 1's. The enemy should attack.
6. **2v2.** Spawn something for **Ally AI** and **Enemy AI**. The AI sides should
   fight each other. Their Medivacs, Observers or Overseers should follow a fighter.
7. **Mix.** With the enemy empty, press **Zerg mix** for the enemy: about 3,000
   resources of a real composition. Press **Terran mix** for yourself; it should
   be scaled to the enemy's value.
8. **Buildings.** In row 2, pick **[Building] Pylon**, press **1x**, and left-click
   the map. Then place a **[Building] Photon Cannon** next to it. Right-click while
   placing should cancel.
9. **Workers build.** Spawn an SCV for yourself and build a Barracks. Minerals stay
   at 99,999 and nothing costs supply.
10. **Spawn point.** Press **Move spawn point** and click a corner. The next spawn
    for that side should appear there.
11. **Upgrades.** Toggle **Max upgrades** for your side to OFF. Your Marines should
    lose +3 weapons and Stimpack. Toggle it back ON.
12. **Loadouts.** Build a small army for yourself. Choose **Loadout 2**, press
    **Save army**, and check that the label lists it. Press **Reset arena**, then
    **Deploy**; the army should come back.
13. **Persistence.** Change row 1 to **Marauder**. Exit the game and press
    **Ctrl+F9** again. Row 1 should start on Marauder, and Loadout 2 should still
    hold the army. This is the one feature the scripted test could not confirm.
14. **Speed.** Drag the speed slider during a fight. It should still snap to the
    five presets.

Report any step that fails, with what you saw. A screenshot of the panel helps if
anything is clipped.

For the original Marine recovery checklist, see [SOLO_TEST.md](SOLO_TEST.md).
For the cause of the earlier compile failures, see [ROOT_CAUSE.md](ROOT_CAUSE.md).
