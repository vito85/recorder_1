import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
import time
from datetime import datetime
import os
import pygrabber.dshow_graph as dshow

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("4K Pro Recorder - Razer Kiyo (Focus Control)")
        self.geometry("900x850") 
        ctk.set_appearance_mode("dark")

        self.recording = False
        self.out = None
        self.cap = None
        self.update_running = False

        # --- UI ԷԼԵՄԵՆՏՆԵՐ ---
        self.label = ctk.CTkLabel(self, text="4K Video Recorder", font=("Helvetica", 20, "bold"))
        self.label.pack(pady=5)

        self.preview_label = ctk.CTkLabel(self, text="Որոնում...", fg_color="black", width=640, height=360)
        self.preview_label.pack(pady=5)

        # Settings Frame
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, fill="x", padx=20)

        # 1. Տեսախցիկի ընտրություն
        self.cameras = self.get_camera_list()
        default_cam = self.cameras[-1] if self.cameras else "No Device"
        for cam in self.cameras:
            if "Razer" in cam or "Kiyo" in cam:
                default_cam = cam
                break

        self.cam_menu = ctk.CTkOptionMenu(self.settings_frame, values=self.cameras if self.cameras else ["No Device"], 
                                         command=self.change_camera)
        self.cam_menu.set(default_cam)
        self.cam_menu.grid(row=0, column=0, padx=10, pady=10)

        # 2. Ֆորմատի ընտրություն
        self.format_var = ctk.StringVar(value="MP4")
        self.format_menu = ctk.CTkOptionMenu(self.settings_frame, values=["MP4", "AVI", "MKV"], variable=self.format_var, width=80)
        self.format_menu.grid(row=0, column=1, padx=10)

        # 3. ԱՎՏՈՖՈԿՈՒՍԻ ԱՆՋԱՏԻՉ (ՆՈՐ)
        self.af_var = ctk.BooleanVar(value=True) # Դիֆոլտ միացված
        self.af_switch = ctk.CTkSwitch(self.settings_frame, text="Auto Focus", 
                                       variable=self.af_var, command=self.toggle_autofocus)
        self.af_switch.grid(row=0, column=2, padx=10)

        # 4. Ժամանակի անջատիչ
        self.overlay_var = ctk.BooleanVar(value=True)
        self.overlay_switch = ctk.CTkSwitch(self.settings_frame, text="Time", variable=self.overlay_var)
        self.overlay_switch.grid(row=0, column=3, padx=10)

        self.timer_label = ctk.CTkLabel(self, text="00:00:00", font=("Consolas", 35, "bold"), text_color="#e74c3c")
        self.timer_label.pack(pady=5)

        # Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.start_button = ctk.CTkButton(self.btn_frame, text="START", command=self.start_recording, fg_color="#2ecc71", width=180, height=45)
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = ctk.CTkButton(self.btn_frame, text="STOP", command=self.stop_recording, state="disabled", fg_color="#e74c3c", width=180, height=45)
        self.stop_button.grid(row=0, column=1, padx=10)

        self.change_camera(default_cam)

    def get_camera_list(self):
        try:
            return [device for device in dshow.FilterGraph().get_input_devices()]
        except:
            return ["Camera 0"]

    def toggle_autofocus(self):
        if self.cap and self.cap.isOpened():
            val = 1 if self.af_var.get() else 0
            # Փորձում ենք փոխել ապարատային ավտոֆոկուսը
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, val)
            status = "Միացված" if val == 1 else "Անջատված"
            print(f"Autofocus: {status}")

    def change_camera(self, choice):
        if self.cap is not None:
            self.cap.release()
            time.sleep(0.5)

        cam_index = self.cameras.index(choice) if choice in self.cameras else 0
        self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        
        # Կարգավորումներ Razer-ի համար
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        # Միացնում ենք ավտոֆոկուսը դիֆոլտ
        self.toggle_autofocus()

        if not self.update_running:
            self.update_running = True
            self.update_frame()

    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                if self.recording and self.out:
                    if self.overlay_var.get():
                        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        cv2.putText(frame, now, (50, 2100), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 4)
                    self.out.write(frame)
                    elapsed = int(time.time() - self.start_time)
                    self.timer_label.configure(text=time.strftime('%H:%M:%S', time.gmtime(elapsed)))

                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((640, 360))
                imgtk = ImageTk.PhotoImage(image=img)
                self.preview_label.configure(image=imgtk, text="")
                self.preview_label.image = imgtk
        self.after(15, self.update_frame)

    def start_recording(self):
        self.recording = True
        self.start_time = time.time()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        
        fmt = self.format_var.get()
        codec, ext = ('mp4v', 'mp4') if fmt == "MP4" else (('XVID', 'avi') if fmt == "AVI" else ('XVID', 'mkv'))
        
        self.out = cv2.VideoWriter(f"REC_4K_{int(self.start_time)}.{ext}", cv2.VideoWriter_fourcc(*codec), 30.0, (3840, 2160))

    def stop_recording(self):
        self.recording = False
        if self.out: self.out.release()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        os.startfile(os.getcwd())

if __name__ == "__main__":
    app = App()
    app.mainloop()