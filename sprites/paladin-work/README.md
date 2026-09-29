# Paladin work motion draft

## 2026-09-29 victory frame correction

The combined atlas is integrated into the game with 5 combat and 6 work motions.
The source down row extended below its nominal y=909 boundary into three victory cells.
`build-combined.lua` now retains the connected victory silhouette before computing bounds,
removing these detached down-pose fragments without cropping the raised victory weapon.
All four exported victory frames were checked for detached components, and runtime rendering passed.

Six actions, four frames each. Original generated sheet: source.png. Native Aseprite draft: paladin-work.aseprite, flattened character/tools layer, six tags. Preview: preview.html.

CORRECTION: PNG alpha was verified: empty background pixels are transparent (alpha 0). The earlier opaque-background warning was a visual inspection error. This is a transparent motion/style draft, not yet integrated into the game. Aseprite cells are 256px.

Tool: image_gen, reference: sprites/frames-v3/paladin/idle-00.png. Assembly: Aseprite.

Prompt: Create an animation sprite sheet of EXACTLY the female paladin in the reference, matching her existing tiny detailed chibi pixel-art RPG sprite appearance and proportions: gold blonde side tied hair/navy ribbon, green eyes, huge head short body about 2.3 heads tall, silver/navy armor with gold trim, ivory skirt and navy cape. NOT a new character or taller illustration. REMOVE shield and mace for ALL work actions. Transparent background true alpha. Sheet exactly FOUR equal columns and SIX equal rows, 24 full body sprites, each centered inside its own identical cell with ample transparent padding, same character scale, each cell baseline at 85% cell height. No borders, labels, text, scenery or ground shadows. Suggested canvas 1536x2304, cells384x384. The SAME character repeats 24 times with changed articulated pose, NOT merely translated. Face three-quarter right consistently. Row1 four-frame WEED PULL: kneel lean forward hands reaching green weed; grip low at soil; lean back pulling roots upward; hold tiny pulled weed and recover. Row2 CLOTH FLOOR SCRUB: kneeling with knees on ground, both hands pressing small pale blue rag to floor; reach forward; scrub far right; draw rag back. Row3 DUST WALL: standing feather duster in right hand, lowered at waist; raise arm shoulder level; sweep duster above head to right; lower toward shoulder. No wall drawn. Row4 CARRY FOOD: walking balanced tray with bread and bowl, both hands stable under tray; left step; passing feet; right step; passing feet, slight natural bob but stable food. Row5 MEDITATE: sit cross-legged, eyes closed, hands resting knees; gentle breathe in shoulders lift; breathe peak; breathe out, subtle hair movement. Row6 TURN OPEN BOOK: standing holding open brown book in left hand at chest; right hand pinch right page; page arcs midway across; page settled left, hand relaxes. Four sequential key poses PER ROW, body and head size identical across rows except lowered kneeling/seated poses. No extra arms hands, exactly two arms per character. Clear readable compact pixel-like outlines and detailed clothing, reference identity locked. One sheet only.
