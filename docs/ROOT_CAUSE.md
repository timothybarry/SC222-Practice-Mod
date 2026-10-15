# Recovery from the race-menu compile failure

The latest failed SC2 test logged 311 compiler errors:

| Errors | Diagnostic |
| ---: | --- |
| 10 | Galaxy array definitions require the dimension after the type |
| 150 | Cannot use `[` because the object is not an array |
| 140 | Incorrect type / implicit cast not allowed |
| 11 | Parameter type does not match the function definition |

The first ten errors were invalid declarations such as `int arenaRaceButtons[3];`.
Galaxy requires `int[3] arenaRaceButtons;`. The failed declarations meant the
subsequent indexed values were not valid arrays, leading to the indexing, cast,
and function-argument errors. Those later errors all occurred on paths using the
invalid array declarations.

The earlier checks inspected API names, argument counts, data references, and XML.
They did not parse Galaxy grammar, so they missed the declaration error. That
validation gap allowed a non-compiling update to replace the working map.

## Recovered baseline at stable-marine-v0.1

- `src/Arena.galaxy` is restored byte-for-byte from the working Marine-only backup.
- `Triggers` and `MapScript.galaxy` match that backup after line-ending normalization.
- The active map has four plain buttons and no arrays, roster generation, icons,
  race submenus, or speed-slider logic.
- `Open Arena.cmd` opens `src/InstantArena_Basic.SC2Map/ComponentList.SC2Components`,
  a fresh document path that avoids reusing the failed map in an old Editor session.
- The race-menu experiment is preserved under `experiments/race-menu-v0.2/` and
  is excluded from the active build.
- A Galaxy parser now checks both the source and generated entrypoint **before**
  the builder changes the playable map files.
- Regression tests confirm that invalid C-style array syntax is rejected,
  correct Galaxy syntax is accepted, and a failed build leaves the map untouched.

The restored script has zero parser syntax diagnostics. Four recovery tests pass.
The Basic map was launched using SC2's Test Document-compatible runtime path, and
the user confirmed the recovery game worked as planned.

The bundled parser checks syntax only. It does not replace the SC2 Editor compiler's
type checking or an in-game test. Those checks are required before accepting later
features.

## Incremental development order

1. Keep this Marine-only version as the stable baseline.
2. Add a plain Zealot button and a plain Zergling button, then compile and play-test.
3. Add race navigation with the same small roster, then test switching and ownership.
4. Add unit icons, then test rendering and mouse hit handling.
5. Add speed controls separately and test changes during combat.

Each step should pass syntax checking, Editor compilation, and a solo gameplay test
before the next step is introduced.
