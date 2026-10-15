# Archived race-menu experiment

This version is inactive and is retained for diagnosis and future incremental work.
`Open Arena.cmd` opens the separate Basic map with the tested Marine-only source.

The archived code contains C-style array declarations that SC2's Galaxy compiler
rejects. In Galaxy, the correct form is `int[3] buttons;`, with the dimension after
the type. Do not run this archived builder or copy its generated script into the
active map.

Menus, unit icons, and live speed controls will be brought back in small steps
after the Basic map passes its recovery test.
