# Ninja combat and work sprites

Built-in image_gen sources, assembled with native Aseprite Lua.
Paladin-inspired compact SD proportions; existing ninja ponytail, navy outfit and maroon accents retained.

- `ninja-complete.png`: 1024 × 2816, 256px cells, 4 columns × 11 motions.
- `ninja-complete.aseprite`: 44 frames, named animation tags.
- `ninja-complete.json`: frame rectangles, durations, pivot [128, 170].
- `prompts.json`: generation prompts.
- `source.png` / `combat-source.png`: preserved generated inputs.
- `build-combined.lua`: cell extraction and root alignment; carry/read use body-axis anchors.
- `pack.py`: embeds dedicated ninja atlas into game.html.

Motion order: idle, attack, hit, down, win, weed, scrub, dust, carry, meditate, read.
Farm uses weed; church/salon use dust and scrub; inn/tavern also use carry.
Chapel uses meditate; library uses read. Rest/failed states retain fallback behavior.

Rebuild: run build-combined.lua with Aseprite batch, then pack.py, reports/pack.py, wrap.py, wrap_site.py.
Verification: check.cjs renders all 44 frames through the game renderer and checks quest/facility mappings.
