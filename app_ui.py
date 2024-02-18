import tkinter as tk
from tkinter import ttk
import sv_ttk

class UIManager:
    def __init__(self, configManager, controlManager):
        self.configManager = configManager
        self.controlManager = controlManager

        self.image_model_list = self.configManager.get_config("image_model_list")
        self.text_model_list = self.configManager.get_config("text_model_list") 
        self.audio_model_list = self.configManager.get_config("audio_model_list")
        self.image_quality_list = self.configManager.get_config("image_quality_list")

        self.agent_elements = {
            "LIVE SUMMARY SETTINGS": [
                {"type": "label", "text": "LOOP TIME IN MIN"},
                {"type": "slider", "from": 0, "to": 60, "orient": tk.HORIZONTAL, "key": "agent_livesummary_loop_time_in_min"},
                {"type": "label", "text": "TEXT MODEL"},
                {"type": "combobox", "values": self.text_model_list , "key": "agent_livesummary_text_model"},
                {"type": "checkbutton", "text": "ENABLED", "key": "agent_livesummary_enabled"}
            ],
            "FEATURE #2 SETTINGS": [
                {"type": "label", "text": "LOOP TIME IN MIN"},
                {"type": "slider", "from": 0, "to": 60, "orient": tk.HORIZONTAL, "key": "agent_feature2_loop_time_in_min"},
                {"type": "label", "text": "TEXT MODEL"},
                {"type": "combobox", "values": self.text_model_list , "key": "agent_feature2_text_model"},
                {"type": "checkbutton", "text": "ENABLED", "key": "agent_feature2_enabled"}
            ],
        }
        self.all_elements = {
            "MODEL SETTINGS": [
                {"type": "label", "text": "OPENAI API KEY"},
                {"type": "entry", "key": "openai_api_key"},
                {"type": "label", "text": "TOGETHER API KEY"},
                {"type": "entry", "key": "together_api_key"},
                {"type": "label", "text": "DEEPGRAM API KEY"},
                {"type": "entry", "key": "deepgram_api_key"},
            ],
            "SCREENSHOT SETTINGS": [
                {"type": "label", "text": "LOOP TIME IN MIN"},
                {"type": "slider", "from": 0, "to": 60, "orient": tk.HORIZONTAL, "key": "screenshot_loop_time_in_min"},
                {"type": "label", "text": "TEXT MODEL"},
                {"type": "combobox", "values": self.text_model_list , "key": "screenshot_text_model"},
                {"type": "label", "text": "COMPRESSION %"},
                {"type": "slider", "from": 0, "to": 100, "orient": tk.HORIZONTAL, "key": "screenshot_compression_perc"},
                {"type": "checkbutton", "text": "ENABLED", "key": "screenshot_enabled"}
            ],
            "PHOTO SETTINGS": [
                {"type": "label", "text": "LOOP TIME IN MIN"},
                {"type": "slider", "from": 0, "to": 60, "orient": tk.HORIZONTAL, "key": "photo_loop_time_in_min"},
                {"type": "label", "text": "VISION MODEL"},
                {"type": "combobox", "values": self.text_model_list , "key": "photo_image_model"},
                {"type": "label", "text": "MODEL IMAGE QUALITY"},
                {"type": "combobox", "values": self.image_quality_list, "key": "photo_image_quality_val"},
                {"type": "label", "text": "COMPRESSION %"},
                {"type": "slider", "from": 0, "to": 100, "orient": tk.HORIZONTAL, "key": "photo_compression_perc"},
                {"type": "checkbutton", "text": "ENABLED", "key": "photo_enabled"}
            ],
            "AUDIO SETTINGS": [
                {"type": "label", "text": "LOOP TIME IN MIN"},
                {"type": "slider", "from": 0, "to": 60, "orient": tk.HORIZONTAL, "key": "audio_loop_time_in_min"},
                {"type": "label", "text": "AUDIO MODEL"},
                {"type": "combobox", "values": self.audio_model_list, "key": "audio_audio_model"},
                {"type": "label", "text": "COMPRESSION %"},
                {"type": "slider", "from": 0, "to": 100, "orient": tk.HORIZONTAL, "key": "audio_compression_perc"},
                {"type": "checkbutton", "text": "ENABLED", "key": "audio_enabled"}
            ],
            "AGENT SETTINGS": [
                {"type": "checkbutton", "text": "LIVE SUMMARY", "key": "agent_livesummary_enabled"},
                {"type": "button", "text": "Open New Window", "command": lambda: self.open_new_window("LIVE SUMMARY SETTINGS")},
                {"type": "checkbutton", "text": "FEATURE #2", "key": "agent_feature2_enabled"},
                {"type": "button", "text": "Open New Window", "command": lambda: self.open_new_window("FEATURE #2 SETTINGS")},
            ],
        }
        
        self.root = tk.Tk()
        self.root.title("EYES")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.main_frame = ttk.Frame(self.root, padding=(10, 10, 10, 10))
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.create_general_frames()
        self.create_button_frames()

        sv_ttk.set_theme("dark")

    def create_general_frames(self):
        frames = {}
        for title, elements in self.all_elements.items():
            frames[title] = self.create_settings_frame(self.main_frame, title, elements)
            frames[title].pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    def create_button_frames(self):
        button_frame = ttk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, padx=5, pady=5, fill=tk.X)

        start_button = ttk.Button(button_frame, text="START", command=self.start_action)
        stop_button = ttk.Button(button_frame, text="STOP", command=self.stop_action)

        start_button.pack(side=tk.LEFT, padx=(0, 5), pady=5, fill=tk.X, expand=True)
        stop_button.pack(side=tk.LEFT, padx=(5, 0), pady=5, fill=tk.X, expand=True)

    def create_settings_frame(self, parent, title, elements):
        frame = ttk.LabelFrame(parent, text=title, padding=(10, 10, 10, 10))
        
        for element in elements:
            if element["type"] == "label":
                label = ttk.Label(frame, text=element["text"])
                label.pack(fill=tk.X, padx=5, pady=5)
            elif element["type"] == "button":
                button = ttk.Button(frame, text=element["text"], command=element["command"])
                button.pack(fill=tk.X, padx=5, pady=5)
            
            elif element["type"] == "entry":
                default_value = self.configManager.get_config(element["key"])

                entry = ttk.Entry(frame)
                entry.pack(fill=tk.X, padx=5, pady=5)
                entry.insert(0, default_value)
                entry.bind("<Return>", lambda event, key=element["key"]: self.entry_enter(event, key))
                entry.bind('<FocusOut>', lambda event, key=element["key"]: self.entry_enter(event, key))
            elif element["type"] == "checkbutton":
                default_bool_value = self.configManager.get_config(element["key"])
                var = tk.BooleanVar(value=default_bool_value)

                checkbutton = ttk.Checkbutton(frame, text=element["text"], variable=var, onvalue=True, offvalue=False)
                checkbutton.var = var 
                checkbutton.pack(fill=tk.X, padx=5, pady=5)
                checkbutton.bind("<Button-1>", lambda event, key=element["key"]: self.checkbutton_clicked(event, key))
            elif element["type"] == "combobox":
                default_value = self.configManager.get_config(element["key"])

                combobox = ttk.Combobox(frame, values=element["values"])
                combobox.set(default_value) 
                combobox.pack(fill=tk.X, padx=5, pady=5)
                combobox.bind("<<ComboboxSelected>>", lambda event, key=element["key"]: self.combobox_selected(event, key))
            elif element["type"] == "slider":
                default_value = self.configManager.get_config(element["key"])

                slider_frame = ttk.Frame(frame)
                slider_frame.pack(fill=tk.X, expand=True)
                
                value_label = ttk.Label(slider_frame, text=str(default_value))
                value_label.pack(side=tk.RIGHT, padx=(10, 0))

                slider = ttk.Scale(slider_frame, from_=element["from"], to=element["to"], orient=element["orient"])
                slider.pack(fill=tk.X)
                slider.set(default_value) 
                
                slider.bind("<ButtonRelease-1>", lambda event, label=value_label, key=element["key"]: self.scale_changed(event, label, key))
        
        return frame
    
    def run(self):
        self.root.mainloop()

    def start_action(self):
        print("Start action triggered")
    def stop_action(self):
        print("Stop action triggered")
    
    def on_closing(self):
        print("Closing application...")
        if self.controlManager.is_running():
            # FIXME: See how to trigger this in app.py from here
            stop_primary_process()
        self.root.destroy()

    def entry_enter(self, event, key):
        entry_new_val = event.widget.get()
        self.configManager.save_config(key, entry_new_val)
        print(f"Entry entered\n{key} - {entry_new_val}")
    def combobox_selected(self, event, key):
        entry_new_val = event.widget.get()
        self.configManager.save_config(key, entry_new_val)
        print(f"Combobox selected\n{key} - {entry_new_val}")
    def checkbutton_clicked(self, event, key):
        var = event.widget.var
        entry_new_val = not var.get()
        self.configManager.save_config(key, entry_new_val)
        print(f"Checkbutton selected\n{key} - {entry_new_val}")
    def scale_changed(self, event, value_label, key):
        slider = event.widget
        value = int(slider.get())
        value_label.config(text=str(value))
        self.configManager.save_config(key, value)
        print("Scale changed:", value)

    def open_new_window(self, window_title):
        new_window = tk.Toplevel(self.root)
        new_window.title(window_title)
        new_window.geometry("400x250")

        main_frame = ttk.Frame(new_window, padding=(10, 10, 10, 10))
        main_frame.pack(expand=True, fill=tk.BOTH)

        frames = {}
        for title, elements in self.agent_elements.items():
            if window_title == title:
                frames[title] = self.create_settings_frame(new_window, title, elements)
                frames[title].pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, padx=5, pady=5, fill=tk.X)

        start_button = ttk.Button(button_frame, text="DONE", command=self.start_action)
        stop_button = ttk.Button(button_frame, text="CANCEL", command=self.stop_action)

        start_button.pack(side=tk.LEFT, padx=(0, 5), pady=5, fill=tk.X, expand=True)
        stop_button.pack(side=tk.LEFT, padx=(5, 0), pady=5, fill=tk.X, expand=True)