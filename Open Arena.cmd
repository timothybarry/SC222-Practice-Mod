@echo off
rem Opens the arena in the SC2 Editor. Checks the default install and S:\Games.
set "MAP=%~dp0src\InstantArena_Basic.SC2Map\ComponentList.SC2Components"
for %%E in ("C:\Program Files (x86)\StarCraft II\StarCraft II Editor_x64.exe" "S:\Games\StarCraft II\StarCraft II Editor_x64.exe") do (
    if exist %%E (
        start "" %%E "%MAP%"
        exit /b 0
    )
)
echo StarCraft II Editor not found. Open this file from the Editor instead:
echo %MAP%
pause
