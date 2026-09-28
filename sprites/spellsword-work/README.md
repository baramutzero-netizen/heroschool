# Spellsword animations

44 frames: 5 combat and 6 work actions, four frames each. Body proportions reference the compact paladin SD sprite; identity preserves red ponytail, blue bow and navy/gold costume. Native source: spellsword-complete.aseprite; atlas: spellsword-complete.png; metadata: spellsword-complete.json. 256px cells, pivot (128,170).

Generated with image_gen; sliced and assembled in Aseprite. Row and column boundaries are explicitly selected to keep neighboring tools and hair out of each frame. Combat and work use the existing game renderer and pause/speed handling. Facility/quest work mappings match paladin and priest.

Rebuild: Aseprite batch build-combined.lua; python pack.py; python reports/pack.py; python wrap.py; python wrap_site.py. Paths except local pack.py are relative to game root. check.cjs checks all 44 rendered frames and action mappings.
