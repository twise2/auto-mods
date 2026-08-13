#! /bin/bash
# Builds the local combined mod (heroes-and-villains + regional-heritage +
# exploding-kings + community-games-custom + rewarding-snipes) against
# whatever's currently installed, and deploys it straight into the game's
# local mods folder. Safe to re-run any time - after a game update, after
# Steam "verify integrity of game files", or just to pick up code changes.
#
# Run from Git Bash (or WSL) in this repo's directory:
#   ./build-local-mod.sh
#
# Requires: python with genieutils-py installed (same environment used to
# develop this repo).
set -e

VANILLA="D:/Program Files/Steam/steamapps/common/AoE2DE/resources/_common/dat"
DEPLOY="C:/Users/gwise/Games/Age of Empires 2 DE/76561198037964051/mods/local/localDataMod/resources/_common/dat"
BUILD="./build/local_mod/resources/_common/dat"

MODS="heroes-and-villains regional-heritage exploding-kings community-games-custom rewarding-snipes"

echo "=== Building .dat with mods: $MODS ==="
rm -rf ./build/local_mod
mkdir -p "$BUILD"
python auto-mod.py "$VANILLA/empires2_x2_p1.dat" "$BUILD/empires2_x2_p1.dat" --mods $MODS

echo "=== Syncing CivTechTrees (F11 tech-tree screen) ==="
python sync_tech_trees.py "$VANILLA/empires2_x2_p1.dat" "$VANILLA/CivTechTrees" "$VANILLA/civilizations.json" \
  "$BUILD/CivTechTrees"

echo "=== Patching futuravailableunits.json ==="
python disable_unit_lines.py "$VANILLA/empires2_x2_p1.dat" "$VANILLA/futuravailableunits.json" "$VANILLA/civilizations.json" \
  "$BUILD/futuravailableunits.json"

echo "=== Deploying to $DEPLOY ==="
mkdir -p "$DEPLOY"
cp "$BUILD/empires2_x2_p1.dat" "$DEPLOY/empires2_x2_p1.dat"
cp "$BUILD/futuravailableunits.json" "$DEPLOY/futuravailableunits.json"
cp "$VANILLA/civilizations.json" "$DEPLOY/civilizations.json"
rm -rf "$DEPLOY/CivTechTrees"
cp -r "$BUILD/CivTechTrees" "$DEPLOY/CivTechTrees"

echo "=== Done. Deployed files: ==="
ls -la "$DEPLOY"
