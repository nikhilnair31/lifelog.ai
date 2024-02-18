import tkinter as tk
from tkinter import ttk
import sv_ttk

class UIManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EYES")

        self.main_frame = ttk.Frame(self.root, padding=(10, 10, 10, 10))
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        self.additional_elements = {
            "ADDITIONAL SETTINGS": [
                {"type": "label", "text": "LOOP TIME IN MIN"},
                {"type": "slider", "from": 0, "to": 60, "orient": tk.HORIZONTAL, "command": self.scale_changed},
                {"type": "label", "text": "TEXT MODEL"},
                {"type": "combobox", "values": ["Option 1", "Option 2", "Option 3"], "default_value": "Option 1", "command": self.combobox_selected},
                {"type": "checkbutton", "text": "ENABLED", "command": self.checkbutton_clicked}
            ]
        }
        self.all_elements = {
            "MODEL SETTINGS": [
                {"type": "label", "text": "OPENAI API KEY"},
                {"type": "entry", "command": self.entry_enter},
                {"type": "label", "text": "TOGETHER API KEY"},
                {"type": "entry", "command": self.entry_enter},
                {"type": "label", "text": "DEEPGRAM API KEY"},
                {"type": "entry", "command": self.entry_enter},
            ],
            "SCREENSHOT SETTINGS": [
                {"type": "label", "text": "LOOP TIME IN MIN"},
                {"type": "slider", "from": 0, "to": 60, "orient": tk.HORIZONTAL, "command": self.scale_changed},
                {"type": "label", "text": "TEXT MODEL"},
                {"type": "combobox", "values": ["Option 1", "Option 2", "Option 3"], "default_value": "Option 1", "command": self.combobox_selected},
                {"type": "label", "text": "COMPRESSION %"},
                {"type": "slider", "from": 0, "to": 100, "orient": tk.HORIZONTAL, "command": self.scale_changed},
                {"type": "checkbutton", "text": "ENABLED", "command": self.checkbutton_clicked}
            ],
            "PHOTO SETTINGS": [
                {"type": "label", "text": "LOOP TIME IN MIN"},
                {"type": "slider", "from": 0, "to": 60, "orient": tk.HORIZONTAL, "command": self.scale_changed},
                {"type": "label", "text": "VISION MODEL"},
                {"type": "combobox", "values": ["Option 1", "Option 2", "Option 3"], "default_value": "Option 1", "command": self.combobox_selected},
                {"type": "label", "text": "COMPRESSION %"},
                {"type": "slider", "from": 0, "to": 100, "orient": tk.HORIZONTAL, "command": self.scale_changed},
                {"type": "checkbutton", "text": "ENABLED", "command": self.checkbutton_clicked}
            ],
            "AUDIO SETTINGS": [
                {"type": "label", "text": "LOOP TIME IN MIN"},
                {"type": "slider", "from": 0, "to": 60, "orient": tk.HORIZONTAL, "command": self.scale_changed},
                {"type": "label", "text": "AUDIO MODEL"},
                {"type": "combobox", "values": ["Option 1", "Option 2", "Option 3"], "default_value": "Option 1", "command": self.combobox_selected},
                {"type": "label", "text": "COMPRESSION %"},
                {"type": "slider", "from": 0, "to": 100, "orient": tk.HORIZONTAL, "command": self.scale_changed},
                {"type": "checkbutton", "text": "ENABLED", "command": self.checkbutton_clicked}
            ],
            "AGENT SETTINGS": [
                {"type": "checkbutton", "text": "LIVE SUMMARY", "command": self.checkbutton_clicked},
                {"type": "button", "text": "Open New Window", "command": lambda: self.open_new_window(self.additional_elements)},
            ],
        }

        self.create_general_frames()
        self.create_button_frames()

        sv_ttk.set_theme("dark")

    def create_settings_frame(self, parent, title, elements):
        frame = ttk.LabelFrame(parent, text=title, padding=(10, 10, 10, 10))
        
        for element in elements:
            if element["type"] == "label":
                label = ttk.Label(frame, text=element["text"])
                label.pack(fill=tk.X, padx=5, pady=5)
            elif element["type"] == "entry":
                entry = ttk.Entry(frame)
                entry.pack(fill=tk.X, padx=5, pady=5)
                entry.bind("<Return>", element.get("command"))
            elif element["type"] == "checkbutton":
                var = tk.BooleanVar(value=element.get("default_value", False))
                checkbutton = ttk.Checkbutton(frame, text=element["text"], variable=var, onvalue=False, offvalue=True)
                checkbutton.pack(fill=tk.X, padx=5, pady=5)
                checkbutton.var = var
                checkbutton.bind("<Button-1>", element.get("command"))
            elif element["type"] == "combobox":
                var = tk.StringVar(value=element.get("default_value", ""))
                combobox = ttk.Combobox(frame, textvariable=var, values=element["values"])
                combobox.pack(fill=tk.X, padx=5, pady=5)
                combobox.bind("<<ComboboxSelected>>", element.get("command"))
            elif element["type"] == "slider":
                slider_frame = ttk.Frame(frame)
                slider_frame.pack(fill=tk.X, expand=True)
                
                value_label = ttk.Label(slider_frame, text=str(element["from"]))
                value_label.pack(side=tk.RIGHT, padx=(10, 0))

                slider = ttk.Scale(slider_frame, from_=element["from"], to=element["to"], orient=element["orient"])
                slider.pack(fill=tk.X)
                
                slider.bind("<ButtonRelease-1>", lambda event, label=value_label: self.scale_changed(event, label))
            elif element["type"] == "button":
                button = ttk.Button(frame, text=element["text"], command=element["command"])
                button.pack(fill=tk.X, padx=5, pady=5)
        
        return frame
    
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

    def run(self):
        self.root.mainloop()

    def start_action(self):
        print("Start action triggered")
    def stop_action(self):
        print("Stop action triggered")
        
    def entry_enter(self, event):
        print("Entry entered:", event.widget.get())

    def combobox_selected(self, event):
        print("Combobox selected:", event.widget.get())

    def checkbutton_clicked(self, event):
        if isinstance(event.widget, ttk.Checkbutton):
            var = event.widget.var
            print("Checkbutton clicked:", var.get())

    def scale_changed(self, event, value_label):
        slider = event.widget
        value = int(slider.get())  # Round the float value to an integer
        print("Scale changed:", value)
        value_label.config(text=str(value))

    def open_new_window(self, additional_elements):
        new_window = tk.Toplevel(self.root)
        new_window.title("New Window")

        main_frame = ttk.Frame(new_window, padding=(10, 10, 10, 10))
        main_frame.pack(expand=True, fill=tk.BOTH)

        frames = {}
        for title, elements in additional_elements.items():
            frames[title] = self.create_settings_frame(new_window, title, elements)
            frames[title].pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, padx=5, pady=5, fill=tk.X)

        start_button = ttk.Button(button_frame, text="DONE", command=self.start_action)
        stop_button = ttk.Button(button_frame, text="CANCEL", command=self.stop_action)

        start_button.pack(side=tk.LEFT, padx=(0, 5), pady=5, fill=tk.X, expand=True)
        stop_button.pack(side=tk.LEFT, padx=(5, 0), pady=5, fill=tk.X, expand=True)