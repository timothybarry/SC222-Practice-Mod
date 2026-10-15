# Basic Marine arena test

This recovery test passed: the user confirmed that the game worked as planned.
It documents the original Marine-only baseline. For the current race and unit
dropdown test, follow [NEXT_SOLO_TEST.md](NEXT_SOLO_TEST.md).

Open **Open Arena.cmd**, then press **Ctrl+F9** in the Editor. The active document
is `src/InstantArena_Basic.SC2Map/ComponentList.SC2Components`.

Expected controls:

1. **Spawn My Marine** creates one controllable Marine on your side.
2. **Spawn Enemy Marine** creates one hostile Marine on the other side and sends
   it toward your spawn area.
3. **Clear My Army** removes your army while leaving enemies in place.
4. **Reset Arena** removes both armies and clears both counters.

Let your army die, then spawn again. The session should continue. Each side is
limited to 100 living spawned units.

If you see portrait grids or errors mentioning `arenaRaceButtons`, you have the
old experimental map loaded. Close that document without saving it over the repaired
files, then reopen the Basic map using the launcher.

Publishing is not required for solo tests. Check syntax and recovery regressions with:

```powershell
python tools/validate_galaxy.py
python -m unittest discover -s tests -v
```

Always follow file checks with Editor compilation and a gameplay test.
