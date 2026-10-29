'''
This is a python project in which the user can play a 1v1 in the same device

Controlles:
Player 1:
     W: jump 
     A: left
     D: right
     S: block
     Q: dash
     F: Kick

Player 2:
     Up-arrow: Jump
     Left-arrow: Left
     Right-arrow: right
     Down-arrow: Block
     Ctrl: Dash
     /: Punch 
     .: Kick
'''

import pygame
import sys
import math
import random
# This init state creates the window, of the pygame.
pygame.init()
pygame.mixer.init()
# =========================
# SETTINGS (controlls all the settings of the game.)
# =========================
WIDTH = 1000
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman FIGHTERRR")
clock = pygame.time.Clock()

# Canvas for screen shake and effects
canvas = pygame.Surface((WIDTH, HEIGHT))

# Load Audio Files
try:
    death_sound = pygame.mixer.Sound(r"..\Sounds\myinstants.mp3")
    alarm_sound = pygame.mixer.Sound(r"..\Sounds\Alarm.mp3")
    dash_sound = pygame.mixer.Sound(r"..\Sounds\Dash.mp3")
    punch_sound = pygame.mixer.Sound(r"..\Sounds\punch.mp3")
    fah_sound = pygame.mixer.Sound(r"..\Sounds\FAHHHH.mp3")
    miss_sound = pygame.mixer.Sound(r"..\Sounds\Miss.mp3")

except pygame.error as e:
    print(f"Warning: Could not load sound files. Error: {e}")
    death_sound = None
    alarm_sound = None
    punch_sound = None
    dash_sound = None
    miss_sound = None

# Fonts
font = pygame.font.SysFont("Arial", 24, bold=True)
combo_font = pygame.font.SysFont("Arial", 32, bold=True)
timer_font = pygame.font.SysFont("Arial", 40, bold=True)
title_font = pygame.font.SysFont("Arial", 72, bold=True)
large_font = pygame.font.SysFont("Arial", 64, bold=True)

# Colors
DARK_GRAY = (40, 40, 40)
MID_GRAY = (80, 80, 80)
LIGHT_GRAY = (130, 130, 130)
GROUND_COLOR = (100, 100, 100)
WHITE = (255, 255, 255)
P1_COLOR = (0, 255, 0)
P2_COLOR = (255, 80, 80)
P1_GHOST = (50, 120, 50)
P2_GHOST = (120, 50, 50)
SPARK_COLOR = (255, 255, 0)
COMBO_COLOR = (255, 215, 0) # Gold

GROUND_Y = 350.0

# =========================
# STICKMAN DRAW ENGINE
# =========================
def draw_stickman(screen, x, y, color, facing_right=True, walk_time=0,
                  is_moving=False, is_jumping=False, velocity_y=0, 
                  attack_type=None, is_dead=False, is_blocking=False): 
    d = 1 if facing_right else -1
    
    if is_dead:
        hx = int(x)
        hy = int(GROUND_Y + 75)
        
        pygame.draw.circle(screen, color, (hx + d * 25, hy), 22, 3)
        pygame.draw.circle(screen, color, (hx + d * 33, hy - 4), 3)
        pygame.draw.line(screen, color, (hx, hy), (hx + d * 60, hy), 4)
        
        pygame.draw.line(screen, color, (hx + d * 10, hy), (hx + d * 5, hy - 25), 4)
        pygame.draw.line(screen, color, (hx + d * 10, hy), (hx + d * 5, hy + 25), 4)
        
        pygame.draw.line(screen, color, (hx + d * 50, hy), (hx + d * 80, hy - 25), 4)
        pygame.draw.line(screen, color, (hx + d * 50, hy), (hx + d * 80, hy + 25), 4)
        return

    t = walk_time
    
    if is_blocking: # Guard pose
        bob = 0
        lean = d * 5
        arm_motion1 = -60
        arm_motion2 = 20
        thigh_f = 0
        thigh_b = 0
        shin_f = 10
        shin_b = 10
    elif is_jumping:
        jump_phase = min(max(velocity_y / 13.0, -1), 1)
        bob = 0
        lean = d * 14
        arm_motion1 = -35 + jump_phase * 20   
        arm_motion2 = 35 - jump_phase * 10
        thigh_f = -30 - jump_phase * 12   
        thigh_b = 30 + jump_phase * 8
        shin_f = -15 + jump_phase * 25   
        shin_b = 20 - jump_phase * 10
    elif is_moving:
        bob = math.sin(t * 3.5) * 10     
        lean = d * 22  
        run_cycle_f = math.sin(t)
        run_cycle_b = math.cos(t)
        arm_motion1 = run_cycle_f * 45
        arm_motion2 = run_cycle_b * 45
        thigh_f = run_cycle_f * 55
        thigh_b = -run_cycle_f * 55
        shin_f = 25 + run_cycle_f * 25
        shin_b = 25 - run_cycle_f * 25
    else:
        bob = 0
        lean = 0
        arm_motion1 = arm_motion2 = 0
        thigh_f = thigh_b = 0
        shin_f = shin_b = 0

    hx = int(x)
    hy = int(y + bob)
    
    shoulder = (hx, hy + 22)
    hip = (hx + lean * 0.5, hy + 88)
    
    if is_jumping and attack_type is not None:
        lean = d * 45
        hip = (hx - d * 25, hy + 50)
        shoulder = (hx + d * 15, hy + 30)

    head_pos = (hx + d * 25, hy + 10) if (is_jumping and attack_type is not None) else (hx, hy)
    pygame.draw.circle(screen, color, head_pos, 22, 3)
    
    eye_x = head_pos[0] + (d * 8)
    eye_y = head_pos[1] - 4
    pygame.draw.circle(screen, color, (eye_x, eye_y), 3)

    pygame.draw.line(screen, color, (head_pos[0], head_pos[1] + 22), shoulder, 3)
    
    spine_mid = (hx + lean * 0.25, hy + 55) if not (is_jumping and attack_type is not None) else (hx, hy + 40)
    pygame.draw.lines(screen, color, False, [shoulder, spine_mid, hip], 4)
    
    sx, sy = shoulder
    
    if is_blocking:
        elbow1 = (sx + d * 15, sy - 15)
        hand1  = (sx + d * 20, sy - 20)
        elbow2 = (sx + d * 25, sy + 30)
        hand2  = (sx + d * 5,  sy + 40)
    elif is_jumping and attack_type is not None:
        elbow1 = (sx - d * 15, sy - 15)
        hand1 = (sx - d * 30, sy - 20)
        elbow2 = (sx - d * 25, sy - 5)
        hand2 = (sx - d * 40, sy - 5)
    elif attack_type == "punch1" and not is_jumping:
        elbow1 = (sx + d * 35, sy + 5)
        hand1 = (sx + d * 65, sy + 5)
        elbow2 = (sx - d * 20, sy + 25)
        hand2 = (sx - d * 30, sy + 45)
    elif attack_type == "punch2" and not is_jumping:
        elbow1 = (sx + d * 40, sy - 10)
        hand1 = (sx + d * 32, sy + 20)
        elbow2 = (sx - d * 25, sy + 15)
        hand2 = (sx - d * 35, sy + 35)
    elif attack_type == "punch3" and not is_jumping:
        elbow1 = (sx + d * 15, sy + 35)
        hand1 = (sx + d * 20, sy - 35)
        elbow2 = (sx - d * 25, sy + 30)
        hand2 = (sx - d * 20, sy + 60)
    elif attack_type == "kick" and not is_jumping:
        elbow1 = (sx - d * 20, sy + 5)
        hand1 = (sx - d * 45, sy + 15)
        elbow2 = (sx - d * 15, sy + 20)
        hand2 = (sx - d * 35, sy + 35)
    else:
        if is_moving:
            elbow1 = (sx + d * (15 + arm_motion1 * 0.15), sy + 25 + abs(arm_motion1)*0.1)
            hand1  = (sx + d * (25 + arm_motion1 * 0.35), sy + 15 + arm_motion1 * 0.25)
            elbow2 = (sx + d * (15 + arm_motion2 * 0.15), sy + 25 + abs(arm_motion2)*0.1)
            hand2  = (sx + d * (25 + arm_motion2 * 0.35), sy + 15 + arm_motion2 * 0.25)
        else:
            elbow1 = (sx + d * 14 + arm_motion1 * 0.25, sy + 20 + abs(arm_motion1)*0.1)
            hand1  = (sx + d * 34 + arm_motion1 * 0.5,  sy + 40)
            elbow2 = (sx - d * 14 + arm_motion2 * 0.25, sy + 20 + abs(arm_motion2)*0.1)
            hand2  = (sx - d * 34 + arm_motion2 * 0.5,  sy + 40)
        
    pygame.draw.lines(screen, color, False, [(sx, sy), elbow1, hand1], 4)
    pygame.draw.lines(screen, color, False, [(sx, sy), elbow2, hand2], 4)
    
    hpx, hpy = int(hip[0]), int(hip[1])
    
    if is_jumping and attack_type is not None:
        knee1x, knee1y = hpx + d * 45, hpy - 10
        foot1x, foot1y = hpx + d * 85, hpy - 15
        knee2x, knee2y = hpx + d * 35, hpy + 5
        foot2x, foot2y = hpx + d * 75, hpy + 5
    elif attack_type == "kick" and not is_jumping:
        knee1x, knee1y = hpx + d * 45, hpy - 30
        foot1x, foot1y = hpx + d * 80, hpy - 45
        knee2x, knee2y = hpx - d * 15, hpy + 25
        foot2x, foot2y = hpx - d * 10, hpy + 56
    else:
        if is_moving:
            knee1x = hpx + d * int(thigh_f * 0.7)
            knee1y = hpy + 28 - int(abs(thigh_f) * 0.1)
            foot1x = knee1x + d * int(shin_f * 0.5)
            foot1y = hpy + 68
            knee2x = hpx + d * int(thigh_b * 0.7)
            knee2y = hpy + 28 - int(abs(thigh_b) * 0.1)
            foot2x = knee2x + d * int(shin_b * 0.5)
            foot2y = hpy + 68
        else:
            knee1x = hpx + d * 16 + int(thigh_f * 0.5)
            knee1y = hpy + 28
            foot1x = knee1x + d * 14 + int(shin_f * 0.5)
            foot1y = hpy + 62
            knee2x = hpx - d * 16 - int(thigh_b * 0.5)
            knee2y = hpy + 28
            foot2x = knee2x - d * 14 - int(shin_b * 0.5)
            foot2y = hpy + 62

    pygame.draw.lines(screen, color, False, [(hpx, hpy), (knee1x, knee1y), (foot1x, foot1y)], 4)
    pygame.draw.line(screen, color, (foot1x, foot1y), (foot1x + d * 12, foot1y), 4)
    pygame.draw.lines(screen, color, False, [(hpx, hpy), (knee2x, knee2y), (foot2x, foot2y)], 4)
    pygame.draw.line(screen, color, (foot2x, foot2y), (foot2x - d * 12, foot2y), 4)

# =========================
# RESET / INITIAL STATE
# =========================
def reset_game():
    return {
        "p1_x": 220.0, "p1_y": GROUND_Y,
        "p2_x": 780.0, "p2_y": GROUND_Y,
        "p1_vel_y": 0.0, "p2_vel_y": 0.0,
        "p1_ground": True, "p2_ground": True,
        "p1_hp": 100, "p2_hp": 100,
        "p1_walk": 0.0, "p2_walk": 0.0,
        "p1_atk_type": None, "p2_atk_type": None, 
        "p1_atk_time": 0, "p2_atk_time": 0,
        "p1_hit": False, "p2_hit": False,
        "p1_combo_step": 0, "p2_combo_step": 0,
        "p1_combo_window": 0, "p2_combo_window": 0,
        "game_timer": 99, "frame_counter": 0,
        "game_over": False, "winner_text": "",
        "sound_played": False,
        "in_menu": True,
        "spark_x": 0, "spark_y": 0, "spark_timer": 0,
        "shake_duration": 0,
        "flash_timer": 0,
        "p1_dash_timer": 0, "p1_dash_dx": 0.0,
        "p2_dash_timer": 0, "p2_dash_dx": 0.0,
        "p1_ghosts": [], "p2_ghosts": [],
        "p1_combo": 0, "p2_combo": 0,
        "p1_combo_timer": 0, "p2_combo_timer": 0,
        "p1_landed_hit": False, "p2_landed_hit": False,
        "p1_prev_atk": None, "p2_prev_atk": None
    }

g = reset_game()

# =========================
# MAIN LOOP
# =========================
alarm_started_time = 0
alarm_stopped = False  
running = True

while running:
    current_time = pygame.time.get_ticks()
    
    if not g["in_menu"] and alarm_started_time == 0:
        alarm_started_time = current_time
        if alarm_sound: 
            alarm_sound.play()

    if alarm_started_time > 0 and not alarm_stopped:
        if current_time - alarm_started_time >= 3000:
            if alarm_sound:
                alarm_sound.stop()
            alarm_stopped = True

    # Check Blocking Inputs continuously
    keys = pygame.key.get_pressed()
    p1_blocking = keys[pygame.K_s] and not g["in_menu"] and not g["game_over"]
    p2_blocking = keys[pygame.K_DOWN] and not g["in_menu"] and not g["game_over"]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                
            if g["in_menu"]:
                if event.key == pygame.K_SPACE:
                    g["in_menu"] = False
            elif g["game_over"]:
                if event.key == pygame.K_SPACE:
                    g = reset_game()
                    alarm_started_time = 0
                    alarm_stopped = False
                elif event.key == pygame.K_ESCAPE:
                    running = False
                
            if not g["in_menu"] and not g["game_over"]:
                # --- Dash Mechanics ---
                if event.key == pygame.K_q and not p1_blocking and g["p1_dash_timer"] == 0:
                    d = 1 if g["p1_x"] < g["p2_x"] else -1
                    g["p1_dash_dx"] = d * 22
                    g["p1_dash_timer"] = 8
                    if dash_sound: dash_sound.play()

                if event.key in (pygame.K_LCTRL, pygame.K_RCTRL) and not p2_blocking and g["p2_dash_timer"] == 0:
                    d = 1 if g["p2_x"] < g["p1_x"] else -1
                    g["p2_dash_dx"] = d * 22
                    g["p2_dash_timer"] = 8
                    if dash_sound: dash_sound.play()

                # --- Player 1 Input Controls ---
                if not p1_blocking and event.key == pygame.K_f and g["p1_atk_type"] is None:
                    if g["p1_combo_window"] > 0:
                        g["p1_combo_step"] = (g["p1_combo_step"] % 3) + 1
                    else:
                        g["p1_combo_step"] = 1
                        
                    if g["p1_combo_step"] == 1:
                        g["p1_atk_type"] = "punch1"
                        g["p1_atk_time"] = 12
                    elif g["p1_combo_step"] == 2:
                        g["p1_atk_type"] = "punch2"
                        g["p1_atk_time"] = 12
                    elif g["p1_combo_step"] == 3:
                        g["p1_atk_type"] = "punch3"
                        g["p1_atk_time"] = 16
                        
                    g["p1_hit"] = False
                    g["p1_landed_hit"] = False
                    g["p1_combo_window"] = 30  
                    
                if not p1_blocking and event.key == pygame.K_g and g["p1_atk_type"] is None:
                    g["p1_atk_type"] = "kick"
                    g["p1_atk_time"] = 16
                    g["p1_hit"] = False
                    g["p1_landed_hit"] = False
                    g["p1_combo_step"] = 0   
                    
                if not p1_blocking and event.key == pygame.K_w and g["p1_ground"]:
                    g["p1_vel_y"] = -13
                    g["p1_ground"] = False
                    
                # --- Player 2 Input Controls ---
                if not p2_blocking and event.key == pygame.K_SLASH and g["p2_atk_type"] is None:
                    if g["p2_combo_window"] > 0:
                        g["p2_combo_step"] = (g["p2_combo_step"] % 3) + 1
                    else:
                        g["p2_combo_step"] = 1
                        
                    if g["p2_combo_step"] == 1:
                        g["p2_atk_type"] = "punch1"
                        g["p2_atk_time"] = 12
                    elif g["p2_combo_step"] == 2:
                        g["p2_atk_type"] = "punch2"
                        g["p2_atk_time"] = 12
                    elif g["p2_combo_step"] == 3:
                        g["p2_atk_type"] = "punch3"
                        g["p2_atk_time"] = 16
                        
                    g["p2_hit"] = False
                    g["p2_landed_hit"] = False
                    g["p2_combo_window"] = 30
                    
                if not p2_blocking and event.key == pygame.K_PERIOD and g["p2_atk_type"] is None:
                    g["p2_atk_type"] = "kick"
                    g["p2_atk_time"] = 16
                    g["p2_hit"] = False
                    g["p2_landed_hit"] = False
                    g["p2_combo_step"] = 0
                    
                if not p2_blocking and event.key == pygame.K_UP and g["p2_ground"]:
                    g["p2_vel_y"] = -13
                    g["p2_ground"] = False

    # Game Loop Physics 
    if not g["in_menu"] and not g["game_over"]:
        p1_moving = False
        p2_moving = False
        
        # P1 Dash logic with ghost trail recording
        if g["p1_dash_timer"] > 0:
            g["p1_x"] += g["p1_dash_dx"]
            g["p1_ghosts"].append((g["p1_x"], g["p1_y"], g["p1_x"] < g["p2_x"]))
            if len(g["p1_ghosts"]) > 5:
                g["p1_ghosts"].pop(0)
            g["p1_dash_timer"] -= 1
        else:
            g["p1_ghosts"].clear()
            if not p1_blocking:
                if keys[pygame.K_a]:
                    g["p1_x"] -= 6
                    g["p1_walk"] += 0.28
                    p1_moving = True
                if keys[pygame.K_d]:
                    g["p1_x"] += 6
                    g["p1_walk"] += 0.28
                    p1_moving = True
            
        # P2 Dash logic with ghost trail recording
        if g["p2_dash_timer"] > 0:
            g["p2_x"] += g["p2_dash_dx"]
            g["p2_ghosts"].append((g["p2_x"], g["p2_y"], g["p2_x"] < g["p1_x"]))
            if len(g["p2_ghosts"]) > 5:
                g["p2_ghosts"].pop(0)
            g["p2_dash_timer"] -= 1
        else:
            g["p2_ghosts"].clear()
            if not p2_blocking:
                if keys[pygame.K_LEFT]:
                    g["p2_x"] -= 6
                    g["p2_walk"] += 0.28
                    p2_moving = True
                if keys[pygame.K_RIGHT]:
                    g["p2_x"] += 6
                    g["p2_walk"] += 0.28
                    p2_moving = True
            
        if not p1_moving: g["p1_walk"] = 0
        if not p2_moving: g["p2_walk"] = 0
        
        g["p1_x"] = max(40, min(g["p1_x"], WIDTH - 40))
        g["p2_x"] = max(40, min(g["p2_x"], WIDTH - 40))

        g["p1_vel_y"] += 1
        g["p1_y"] += g["p1_vel_y"]
        g["p2_vel_y"] += 1
        g["p2_y"] += g["p2_vel_y"]

        if g["p1_y"] >= GROUND_Y:
            g["p1_y"] = GROUND_Y
            g["p1_vel_y"] = 0
            g["p1_ground"] = True
        if g["p2_y"] >= GROUND_Y:
            g["p2_y"] = GROUND_Y
            g["p2_vel_y"] = 0
            g["p2_ground"] = True

        p1_facing_right = g["p1_x"] < g["p2_x"]
        p2_facing_right = g["p2_x"] < g["p1_x"]

        # Track when P1 attack ends to check for Whiff/Miss
        if g["p1_prev_atk"] is not None and g["p1_atk_type"] is None:
            if not g["p1_landed_hit"] and miss_sound:
                miss_sound.play()
        g["p1_prev_atk"] = g["p1_atk_type"]

        if g["p1_atk_type"] is not None:
            g["p1_atk_time"] -= 1
            if g["p1_atk_time"] <= 0: g["p1_atk_type"] = None
        if g["p1_combo_window"] > 0:
            g["p1_combo_window"] -= 1
            if g["p1_combo_window"] <= 0: g["p1_combo_step"] = 0

        # Track when P2 attack ends to check for Whiff/Miss
        if g["p2_prev_atk"] is not None and g["p2_atk_type"] is None:
            if not g["p2_landed_hit"] and miss_sound:
                miss_sound.play()
        g["p2_prev_atk"] = g["p2_atk_type"]
            
        if g["p2_atk_type"] is not None:
            g["p2_atk_time"] -= 1
            if g["p2_atk_time"] <= 0: g["p2_atk_type"] = None
        if g["p2_combo_window"] > 0:
            g["p2_combo_window"] -= 1
            if g["p2_combo_window"] <= 0: g["p2_combo_step"] = 0

        p1_hitbox = pygame.Rect(g["p1_x"] - 25, g["p1_y"] - 10, 50, 150)
        p2_hitbox = pygame.Rect(g["p2_x"] - 25, g["p2_y"] - 10, 50, 150)
        
        p1_attack_box = None
        if g["p1_atk_type"] is not None:
            atk_x = g["p1_x"] + 15 if p1_facing_right else g["p1_x"] - 75
            p1_attack_box = pygame.Rect(atk_x, g["p1_y"] + 10, 60, 35)

        p2_attack_box = None
        if g["p2_atk_type"] is not None:
            atk_x = g["p2_x"] + 15 if p2_facing_right else g["p2_x"] - 75
            p2_attack_box = pygame.Rect(atk_x, g["p2_y"] + 10, 60, 35)

        # Collision with P2 Block Check
        if p1_attack_box and p1_attack_box.colliderect(p2_hitbox) and not g["p1_hit"]:
            g["p1_hit"] = True 
            g["spark_x"] = p1_attack_box.centerx
            g["spark_y"] = p1_attack_box.centery
            g["spark_timer"] = 8
            
            if not p2_blocking:
                if punch_sound: punch_sound.play()
                # Base Damage + Scaled Tiny Bonus Damage based on Combo count (caps at +3)
                base_dmg = 18 if g["p1_atk_type"] == "punch3" else 10
                combo_bonus = min(g["p1_combo"] * 0.2, 3.0)
                damage = int(base_dmg + combo_bonus)
                
                g["p2_hp"] -= damage
                g["p1_landed_hit"] = True
                
                # Combo Increment for P1
                g["p1_combo"] += 1
                g["p1_combo_timer"] = 90  # 1.5 seconds display time
                g["p2_combo"] = 0  # P2 gets hit, P2 combo resets
                
                knock_dir = 1 if p1_facing_right else -1
                g["p2_x"] = max(40, min(g["p2_x"] + knock_dir * 15, WIDTH - 40))
                
                if g["p1_atk_type"] in ["punch3", "kick"]:
                    g["shake_duration"] = 8
                    g["flash_timer"] = 3
            else:
                # If blocked, combo resets
                g["p1_combo"] = 0

        # Collision with P1 Block Check
        if p2_attack_box and p2_attack_box.colliderect(p1_hitbox) and not g["p2_hit"]:
            g["p2_hit"] = True
            g["spark_x"] = p2_attack_box.centerx
            g["spark_y"] = p2_attack_box.centery
            g["spark_timer"] = 8
            
            if not p1_blocking:
                if punch_sound: punch_sound.play()
                # Base Damage + Scaled Tiny Bonus Damage based on Combo count (caps at +3)
                base_dmg = 18 if g["p2_atk_type"] == "punch3" else 10
                combo_bonus = min(g["p2_combo"] * 0.2, 3.0)
                damage = int(base_dmg + combo_bonus)
                
                g["p1_hp"] -= damage
                g["p2_landed_hit"] = True
                
                # Combo Increment for P2
                g["p2_combo"] += 1
                g["p2_combo_timer"] = 90
                g["p1_combo"] = 0  # P1 gets hit, P1 combo resets
                
                knock_dir = 1 if p2_facing_right else -1
                g["p1_x"] = max(40, min(g["p1_x"] + knock_dir * 15, WIDTH - 40))
                
                if g["p2_atk_type"] in ["punch3", "kick"]:
                    g["shake_duration"] = 8
                    g["flash_timer"] = 3
            else:
                # If blocked, combo resets
                g["p2_combo"] = 0

        if g["spark_timer"] > 0:
            g["spark_timer"] -= 1

        # Decrement Combo Timers
        if g["p1_combo_timer"] > 0:
            g["p1_combo_timer"] -= 1
        else:
            g["p1_combo"] = 0

        if g["p2_combo_timer"] > 0:
            g["p2_combo_timer"] -= 1
        else:
            g["p2_combo"] = 0

        g["frame_counter"] += 1
        if g["frame_counter"] >= 60:
            g["frame_counter"] = 0
            g["game_timer"] -= 1

        if g["p1_hp"] <= 0 or g["p2_hp"] <= 0 or g["game_timer"] <= 0:
            g["game_over"] = True
            if g["p1_hp"] == g["p2_hp"]:
                g["winner_text"] = "TIE MATCH!"
            else:
                g["winner_text"] = "PLAYER 1 WINS!" if g["p1_hp"] > g["p2_hp"] else "PLAYER 2 WINS!"

    if g["game_over"] and not g["sound_played"]:
        if death_sound: death_sound.play()
        g["sound_played"] = True

    # =========================
    # RENDER ENGINE
    # =========================
    canvas.fill(DARK_GRAY)

    if g["in_menu"]:
        title_surf = title_font.render("STICKMAN FIGHTERRR", True, WHITE)
        p1_controls = font.render("P1: W (Jump), A/D (Move), Q (Dash), F (Punch), G (Kick), S (Block)", True, P1_COLOR)
        p2_controls = font.render("P2: UP, L/R, CTRL (Dash), / (Punch), . (Kick), DOWN (Block)", True, P2_COLOR)
        start_msg = font.render("Press SPACEBAR to Start Fight", True, WHITE)
        start_msg = font.render("This is a simple stickman game made by Pajwol Adhikari.Press spacebar to Start the game", True, WHITE)
        
        canvas.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 200)))
        canvas.blit(p1_controls, p1_controls.get_rect(center=(WIDTH // 2, 310)))
        canvas.blit(p2_controls, p2_controls.get_rect(center=(WIDTH // 2, 350)))
        canvas.blit(start_msg, start_msg.get_rect(center=(WIDTH // 2, 430)))

    else:
        pygame.draw.rect(canvas, MID_GRAY, (30, 30, 300, 25))
        pygame.draw.rect(canvas, MID_GRAY, (670, 30, 300, 25))
        if g["p1_hp"] > 0:
            pygame.draw.rect(canvas, P1_COLOR, (30, 30, g["p1_hp"] * 3, 25))
        if g["p2_hp"] > 0:
            pygame.draw.rect(canvas, P2_COLOR, (670 + (300 - g["p2_hp"] * 3), 30, g["p2_hp"] * 3, 25))

        canvas.blit(font.render("PLAYER 1", True, WHITE), (30, 65))
        canvas.blit(font.render("PLAYER 2", True, WHITE), (890, 65))
        
        timer_lbl = timer_font.render(f"{max(0, g['game_timer'])}", True, WHITE)
        canvas.blit(timer_lbl, (timer_lbl.get_rect(center=(WIDTH // 2, 45))))

        pygame.draw.rect(canvas, GROUND_COLOR, (0, 500, WIDTH, 100))
        pygame.draw.line(canvas, LIGHT_GRAY, (0, 500), (WIDTH, 500), 3)

        # Render P1 Dash Ghosts
        for gx, gy, g_dir in g["p1_ghosts"]:
            draw_stickman(canvas, gx, gy, P1_GHOST, facing_right=g_dir)
        
        # Render P2 Dash Ghosts
        for gx, gy, g_dir in g["p2_ghosts"]:
            draw_stickman(canvas, gx, gy, P2_GHOST, facing_right=g_dir)

        draw_stickman(
            canvas, g["p1_x"], g["p1_y"], P1_COLOR, facing_right=(g["p1_x"] < g["p2_x"]),
            walk_time=g["p1_walk"], is_moving=(g["p1_walk"] > 0), is_jumping=not g["p1_ground"], 
            velocity_y=g["p1_vel_y"], attack_type=g["p1_atk_type"], is_dead=(g["p1_hp"] <= 0), is_blocking=p1_blocking
        )
        
        draw_stickman(
            canvas, g["p2_x"], g["p2_y"], P2_COLOR, facing_right=(g["p2_x"] < g["p1_x"]),
            walk_time=g["p2_walk"], is_moving=(g["p2_walk"] > 0), is_jumping=not g["p2_ground"], 
            velocity_y=g["p2_vel_y"], attack_type=g["p2_atk_type"], is_dead=(g["p2_hp"] <= 0), is_blocking=p2_blocking
        )

        # Dynamic hit sparks
        if g["spark_timer"] > 0:
            radius = 15 + (8 - g["spark_timer"]) * 1.5
            pygame.draw.circle(canvas, SPARK_COLOR, (int(g["spark_x"]), int(g["spark_y"])), int(radius))
            pygame.draw.circle(canvas, WHITE, (int(g["spark_x"]), int(g["spark_y"])), int(radius / 2))

        # Floating Combo Text (floats above the player taking the hits)
        if g["p1_combo"] > 1:
            p1_combo_surf = combo_font.render(f"COMBO x{g['p1_combo']}", True, COMBO_COLOR)
            canvas.blit(p1_combo_surf, (g["p2_x"] - 50, g["p2_y"] - 110))
        
        if g["p2_combo"] > 1:
            p2_combo_surf = combo_font.render(f"COMBO x{g['p2_combo']}", True, COMBO_COLOR)
            canvas.blit(p2_combo_surf, (g["p1_x"] - 50, g["p1_y"] - 110))

        # Flash on heavy impact
        if g["flash_timer"] > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT))
            flash_surf.fill(WHITE)
            flash_surf.set_alpha(100)
            canvas.blit(flash_surf, (0, 0))
            g["flash_timer"] -= 1

        if g["game_over"]:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            canvas.blit(overlay, (0, 0))
            win_msg = large_font.render(g["winner_text"], True, WHITE)
            rst_msg = font.render("Press SPACEBAR to Play Again or ESC to Quit", True, WHITE)
            canvas.blit(win_msg, win_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
            canvas.blit(rst_msg, rst_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

    # Screen Shake Logic
    shake_x, shake_y = 0, 0
    if g["shake_duration"] > 0:
        shake_x = random.randint(-8, 8)
        shake_y = random.randint(-8, 8)
        g["shake_duration"] -= 1

    screen.blit(canvas, (shake_x, shake_y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()