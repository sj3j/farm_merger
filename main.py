from item_finder import ImageFinder
from screen_area_selector import ScreenAreaSelector
from merging_points_selector import MergingPointsSelector
import os
import time
import pyautogui
from pynput import keyboard
import numpy as np
import argparse
import math

# =====================================================================
# 🌟 قاموس التتابعات (COLLECT SEQUENCES) 🌟
# هنا تحدد ما هي الأزرار التي يجب الضغط عليها بعد جمع عنصر معين.
# (يجب أن تكون صور الأزرار محفوظة داخل مجلد collect بنفس هذه الأسماء)
# =====================================================================
COLLECT_SEQUENCES = {
    #"check": ["confirm.png"],
    "exclamation": ["make.png","check.png","claim.png","exclamation.png","make.png", "close.png"]
}

# Set up argument parser
parser = argparse.ArgumentParser(description='Farm Merge Clicker')
parser.add_argument('--merge_count', type=int, default=5, help='Number of items to merge')
parser.add_argument('--resize_factor', type=float, help='Resize factor for image recognition (optional)')

args = parser.parse_args()

MERGE_COUNT = args.merge_count
resize_factor = args.resize_factor

print(f"Merge count threshold set to: {MERGE_COUNT}")
print(f"Resize factor set to: {resize_factor}")


def get_screen_area():
    print("-> Setup 1/4: Select the screen area.")
    selector = ScreenAreaSelector()
    return selector.get_coordinates()

def get_anchor_point():
    print("-> Setup 2/4: VISUAL ANCHOR. Click exactly where your Decoration SHOULD be (Target Point).")
    selector = MergingPointsSelector(1)
    pts = selector.get_points()
    return pts[0] if pts else None

def get_merge_points(count):
    print(f"-> Setup 3/4: Click {count} center points for the merging target slots.")
    selector = MergingPointsSelector(count)
    return selector.get_points()

def get_spawner_point():
    print("-> Setup 4/4: Click 1 point to set the Spawner Box location.")
    selector = MergingPointsSelector(1)
    pts = selector.get_points()
    return pts[0] if pts else None

def get_image_file_paths(folder_name='img'):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_folder = os.path.join(base_dir, folder_name)
    
    image_files = []
    if os.path.exists(target_folder):
        for filename in os.listdir(target_folder):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                if 'anchor' not in filename.lower():
                    image_files.append(os.path.join(target_folder, filename))
        image_files.reverse()
    return image_files


# =====================================================================
# 🌟 دالة الجمع التلقائي الذكية (تتعرف على التتابعات) 🌟
# =====================================================================
def perform_auto_collect(start_x, start_y, end_x, end_y, base_dir):
    collect_files = get_image_file_paths('collect')
    if not collect_files:
        print("No images found in 'collect' folder.")
        return False
        
    # جمع أسماء صور الخطوات (مثل confirm.png) لتجاهلها في البحث الأساسي
    sequence_steps = []
    for steps in COLLECT_SEQUENCES.values():
        sequence_steps.extend(steps)
        
    collected_something = False
    
    for collect_img in collect_files:
        base_name = os.path.basename(collect_img).lower()
        
        # تخطي أزرار الخطوات (لا تنقر على confirm العشوائي قبل أن تنقر على العملة)
        if base_name in sequence_steps:
            continue
            
        locs, _ = ImageFinder.find_image_on_screen(
            collect_img, start_x, start_y, end_x, end_y, resize_factor=1.0, threshold=0.75
        )
        
        for loc in locs:
            curr_x, curr_y = loc
            pyautogui.moveTo(curr_x, curr_y)
            pyautogui.mouseDown()
            pyautogui.moveTo(curr_x + 2, curr_y + 2, duration=0.05)
            pyautogui.mouseUp()
            pyautogui.sleep(0.5) # انتظار ظهور النافذة المنبثقة
            collected_something = True
            print(f"[Collect] Picked up: {base_name}")
            
            # فحص ما إذا كان هذا العنصر يحتاج إلى خطوات إضافية (تتابع)
            for key, steps in COLLECT_SEQUENCES.items():
                if key in base_name: # مثلاً إذا كان اسم الملف "coin1.png" فهو يتطابق مع مفتاح "coin"
                    for step_img_name in steps:
                        step_path = os.path.join(base_dir, 'collect', step_img_name)
                        if not os.path.exists(step_path):
                            print(f"[Warning] Missing sequence image: {step_img_name}")
                            continue
                            
                        # البحث عن زر الخطوة (مثل confirm.png) لمدة تصل إلى ثانيتين
                        print(f"   -> Waiting for sequence step: {step_img_name}...")
                        for attempt in range(4): 
                            step_locs, _ = ImageFinder.find_image_on_screen(
                                step_path, start_x, start_y, end_x, end_y, resize_factor=1.0, threshold=0.75
                            )
                            if step_locs:
                                sx, sy = step_locs[0]
                                pyautogui.moveTo(sx, sy)
                                pyautogui.mouseDown()
                                pyautogui.moveTo(sx + 2, sy + 2, duration=0.05)
                                pyautogui.mouseUp()
                                pyautogui.sleep(0.5) # انتظار استجابة الزر
                                print(f"   -> Clicked: {step_img_name}")
                                break
                            pyautogui.sleep(0.5)
                            
    return collected_something


if __name__ == "__main__":
    def on_press(key):
        if key == keyboard.Key.f1:
            print("F1 pressed. Stopping the program.")
            os._exit(0)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    print("==================================")
    print("Press F1 at any time to stop the bot.")
    print("==================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    anchor_img_path = os.path.join(base_dir, 'img', 'anchor.png')
    
    if not os.path.exists(anchor_img_path):
        print("\n[ERROR] 'anchor.png' not found in 'img' folder!")
        print("Please save a screenshot of your decoration as 'anchor.png'.\n")
        os._exit(1)

    # Setup Sequence
    screen_start_x, screen_start_y, screen_end_x, screen_end_y = get_screen_area()
    anchor_target = get_anchor_point()
    clicked_points = get_merge_points(MERGE_COUNT - 1)
    spawner_point = get_spawner_point()

    if not spawner_point or not clicked_points or not anchor_target:
        print("Setup was incomplete. Exiting.")
        os._exit(1)

    if resize_factor is None:
        resize_factor = ImageFinder.find_best_resize_factor((screen_start_x, screen_start_y, screen_end_x, screen_end_y))
    print(f"Using resize factor: {resize_factor}")

    image_files = get_image_file_paths('img')
    
    total_merges_pending = 0
    idle_cycles = 0
    
    center_x = screen_start_x + (screen_end_x - screen_start_x) // 2
    center_y = screen_start_y + (screen_end_y - screen_start_y) // 2
    
    drag_center_y = center_y - 80 
    safe_drag_distance = 120      
    
    bottom_y = drag_center_y + safe_drag_distance
    top_y = drag_center_y - safe_drag_distance

    print("Bot is now running...")
    
    while True:
        # ==========================================================
        # 1. نظام التحقق من المرساة البصرية (Visual Anchor Check)
        # ==========================================================
        anchor_locs, _ = ImageFinder.find_image_on_screen(
            anchor_img_path, screen_start_x, screen_start_y, screen_end_x, screen_end_y, resize_factor, threshold=0.60
        )
        
        if len(anchor_locs) > 0:
            curr_x, curr_y = anchor_locs[0]
            dist = math.hypot(curr_x - anchor_target[0], curr_y - anchor_target[1])
            
            if dist > 45: 
                print("Anchor is visibly shifted. Adjusting map securely...")
                pyautogui.moveTo(curr_x, curr_y)
                pyautogui.mouseDown()
                pyautogui.sleep(0.1) 
                
                pyautogui.moveTo(anchor_target[0], anchor_target[1], duration=0.8)
                
                pyautogui.sleep(0.4) 
                pyautogui.moveRel(2, 0, duration=0.1)  
                pyautogui.moveRel(-2, 0, duration=0.1) 
                pyautogui.sleep(0.4) 
                
                pyautogui.mouseUp()
                pyautogui.sleep(0.5)
        else:
            print("Anchor lost! Initiating Search Protocol (Looking Downwards)...")
            
            pyautogui.moveTo(center_x, top_y)
            pyautogui.mouseDown()
            pyautogui.moveTo(center_x, bottom_y, duration=0.4) 
            pyautogui.mouseUp()
            pyautogui.sleep(1.5)
            
            for attempt in range(10):
                locs, _ = ImageFinder.find_image_on_screen(
                    anchor_img_path, screen_start_x, screen_start_y, screen_end_x, screen_end_y, resize_factor, threshold=0.60
                )
                if len(locs) > 0:
                    print("Anchor found! Re-centering slowly...")
                    curr_x, curr_y = locs[0]
                    pyautogui.moveTo(curr_x, curr_y)
                    pyautogui.mouseDown()
                    pyautogui.sleep(0.1)
                    
                    pyautogui.moveTo(anchor_target[0], anchor_target[1], duration=0.8)
                    
                    pyautogui.sleep(0.4)
                    pyautogui.moveRel(2, 0, duration=0.1)
                    pyautogui.moveRel(-2, 0, duration=0.1)
                    pyautogui.sleep(0.4)
                    
                    pyautogui.mouseUp()
                    pyautogui.sleep(0.5)
                    break
                else:
                    pyautogui.moveTo(center_x, bottom_y)
                    pyautogui.mouseDown()
                    pyautogui.sleep(0.05)
                    pyautogui.moveTo(center_x, top_y, duration=0.8)
                    pyautogui.sleep(0.3) 
                    pyautogui.mouseUp()
                    pyautogui.sleep(0.5)

        # ==========================================================
        # 🌟 الجمع التلقائي 1: قبل الدمج (Pre-Merge Collect) 🌟
        # ==========================================================
        print("--- Pre-Merge Scan ---")
        perform_auto_collect(screen_start_x, screen_start_y, screen_end_x, screen_end_y, base_dir)

        # ==========================================================
        # 2. نظام الدمج الخماسي الأصلي
        # ==========================================================
        merges_this_cycle = 0
        for target_image in image_files:
            template_center_points, modified_screenshot = ImageFinder.find_image_on_screen(
                target_image, screen_start_x, screen_start_y, screen_end_x, screen_end_y, resize_factor
            )
            
            if len(template_center_points) >= MERGE_COUNT and len(clicked_points) >= MERGE_COUNT - 1:
                merges_this_cycle += 1
                for i in range(MERGE_COUNT):
                    start_x, start_y = template_center_points[i]
                    end_x, end_y = clicked_points[i % (MERGE_COUNT - 1)]
                    
                    pyautogui.mouseUp()
                    pyautogui.moveTo(start_x, start_y)
                    pyautogui.mouseDown()
                    pyautogui.moveTo(start_x + 3, start_y + 3, duration=0.05)
                    pyautogui.sleep(0.05)
                    pyautogui.moveTo(end_x, end_y, duration=0.15)
                    pyautogui.mouseUp()
                    pyautogui.sleep(0.1) 
                
                print(f"5-Merge operations completed for {os.path.basename(target_image)}")

        # ==========================================================
        # 3. معالجة التوليد وحالات الطوارئ (Idle/Gridlock)
        # ==========================================================
        if merges_this_cycle > 0:
            total_merges_pending += merges_this_cycle
            idle_cycles = 0 
        else:
            if total_merges_pending > 0:
                # ==========================================================
                # 🌟 الجمع التلقائي 2: بعد الدمج وقبل التوليد (Post-Merge Collect) 🌟
                # ==========================================================
                print("--- Post-Merge Scan ---")
                perform_auto_collect(screen_start_x, screen_start_y, screen_end_x, screen_end_y, base_dir)
                
                clicks_needed = total_merges_pending * 3
                print(f"Spawning {clicks_needed} new items...")
                
                pyautogui.mouseUp()
                for _ in range(clicks_needed):
                    pyautogui.moveTo(spawner_point[0], spawner_point[1])
                    pyautogui.mouseDown()
                    pyautogui.moveTo(spawner_point[0] + 2, spawner_point[1] + 2, duration=0.05) 
                    pyautogui.mouseUp()
                    pyautogui.sleep(0.1)  
                
                pyautogui.sleep(0.5)
                total_merges_pending = 0
                idle_cycles = 0 
            else:
                idle_cycles += 1
                
                if idle_cycles == 2:
                    print("Gridlock detected! Attempting a 3-merge for low-tier items...")
                    performed_emergency_merge = False
                    
                    low_tier_files = [f for f in image_files if '1.' in f.lower() or '2.' in f.lower()]
                    
                    for target_image in low_tier_files:
                        locs, _ = ImageFinder.find_image_on_screen(
                            target_image, screen_start_x, screen_start_y, screen_end_x, screen_end_y, resize_factor
                        )
                        
                        if len(locs) >= 3:
                            print(f"Executing emergency 3-merge for {os.path.basename(target_image)}")
                            for i in range(3):
                                start_x, start_y = locs[i]
                                end_x, end_y = clicked_points[i % 2] 
                                
                                pyautogui.mouseUp()
                                pyautogui.moveTo(start_x, start_y)
                                pyautogui.mouseDown()
                                pyautogui.moveTo(start_x + 3, start_y + 3, duration=0.05)
                                pyautogui.sleep(0.05)
                                pyautogui.moveTo(end_x, end_y, duration=0.15)
                                pyautogui.mouseUp()
                                pyautogui.sleep(0.1)
                                
                            performed_emergency_merge = True
                            total_merges_pending += 1 
                            idle_cycles = 0 
                            break 
                            
                    if not performed_emergency_merge:
                        print("No low-tier 3-merges available. Waiting for crops...")
                        time.sleep(2)
                else:
                    print(f"Waiting for crops to grow... (Idle count: {idle_cycles})")
                    time.sleep(2)