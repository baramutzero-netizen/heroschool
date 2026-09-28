# Priest combat and work animations

44 frames, 256px cells, pivot (128,170). Native file: priest-complete.aseprite. Atlas: priest-complete.png. Animation metadata: priest-complete.json.

Combat: idle, attack, hit, down, win. Work: weed, scrub, dust, carry, meditate, read. Four frames per motion. Generated with image_gen from current priest reference; assembled using Aseprite. Transparent background verified through frame rendering.

Integrated through dedicated SPR_X_IMG.priest atlas. reports/runtime.js selects work motions for priest and paladin. Chapel: meditate; library: read; farm: weed; church and salon: dust/scrub; inn and tavern: dust/scrub/carry. Rest and failed training retain existing motions.

Build: Aseprite batch build-combined.lua, then pack.py, reports/pack.py, wrap.py, wrap_site.py from project root. Preview: preview.html. check.cjs verifies all 44 frames and mappings.
