# import cv2
# import customtkinter as ctk
# from PIL import Image, ImageTk
# import time
# from datetime import datetime
# import os
# import threading
# import pygrabber.dshow_graph as dshow

# class App(ctk.CTk):
#     def __init__(self):
#         super().__init__()

#         self.title("4K Pro Recorder - Razer Kiyo (Focus Control)")
#         self.geometry("900x850") 
#         ctk.set_appearance_mode("dark")

#         self.recording = False
#         self.out = None
#         self.cap = None
#         self.update_running = False
#         self.last_frame = None 

#         # --- UI ԷԼԵՄԵՆՏՆԵՐ ---
#         self.label = ctk.CTkLabel(self, text="4K Video Recorder", font=("Helvetica", 20, "bold"))
#         self.label.pack(pady=5)

#         self.preview_label = ctk.CTkLabel(self, text="Որոնում...", fg_color="black", width=640, height=360)
#         self.preview_label.pack(pady=5)

#         self.settings_frame = ctk.CTkFrame(self)
#         self.settings_frame.pack(pady=10, fill="x", padx=20)

#         self.cameras = self.get_camera_list()
#         default_cam = self.cameras[-1] if self.cameras else "No Device"
#         for cam in self.cameras:
#             if "Razer" in cam or "Kiyo" in cam:
#                 default_cam = cam
#                 break

#         self.cam_menu = ctk.CTkOptionMenu(self.settings_frame, values=self.cameras if self.cameras else ["No Device"], 
#                                          command=self.change_camera)
#         self.cam_menu.set(default_cam)
#         self.cam_menu.grid(row=0, column=0, padx=10, pady=10)

#         self.format_var = ctk.StringVar(value="MP4")
#         self.format_menu = ctk.CTkOptionMenu(self.settings_frame, values=["MP4", "AVI", "MKV"], variable=self.format_var, width=80)
#         self.format_menu.grid(row=0, column=1, padx=10)

#         self.af_var = ctk.BooleanVar(value=True) 
#         self.af_switch = ctk.CTkSwitch(self.settings_frame, text="Auto Focus", variable=self.af_var, command=self.toggle_autofocus)
#         self.af_switch.grid(row=0, column=2, padx=10)

#         self.overlay_var = ctk.BooleanVar(value=True)
#         self.overlay_switch = ctk.CTkSwitch(self.settings_frame, text="Time", variable=self.overlay_var)
#         self.overlay_switch.grid(row=0, column=3, padx=10)

#         self.timer_label = ctk.CTkLabel(self, text="00:00:00", font=("Consolas", 35, "bold"), text_color="#e74c3c")
#         self.timer_label.pack(pady=5)

#         self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
#         self.btn_frame.pack(pady=10)

#         self.start_button = ctk.CTkButton(self.btn_frame, text="START", command=self.start_recording, fg_color="#2ecc71", width=180, height=45)
#         self.start_button.grid(row=0, column=0, padx=10)

#         self.stop_button = ctk.CTkButton(self.btn_frame, text="STOP", command=self.stop_recording, state="disabled", fg_color="#e74c3c", width=180, height=45)
#         self.stop_button.grid(row=0, column=1, padx=10)

#         self.change_camera(default_cam)

#     def get_camera_list(self):
#         try: return [device for device in dshow.FilterGraph().get_input_devices()]
#         except: return ["Camera 0"]

#     def toggle_autofocus(self):
#         if self.cap and self.cap.isOpened():
#             self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1 if self.af_var.get() else 0)

#     def change_camera(self, choice):
#         if self.cap: self.cap.release()
#         time.sleep(0.5)
#         cam_index = self.cameras.index(choice) if choice in self.cameras else 0
#         self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        
#         # Razer Ultra 4K Settings
#         self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
#         self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
#         self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
#         self.toggle_autofocus()

#         if not self.update_running:
#             self.update_running = True
#             self.update_frame()

#     def update_frame(self):
#         if self.cap and self.cap.isOpened():
#             ret, frame = self.cap.read()
#             if ret:
#                 self.last_frame = frame
#                 if self.recording:
#                     elapsed = int(time.time() - self.start_time)
#                     self.timer_label.configure(text=time.strftime('%H:%M:%S', time.gmtime(elapsed)))

#                 img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((640, 360))
#                 imgtk = ImageTk.PhotoImage(image=img)
#                 self.preview_label.configure(image=imgtk, text="")
#                 self.preview_label.image = imgtk
#         self.after(10, self.update_frame)

#     def record_worker(self):
#         while self.recording:
#             if self.last_frame is not None:
#                 f = self.last_frame.copy()
#                 if self.overlay_var.get():
#                     cv2.putText(f, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), (50, f.shape[0]-100), 
#                                 cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 4)
#                 self.out.write(f)
#                 time.sleep(0.033) # 30 FPS

#     def start_recording(self):
#         # Ստանում ենք իրական չափսերը, որոնք տալիս է Razer-ը տվյալ պահին
#         actual_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         actual_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
#         timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         fmt = self.format_var.get()
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v') if fmt == "MP4" else cv2.VideoWriter_fourcc(*'XVID')
#         ext = fmt.lower()

#         filename = f"REC_{timestamp}.{ext}"
#         # Օգտագործում ենք իրական (actual) չափսերը 0 կբ-ից խուսափելու համար
#         self.out = cv2.VideoWriter(filename, fourcc, 30.0, (actual_w, actual_h))
        
#         if self.out.isOpened():
#             self.recording = True
#             self.start_time = time.time()
#             self.start_button.configure(state="disabled")
#             self.stop_button.configure(state="normal")
#             threading.Thread(target=self.record_worker, daemon=True).start()

#     def stop_recording(self):
#         self.recording = False
#         time.sleep(0.3)
#         if self.out: self.out.release()
#         self.out = None
#         self.start_button.configure(state="normal")
#         self.stop_button.configure(state="disabled")
#         os.startfile(os.getcwd())

# if __name__ == "__main__":
#     app = App()
#     app.protocol("WM_DELETE_WINDOW", lambda: (app.stop_recording(), app.destroy()))
#     app.mainloop()



# 4K Force կոդը
import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
import time
from datetime import datetime
import os
import threading
import pygrabber.dshow_graph as dshow

class VideoRecorderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Razer Kiyo Pro Ultra - TRUE 4K")
        self.geometry("900x850") 
        ctk.set_appearance_mode("dark")

        self.recording = False
        self.out = None
        self.cap = None
        self.update_running = False
        self.last_frame = None 

        self.setup_ui()
        self.init_camera()

    def setup_ui(self):
        self.label = ctk.CTkLabel(self, text="TRUE 4K Video Recorder", font=("Helvetica", 22, "bold"))
        self.label.pack(pady=10)

        self.preview_label = ctk.CTkLabel(self, text="Միացում...", fg_color="black", width=640, height=360)
        self.preview_label.pack(pady=5)

        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, fill="x", padx=20)

        self.cameras = self.get_camera_list()
        default_cam = next((c for c in self.cameras if "Razer" in c or "Kiyo" in c), self.cameras[-1] if self.cameras else "No Device")

        self.cam_menu = ctk.CTkOptionMenu(self.settings_frame, values=self.cameras, command=self.change_camera)
        self.cam_menu.set(default_cam)
        self.cam_menu.grid(row=0, column=0, padx=10, pady=10)

        self.format_var = ctk.StringVar(value="MP4")
        self.format_menu = ctk.CTkOptionMenu(self.settings_frame, values=["MP4", "AVI"], variable=self.format_var, width=80)
        self.format_menu.grid(row=0, column=1, padx=10)

        self.af_var = ctk.BooleanVar(value=True) 
        self.af_switch = ctk.CTkSwitch(self.settings_frame, text="Auto Focus", variable=self.af_var, command=self.toggle_autofocus)
        self.af_switch.grid(row=0, column=2, padx=10)

        self.timer_label = ctk.CTkLabel(self, text="00:00:00", font=("Consolas", 35, "bold"), text_color="#e74c3c")
        self.timer_label.pack(pady=10)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.start_button = ctk.CTkButton(self.btn_frame, text="START 4K", command=self.start_recording, fg_color="#2ecc71", width=180, height=50)
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = ctk.CTkButton(self.btn_frame, text="STOP", command=self.stop_recording, state="disabled", fg_color="#e74c3c", width=180, height=50)
        self.stop_button.grid(row=0, column=1, padx=10)

    def get_camera_list(self):
        try: return [device for device in dshow.FilterGraph().get_input_devices()]
        except: return ["Camera 0"]

    def init_camera(self):
        self.change_camera(self.cam_menu.get())

    def toggle_autofocus(self):
        if self.cap: self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1 if self.af_var.get() else 0)

    def change_camera(self, choice):
        if self.cap: self.cap.release()
        idx = self.cameras.index(choice) if choice in self.cameras else 0
        
        # Օգտագործում ենք MSMF (Microsoft Media Foundation) ավելի լավ 4K աջակցության համար
        self.cap = cv2.VideoCapture(idx, cv2.CAP_MSMF)
        
        # ԿԱՐԵՎՈՐ։ Սկզբից սահմանում ենք ֆորմատը, հետո չափսերը
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Ստուգում ենք՝ արդյոք տեսախցիկը ընդունեց 4K-ն
        w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Կարգավորված որակը: {w}x{h}")
        
        self.toggle_autofocus()

        if not self.update_running:
            self.update_running = True
            self.update_frame()

    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.last_frame = frame
                if self.recording:
                    elapsed = int(time.time() - self.start_time)
                    self.timer_label.configure(text=time.strftime('%H:%M:%S', time.gmtime(elapsed)))

                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((640, 360))
                imgtk = ImageTk.PhotoImage(image=img)
                self.preview_label.configure(image=imgtk, text="")
                self.preview_label.image = imgtk
        self.after(10, self.update_frame)

    def record_loop(self):
        while self.recording:
            if self.last_frame is not None:
                self.out.write(self.last_frame)
                time.sleep(1/31)

    def start_recording(self):
        # ՍՏԻՊՈՂԱԿԱՆ վերցնում ենք այն, ինչ տալիս է սենսորը
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if w < 3840:
            print(f"ԶԳՈՒՇԱՑՈՒՄ: Տեսախցիկը աշխատում է {w}x{h} որակով, ոչ թե 4K:")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fmt = self.format_var.get()
        fourcc = cv2.VideoWriter_fourcc(*('mp4v' if fmt == "MP4" else 'XVID'))
        
        self.out = cv2.VideoWriter(f"REC_{timestamp}.{fmt.lower()}", fourcc, 30.0, (w, h))
        
        if self.out.isOpened():
            self.recording = True
            self.start_time = time.time()
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            threading.Thread(target=self.record_loop, daemon=True).start()

    def stop_recording(self):
        self.recording = False
        time.sleep(0.3)
        if self.out: self.out.release()
        self.out = None
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        os.startfile(os.getcwd())

if __name__ == "__main__":
    app = VideoRecorderApp()
    app.mainloop()