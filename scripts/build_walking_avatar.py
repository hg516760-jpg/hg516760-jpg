import os
from PIL import Image

def generate_walking_avatar_gif(output_path='assets/walking-avatar.gif', scale=2, fps=15):
    # Palette
    C_TRANSPARENT = (0, 0, 0, 0)
    C_HAIR_1 = (22, 17, 14, 255)
    C_HAIR_2 = (42, 32, 26, 255)
    C_HAIR_3 = (72, 58, 46, 255)
    C_SKIN_BASE = (218, 162, 116, 255)
    C_SKIN_SHADOW = (172, 112, 72, 255)
    C_SKIN_HL = (244, 198, 158, 255)
    C_GLASSES = (15, 15, 18, 255)
    C_EYE_WHITE = (255, 255, 255, 255)
    C_EYE_DARK = (20, 16, 14, 255)
    C_BEARD = (28, 22, 18, 255)
    C_TURTLE = (20, 24, 30, 255)
    C_TURTLE_HL = (36, 42, 54, 255)
    C_BLAZER = (26, 30, 40, 255)
    C_BLAZER_HL = (48, 56, 72, 255)
    C_PANTS = (18, 22, 30, 255)
    C_SHOE = (35, 40, 50, 255)
    C_SOLE = (245, 248, 255, 255)

    W, H = 20, 26

    # 1. Generate base 4-frame walk cycle facing right
    walk_right = []
    for phase in range(4):
        im = Image.new('RGBA', (W, H), C_TRANSPARENT)
        bob = -1 if phase in (1, 3) else 0

        # Hair
        for x, y in [
            (6,0),(7,0),(8,0),(9,0),(10,0),
            (5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(12,1),
            (4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),(12,2),(13,2),
            (4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),(11,3),(12,3),(13,3),(14,3),
            (4,4),(5,4),(6,4),(13,4),(14,4),
            (4,5),(5,5),(13,5),
            (4,6),(5,6)
        ]:
            im.putpixel((x, y + bob), C_HAIR_1)

        for x, y in [(7,1),(8,1),(9,1),(6,2),(7,2),(10,2),(11,2),(7,3),(8,3),(11,3),(12,3)]:
            im.putpixel((x, y + bob), C_HAIR_2)
        im.putpixel((8, 2 + bob), C_HAIR_3)

        # Face
        for y in range(4, 11):
            for x in range(6, 13):
                if im.getpixel((x, y + bob)) == C_TRANSPARENT:
                    im.putpixel((x, y + bob), C_SKIN_BASE)

        # Glasses
        for x, y in [(5,5),(6,5),(7,5),(8,5),(5,6),(8,6),(5,7),(6,7),(7,7),(8,7)]:
            im.putpixel((x, y + bob), C_GLASSES)
        im.putpixel((9, 6 + bob), C_GLASSES)
        for x, y in [(10,5),(11,5),(12,5),(13,5),(10,6),(13,6),(10,7),(11,7),(12,7),(13,7)]:
            im.putpixel((x, y + bob), C_GLASSES)

        # Eyes inside
        im.putpixel((6, 6 + bob), C_EYE_WHITE)
        im.putpixel((7, 6 + bob), C_EYE_DARK)
        im.putpixel((11, 6 + bob), C_EYE_WHITE)
        im.putpixel((12, 6 + bob), C_EYE_DARK)

        # Nose
        im.putpixel((13, 8 + bob), C_SKIN_SHADOW)
        im.putpixel((12, 8 + bob), C_SKIN_HL)

        # Mustache & Beard
        for x in [9, 10, 11, 12]:
            im.putpixel((x, 9 + bob), C_BEARD)
        im.putpixel((10, 10 + bob), C_SKIN_SHADOW)
        im.putpixel((11, 10 + bob), C_SKIN_SHADOW)
        for x, y in [(5,7),(5,8),(5,9),(6,9),(6,10),(7,10),(8,10),(9,11),(10,11),(11,11)]:
            im.putpixel((x, y + bob), C_BEARD)

        # Turtleneck collar
        for x in range(7, 12):
            im.putpixel((x, 12 + bob), C_TURTLE)
        im.putpixel((8, 12 + bob), C_TURTLE_HL)
        im.putpixel((10, 12 + bob), C_TURTLE_HL)

        # Blazer & body (rows 13..18)
        for y in range(13, 19):
            for x in range(5, 14):
                im.putpixel((x, y), C_BLAZER)
        
        im.putpixel((9, 13), C_TURTLE)
        im.putpixel((9, 14), C_TURTLE)
        im.putpixel((8, 13), C_BLAZER_HL)
        im.putpixel((10, 13), C_BLAZER_HL)
        im.putpixel((12, 14), C_BLAZER_HL)
        im.putpixel((12, 15), C_BLAZER_HL)

        # Arms
        if phase == 0:
            for y in range(13, 17):
                im.putpixel((4, y), C_BLAZER)
                im.putpixel((14, y), C_BLAZER_HL)
            im.putpixel((4, 17), C_SKIN_BASE)
            im.putpixel((14, 17), C_SKIN_BASE)
        elif phase in (1, 3):
            for y in range(13, 17):
                im.putpixel((5, y), C_BLAZER)
                im.putpixel((13, y), C_BLAZER_HL)
            im.putpixel((5, 17), C_SKIN_BASE)
            im.putpixel((13, 17), C_SKIN_BASE)
        elif phase == 2:
            for y in range(13, 17):
                im.putpixel((14, y), C_BLAZER)
                im.putpixel((4, y), C_BLAZER_HL)
            im.putpixel((14, 17), C_SKIN_BASE)
            im.putpixel((4, 17), C_SKIN_BASE)

        # Pants & Legs (rows 19..25)
        for x in range(6, 13):
            im.putpixel((x, 19), C_PANTS)

        if phase == 0:
            for y in [20, 21]:
                im.putpixel((5, y), C_PANTS)
                im.putpixel((6, y), C_PANTS)
            im.putpixel((4, 22), C_PANTS)
            im.putpixel((5, 22), C_PANTS)
            im.putpixel((3, 23), C_SHOE)
            im.putpixel((4, 23), C_SHOE)
            im.putpixel((3, 24), C_SOLE)
            im.putpixel((4, 24), C_SOLE)

            for y in [20, 21]:
                im.putpixel((9, y), C_PANTS)
                im.putpixel((10, y), C_PANTS)
            im.putpixel((10, 22), C_PANTS)
            im.putpixel((11, 22), C_PANTS)
            im.putpixel((11, 23), C_SHOE)
            im.putpixel((12, 23), C_SHOE)
            im.putpixel((11, 24), C_SOLE)
            im.putpixel((12, 24), C_SOLE)

        elif phase in (1, 3):
            for y in range(20, 23):
                im.putpixel((7, y), C_PANTS)
                im.putpixel((8, y), C_PANTS)
                im.putpixel((9, y), C_PANTS)
                im.putpixel((10, y), C_PANTS)
            for x in range(6, 12):
                im.putpixel((x, 23), C_SHOE)
                im.putpixel((x, 24), C_SOLE)

        elif phase == 2:
            for y in [20, 21]:
                im.putpixel((9, y), C_PANTS)
                im.putpixel((10, y), C_PANTS)
            im.putpixel((11, 22), C_PANTS)
            im.putpixel((12, 22), C_PANTS)
            im.putpixel((12, 23), C_SHOE)
            im.putpixel((13, 23), C_SHOE)
            im.putpixel((12, 24), C_SOLE)
            im.putpixel((13, 24), C_SOLE)

            for y in [20, 21]:
                im.putpixel((6, y), C_PANTS)
                im.putpixel((7, y), C_PANTS)
            im.putpixel((5, 22), C_PANTS)
            im.putpixel((6, 22), C_PANTS)
            im.putpixel((4, 23), C_SHOE)
            im.putpixel((5, 23), C_SHOE)
            im.putpixel((4, 24), C_SOLE)
            im.putpixel((5, 24), C_SOLE)

        # Scale with nearest-neighbor for sharp pixel art
        im_scaled = im.resize((W * scale, H * scale), Image.NEAREST)
        walk_right.append(im_scaled)

    # 2. Mirror for walk facing left
    walk_left = [im.transpose(Image.FLIP_LEFT_RIGHT) for im in walk_right]

    # 3. Canvas Stage: Width = 800, Height = 56
    STAGE_W = 800
    STAGE_H = H * scale + 4 # 56px
    SPRITE_W = W * scale    # 40px
    SPRITE_H = H * scale    # 52px
    Y_POS = 2               # vertical offset

    START_X = 20
    END_X = STAGE_W - SPRITE_W - 20 # 740
    SPEED = 5 # pixels per frame

    frames = []

    # Sequence A: Walk Right from START_X to END_X
    x = START_X
    step = 0
    while x < END_X:
        f = Image.new('RGBA', (STAGE_W, STAGE_H), C_TRANSPARENT)
        current_sprite = walk_right[step % 4]
        f.paste(current_sprite, (int(x), Y_POS), current_sprite)
        frames.append(f)
        x += SPEED
        step += 1

    # Pause at right turn (2 frames)
    for _ in range(3):
        f = Image.new('RGBA', (STAGE_W, STAGE_H), C_TRANSPARENT)
        idle_r = walk_right[1]
        f.paste(idle_r, (int(END_X), Y_POS), idle_r)
        frames.append(f)

    # Sequence B: Walk Left from END_X back to START_X
    x = END_X
    step = 0
    while x > START_X:
        f = Image.new('RGBA', (STAGE_W, STAGE_H), C_TRANSPARENT)
        current_sprite = walk_left[step % 4]
        f.paste(current_sprite, (int(x), Y_POS), current_sprite)
        frames.append(f)
        x -= SPEED
        step += 1

    # Pause at left turn (2 frames)
    for _ in range(3):
        f = Image.new('RGBA', (STAGE_W, STAGE_H), C_TRANSPARENT)
        idle_l = walk_left[1]
        f.paste(idle_l, (int(START_X), Y_POS), idle_l)
        frames.append(f)

    # Save as transparent animated GIF
    # Convert frames to P mode with transparency
    palette_frames = []
    for frame in frames:
        # Create an RGBA image
        alpha = frame.split()[3]
        # Quantize RGB to 255 colors, leave 1 for transparent
        p_frame = frame.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        # Set transparent pixel where alpha == 0
        mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
        p_frame.paste(255, mask)
        p_frame.info['transparency'] = 255
        palette_frames.append(p_frame)

    frame_duration = int(1000 / fps) # ~66ms per frame
    palette_frames[0].save(
        output_path,
        save_all=True,
        append_images=palette_frames[1:],
        duration=frame_duration,
        loop=0,
        transparency=255,
        disposal=2
    )

    size_kb = os.path.getsize(output_path) / 1024
    print(f"Generated {output_path}: {len(frames)} frames, {size_kb:.1f} KB")

if __name__ == '__main__':
    generate_walking_avatar_gif('assets/walking-avatar.gif')
