import cv2
import numpy as np
import os
import time
import mss

class TemplateCapturer:
    def __init__(self):
        self.sct = mss.mss()
        # Capture the primary monitor for templates
        self.monitor = self.sct.monitors[1] 
        
        self.roi_start = None
        self.roi_end = None
        self.drawing = False
        
        self.state = "DRAWING" 
        self.current_screen = None
        
    def mouse_callback(self, event, x, y, flags, param):
        if self.state != "DRAWING":
            return

        if event == cv2.EVENT_LBUTTONDOWN:
            self.roi_start = (x, y)
            self.roi_end = (x, y)
            self.drawing = True
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.roi_end = (x, y)
                
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.roi_end = (x, y)
                self.drawing = False
                
                if self.roi_start and self.roi_end:
                    x1, y1 = self.roi_start
                    x2, y2 = self.roi_end
                    # 🌟 التعديل هنا: تم تغيير 20 إلى 5 للسماح بالقصات الصغيرة جداً 🌟
                    if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:
                        print("\n🛑 Box drawn! Check the console to name your item.")
                        self.state = "WAITING_INPUT"
                    else:
                        print("⚠️ Box was too small! Try drawing a slightly bigger one.")
                        self.roi_start = None
                        self.roi_end = Nonecolgo

    def capture_screen(self) -> np.ndarray:
        """Captures the primary monitor using mss."""
        img = np.array(self.sct.grab(self.monitor))
        return img[:, :, :3]

    def run(self):
        print("📸 AI Template Capturer Started.")
        print("⏳ Please open your game and make sure the item you want is visible.")
        
        # 5-Second Countdown
        for i in range(5, 0, -1):
            print(f"Capturing screenshot in {i}...")
            time.sleep(1)
            
        print("📸 SNAP! Screenshot captured.")
        self.current_screen = self.capture_screen()
        
        print("\n" + "="*50)
        print("INSTRUCTIONS:")
        print("1. Draw a box around the item in the image window.")
        print("2. Release the mouse, then look at THIS console to name it.")
        print("3. Press 'r' on your keyboard to RETAKE the screenshot.")
        print("4. Press 'q' on your keyboard to QUIT.")
        print("="*50 + "\n")
        
        # WINDOW_NORMAL allows you to resize the window if your screen is 4K/1440p
        cv2.namedWindow("Template Capturer", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Template Capturer", self.mouse_callback)
        
        while True:
            if self.current_screen is None:
                break
                
            display_img = self.current_screen.copy()
            
            # Draw the ROI
            if self.roi_start and self.roi_end:
                color = (0, 255, 0) if self.state == "DRAWING" else (0, 0, 255) 
                cv2.rectangle(display_img, self.roi_start, self.roi_end, color, 2)
                
            cv2.imshow("Template Capturer", display_img)
            key = cv2.waitKey(20) & 0xFF 
            
            if key == ord('q'):
                print("👋 Quitting capturer.")
                break
            elif key == ord('r'):
                print("🔄 Retaking screenshot in 3 seconds... Switch to game!")
                time.sleep(3)
                self.current_screen = self.capture_screen()
                self._reset_state()
                print("📸 SNAP! New screenshot captured.\n")
                
            if self.state == "WAITING_INPUT":
                self._handle_input()
                
        cv2.destroyAllWindows()

    def _handle_input(self):
        print("\n" + "="*40)
        print("*(Note: The image window might say 'Not Responding' while you type here. This is normal!)*")
        name = input("👉 Enter base name (e.g., 'weaht'): ").strip().lower()
        tier = input("👉 Enter tier (1, 2, or 3): ").strip()
        print("="*40 + "\n")
        
        if not name or tier not in ['1', '2', '3']:
            print("❌ Invalid input. Cancelling capture. Draw a new box.")
            self._reset_state()
            return
            
        self.state = "PROCESSING"
        self._process_and_save(name, tier)
        self._reset_state()

    def _reset_state(self):
        self.state = "DRAWING"
        self.roi_start = None
        self.roi_end = None
        self.drawing = False
        print("✅ Ready for next box! (Draw on the image or press 'r' for a new screenshot)\n")

    def _process_and_save(self, name, tier):
        x1, y1 = self.roi_start
        x2, y2 = self.roi_end
        x_min, x_max = sorted([x1, x2])
        y_min, y_max = sorted([y1, y2])
        
        # أخذ المربع المقصوص بالضبط كما رسمته (بدون إزالة الخلفية لتجنب بكسلات اللون الأسود)
        final_img = self.current_screen[y_min:y_max, x_min:x_max]
        
        filename = f"{name}.png" if tier == "1" else f"{name}{tier}.png"
        
        # إصلاح دمج المسارات لتجنب مشاكل علامة (\)
        save_path = os.path.join("collect", filename)
        
        cv2.imwrite(save_path, final_img)
        print(f"✅ Saved exact template to: {save_path}")

if __name__ == "__main__":
    if not os.path.exists("collect"):
        os.makedirs("collect")
    capturer = TemplateCapturer()
    capturer.run()