import tkinter as tk
from tkinter import ttk
import sv_ttk

def create_settings_frame(parent, title, elements):
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
            
            slider.bind("<ButtonRelease-1>", lambda event, label=value_label: scale_changed(event, label))
        elif element["type"] == "button":
            button = ttk.Button(frame, text=element["text"], command=element["command"])
            button.pack(fill=tk.X, padx=5, pady=5)
    
    return frame

def start_action():
    print("Start action triggered")

def stop_action():
    print("Stop action triggered")

def combobox_selected(event):
    print("Combobox selected:", event.widget.get())

def checkbutton_clicked(event):
    if isinstance(event.widget, ttk.Checkbutton):
        var = event.widget.var
        print("Checkbutton clicked:", var.get())

def entry_enter(event):
    print("Entry entered:", event.widget.get())

def scale_changed(event, value_label):
    slider = event.widget
    value = int(slider.get())  # Round the float value to an integer
    print("Scale changed:", value)
    value_label.config(text=str(value))

def open_new_window(additional_elements):
    new_window = tk.Toplevel(root)
    new_window.title("New Window")

    frames = {}
    for title, elements in additional_elements.items():
        frames[title] = create_settings_frame(new_window, title, elements)
        frames[title].pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

# Define elements for each frame
additional_elements = {
    "ADDITIONAL SETTINGS": [
        {"type": "label", "text": "LOOP TIME IN MIN"},
        {"type": "slider", "from": 0, "to": 60, "orient": tk.HORIZONTAL, "command": scale_changed},
        {"type": "label", "text": "TEXT MODEL"},
        {"type": "combobox", "values": ["Option 1", "Option 2", "Option 3"], "default_value": "Option 1", "command": combobox_selected},
        {"type": "checkbutton", "text": "ENABLED", "command": checkbutton_clicked}
    ]
}
all_elements = {
    "MODEL SETTINGS": [
        {"type": "label", "text": "OPENAI API KEY"},
        {"type": "entry", "command": entry_enter},
        {"type": "label", "text": "TOGETHER API KEY"},
        {"type": "entry", "command": entry_enter},
        {"type": "label", "text": "DEEPGRAM API KEY"},
        {"type": "entry", "command": entry_enter},
    ],
    "SCREENSHOT SETTINGS": [
        {"type": "label", "text": "LOOP TIME IN MIN"},
        {"type": "slider", "from": 0, "to": 60, "orient": tk.HORIZONTAL, "command": scale_changed},
        {"type": "label", "text": "TEXT MODEL"},
        {"type": "combobox", "values": ["Option 1", "Option 2", "Option 3"], "default_value": "Option 1", "command": combobox_selected},
        {"type": "label", "text": "COMPRESSION %"},
        {"type": "slider", "from": 0, "to": 100, "orient": tk.HORIZONTAL, "command": scale_changed},
        {"type": "checkbutton", "text": "ENABLED", "command": checkbutton_clicked}
    ],
    "PHOTO SETTINGS": [
        {"type": "label", "text": "LOOP TIME IN MIN"},
        {"type": "slider", "from": 0, "to": 60, "orient": tk.HORIZONTAL, "command": scale_changed},
        {"type": "label", "text": "VISION MODEL"},
        {"type": "combobox", "values": ["Option 1", "Option 2", "Option 3"], "default_value": "Option 1", "command": combobox_selected},
        {"type": "label", "text": "COMPRESSION %"},
        {"type": "slider", "from": 0, "to": 100, "orient": tk.HORIZONTAL, "command": scale_changed},
        {"type": "checkbutton", "text": "ENABLED", "command": checkbutton_clicked}
    ],
    "AUDIO SETTINGS": [
        {"type": "label", "text": "LOOP TIME IN MIN"},
        {"type": "slider", "from": 0, "to": 60, "orient": tk.HORIZONTAL, "command": scale_changed},
        {"type": "label", "text": "AUDIO MODEL"},
        {"type": "combobox", "values": ["Option 1", "Option 2", "Option 3"], "default_value": "Option 1", "command": combobox_selected},
        {"type": "label", "text": "COMPRESSION %"},
        {"type": "slider", "from": 0, "to": 100, "orient": tk.HORIZONTAL, "command": scale_changed},
        {"type": "checkbutton", "text": "ENABLED", "command": checkbutton_clicked}
    ],
    "AGENT SETTINGS": [
        {"type": "checkbutton", "text": "LIVE SUMMARY", "command": checkbutton_clicked},
        {"type": "button", "text": "Open New Window", "command": lambda: open_new_window(additional_elements)},
    ],
}

root = tk.Tk()
root.title("EYES")

# Create main frame
main_frame = ttk.Frame(root, padding=(10, 10, 10, 10))
main_frame.pack(expand=True, fill=tk.BOTH)

frames = {}
for title, elements in all_elements.items():
    frames[title] = create_settings_frame(main_frame, title, elements)
    frames[title].pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

# Create frame for buttons
button_frame = ttk.Frame(root)
button_frame.pack(side=tk.BOTTOM, padx=5, pady=5, fill=tk.X)

# Create start and stop buttons
start_button = ttk.Button(button_frame, text="START", command=start_action, style='start.TButton')
stop_button = ttk.Button(button_frame, text="STOP", command=stop_action, style='stop.TButton')

# Pack buttons
start_button.pack(side=tk.LEFT, padx=(0, 5), pady=5, fill=tk.X, expand=True)
stop_button.pack(side=tk.LEFT, padx=(5, 0), pady=5, fill=tk.X, expand=True)

# This is where the magic happens
sv_ttk.set_theme("dark")

root.mainloop()