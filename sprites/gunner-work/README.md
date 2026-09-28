# Gunner combat and work sprites

44 frames: five combat and six work actions, four frames per action. Compact SD body references paladin. Identity: blonde drill curls, navy bows, navy/gold dress, twin pistols in combat.

gunner-complete.aseprite is the native animation, gunner-complete.png the atlas, gunner-complete.json the runtime metadata. Cell 256x256, root (128,170). Carry/read use manually fixed body-axis pivots independent of prop bounds. Source sheet rows are explicitly separated to avoid neighboring frame fragments.

Generated via image_gen and assembled with Aseprite. Build using build-combined.lua, pack.py, then reports/pack.py, wrap.py and wrap_site.py. check.cjs verifies frame rendering and facility/quest action selection. Dedicated gunner atlas and report mappings are applied in game.
