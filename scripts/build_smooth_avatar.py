import math
import os
import numpy as np
from PIL import Image

def build_smooth_walking_avatar(
    output_path='assets/walking-avatar.gif',
    stage_w=850,
    char_h=96,
    fps=12,
    speed_px_per_frame=3.2
):
    print("Loading component parts...")
    arm_im = Image.open('scripts/rig_arm_near.png')
    leg_near_im = Image.open('scripts/rig_leg_near.png')
    leg_far_im = Image.open('scripts/rig_leg_far.png')
    torso_im = Image.open('scripts/rig_torso_clean.png')
    front_im = Image.open('scripts/clean_char_front.png')

    # Shaded far limbs for depth
    far_arm_im = Image.fromarray((np.array(arm_im) * [0.75, 0.75, 0.75, 1.0]).astype('uint8'))
    far_leg_dark = Image.fromarray((np.array(leg_far_im) * [0.80, 0.80, 0.80, 1.0]).astype('uint8'))

    ARM_PIVOT = (85, 60)
    ARM_WORLD_PIVOT = (240, 740)
    LEG_NEAR_PIVOT = (60, 40)
    LEG_NEAR_WORLD_PIVOT = (270, 1320)
    LEG_FAR_PIVOT = (120, 40)
    LEG_FAR_WORLD_PIVOT = (230, 1320)

    def rotate_about_pivot(img, angle_deg, pivot):
        px, py = pivot
        pad = 200
        w, h = img.size
        expanded = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
        expanded.paste(img, (pad, pad), img)
        rotated = expanded.rotate(angle_deg, resample=Image.BICUBIC, center=(px + pad, py + pad))
        return rotated, px + pad, py + pad

    def render_hires_frame(cycle_progress):
        phase_rad = cycle_progress * 2 * math.pi
        # Smooth natural arm and leg swing
        near_leg_angle = 13.0 * math.cos(phase_rad)
        far_leg_angle  = -13.0 * math.cos(phase_rad)
        near_arm_angle = -16.0 * math.cos(phase_rad)
        far_arm_angle  = 16.0 * math.cos(phase_rad)
        
        # Natural vertical body bob (weight transfer dip and push-off rise)
        bob_y = int(14.0 * (math.cos(2 * phase_rad) + 1) / 2)
        lift_far  = max(0, math.sin(phase_rad)) * 28 if math.sin(phase_rad) > 0 else 0
        lift_near = max(0, -math.sin(phase_rad)) * 28 if -math.sin(phase_rad) > 0 else 0

        CANVAS_W, CANVAS_H = 750, 2400
        frame = Image.new('RGBA', (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        BASE_X = 120

        # 1. Far Arm (back)
        rot_arm_f, piv_fx, piv_fy = rotate_about_pivot(far_arm_im, far_arm_angle, ARM_PIVOT)
        frame.paste(rot_arm_f, (BASE_X + ARM_WORLD_PIVOT[0] - piv_fx, ARM_WORLD_PIVOT[1] + bob_y - piv_fy), rot_arm_f)

        # 2. Far Leg
        rot_leg_f, l_piv_fx, l_piv_fy = rotate_about_pivot(far_leg_dark, far_leg_angle, LEG_FAR_PIVOT)
        frame.paste(rot_leg_f, (BASE_X + LEG_FAR_WORLD_PIVOT[0] - l_piv_fx, LEG_FAR_WORLD_PIVOT[1] + bob_y - int(lift_far) - l_piv_fy), rot_leg_f)

        # 3. Torso & Head
        frame.paste(torso_im, (BASE_X, bob_y), torso_im)

        # 4. Near Leg
        rot_leg_n, l_piv_nx, l_piv_ny = rotate_about_pivot(leg_near_im, near_leg_angle, LEG_NEAR_PIVOT)
        frame.paste(rot_leg_n, (BASE_X + LEG_NEAR_WORLD_PIVOT[0] - l_piv_nx, LEG_NEAR_WORLD_PIVOT[1] + bob_y - int(lift_near) - l_piv_ny), rot_leg_n)

        # 5. Near Arm (front)
        rot_arm_n, piv_nx, piv_ny = rotate_about_pivot(arm_im, near_arm_angle, ARM_PIVOT)
        frame.paste(rot_arm_n, (BASE_X + ARM_WORLD_PIVOT[0] - piv_nx, ARM_WORLD_PIVOT[1] + bob_y - piv_ny), rot_arm_n)

        return frame.crop(frame.getbbox())

    print("Generating 12-frame fluid walk cycle...")
    NUM_CYCLE_FRAMES = 12
    hires_cycle = [render_hires_frame(i / NUM_CYCLE_FRAMES) for i in range(NUM_CYCLE_FRAMES)]

    # Downscale walk cycle to target display height with Lanczos for crisp detail
    walk_right = []
    for hf in hires_cycle:
        target_w = int(hf.width * char_h / hf.height)
        scaled = hf.resize((target_w, char_h), Image.LANCZOS)
        walk_right.append(scaled)

    # Left facing walk cycle
    walk_left = [sf.transpose(Image.FLIP_LEFT_RIGHT) for sf in walk_right]

    # Front facing sprite for turning transitions
    front_w = int(front_im.width * char_h / front_im.height)
    front_scaled = front_im.resize((front_w, char_h), Image.LANCZOS)

    # Stage setup
    STAGE_H = char_h + 6 # extra 6px vertical padding
    C_TRANSPARENT = (0, 0, 0, 0)
    START_X = 30
    END_X = stage_w - walk_right[0].width - 30

    frames = []

    # 1. Walk Right across the stage
    x = START_X
    step_idx = 0
    while x < END_X:
        f = Image.new('RGBA', (stage_w, STAGE_H), C_TRANSPARENT)
        sprite = walk_right[step_idx % NUM_CYCLE_FRAMES]
        f.paste(sprite, (int(x), 3), sprite)
        frames.append(f)
        x += speed_px_per_frame
        step_idx += 1

    # 2. Turn at Right End
    # Pause 1 frame standing
    f_stop = Image.new('RGBA', (stage_w, STAGE_H), C_TRANSPARENT)
    f_stop.paste(walk_right[3], (int(END_X), 3), walk_right[3])
    frames.append(f_stop)
    
    # 2 frames facing front
    for _ in range(2):
        f_turn = Image.new('RGBA', (stage_w, STAGE_H), C_TRANSPARENT)
        f_turn.paste(front_scaled, (int(END_X - (front_scaled.width - walk_right[0].width) // 2), 3), front_scaled)
        frames.append(f_turn)

    # 3. Walk Left across the stage
    x = END_X
    step_idx = 0
    while x > START_X:
        f = Image.new('RGBA', (stage_w, STAGE_H), C_TRANSPARENT)
        sprite = walk_left[step_idx % NUM_CYCLE_FRAMES]
        f.paste(sprite, (int(x), 3), sprite)
        frames.append(f)
        x -= speed_px_per_frame
        step_idx += 1

    # 4. Turn at Left End
    # Pause 1 frame standing
    f_stop_l = Image.new('RGBA', (stage_w, STAGE_H), C_TRANSPARENT)
    f_stop_l.paste(walk_left[3], (int(START_X), 3), walk_left[3])
    frames.append(f_stop_l)

    # 2 frames facing front
    for _ in range(2):
        f_turn_l = Image.new('RGBA', (stage_w, STAGE_H), C_TRANSPARENT)
        f_turn_l.paste(front_scaled, (int(START_X - (front_scaled.width - walk_right[0].width) // 2), 3), front_scaled)
        frames.append(f_turn_l)

    print(f"Total animation frames: {len(frames)}")

    # Optimize and convert to indexed palette GIF with transparency
    print("Converting to optimized transparent GIF...")
    palette_frames = []
    for idx, frame in enumerate(frames):
        alpha = frame.split()[3]
        p_frame = frame.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
        p_frame.paste(255, mask)
        p_frame.info['transparency'] = 255
        palette_frames.append(p_frame)

    frame_duration = int(1000 / fps) # ~83ms per frame at 12 fps
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
    print(f"Successfully generated {output_path}: {len(frames)} frames, {size_kb:.1f} KB")

if __name__ == '__main__':
    build_smooth_walking_avatar('assets/walking-avatar.gif')
