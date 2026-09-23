# Demonking

- Result: `../src/demonking.png`, transparent RGBA, 1536×1280, 6×5 cells of 256px.
- Rows: idle 4, attack 6, hit 3, down 5, win 4. Frame durations copied from darkpriest's frames-v3 manifest; see animations.json.
- Source character: `../frames-v3/darkpriest/darkpriest-sheet.png`; unchanged.
- Built-in image_gen edit, 2026-09-23. Prompt: preserve dark priest character and all 22 poses/grid; add vivid violet fighting-spirit flame wisps, amethyst ribbons, lavender sparks and rim glow; lower aura on defeat; transparent empty cells; no scenery or text.
- Generated source: exec-14a563f2-602c-4cca-8488-e27b5894e2d6.png, copied to generated-source.png. Generated 229px cells resampled with nearest-neighbor to 256px for the existing sheet format.
- This is an AI-edited variant, not a pixel-identical effect layer. Preview WebPs are packed from the result, with original animation timings. Game registration is not modified.

Attack frame repair: split at actual transparent gutters (x=1059,1325 in the 1536px sheet), reposition intact thrust poses within 256px cells; regenerate attack.webp. Other motions unchanged. Backup: demonking-before-frame-fix.png.

## Exclusive battle field
- field_demonking.png generated via image_gen using field_guardian.png as the style reference: obsidian cathedral, distant throne, purple eclipse, violet flames, unobstructed combat floor, no characters/text.
- Generated source: exec-3e8fd8bd-bfb8-4de2-b893-767372c15349.png. Runtime WebP: field.webp.
- FIELD_IMG.demonking registered in sprites/field.js and game.html. demonWatch uses this key; fieldAlpha('demonking') returns 0 to remove the background scrim. Other fields retain their settings.
- Verified in actual openBattle rendering; computed ::after opacity is 0. Screenshot: battle-field-preview.png.
