import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
from PIL import Image, ImageTk
import os
import random
import pygame
import csv
import tempfile
import shutil

def read_settings(file_path):
    settings = {}
    if not os.path.exists(file_path):
        # If settings file doesn't exist, return default settings
        settings['display_time'] = 2500
        settings['repeat_count'] = 1
        return settings
    with open(file_path, 'r') as file:
        for line in file:
            name, value = line.strip().split('=')
            settings[name] = int(value)
    return settings

def write_settings(file_path, display_time, repeat_count):
    try:
        with open(file_path, 'w') as file:
            file.write(f"display_time={display_time}\n")
            file.write(f"repeat_count={repeat_count}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save settings: {e}")

def read_verb_binyan_mapping(file_path):
    mapping = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 3:
                    verb = row[0]
                    binyan = row[1]
                    root = row[2]
                    mapping[verb] = {'binyan': binyan, 'root': root}
                    # print(f"Loaded verb: {verb}, binyan: {binyan}, root: {root}")  # Debug print
    except Exception as e:
        print(f"Error reading binyan mapping: {e}")
    return mapping

def center_window(window, width, height):
    window.update_idletasks()  # Ensure window dimensions are calculated
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

class HebrewVerbApp:
    def __init__(self, root, resource_dirs, display_time=2500, repeat_count=1, settings_file='settings.txt'):
        self.root = root
        self.root.title("TPR Game")
        center_window(self.root, 1200, 1100)  # Center the window
        self.root.configure(bg="#F0F4F8")

        self.resource_dirs = resource_dirs
        self.images = []
        self.audios = []
        self.verbs = []
        self.load_resources()

        pygame.mixer.init()

        self.create_menu()

        self.image_label = tk.Label(root)
        self.image_label.pack(pady=20)

        self.verb_label = tk.Label(root, font=("Arial", 44))
        self.verb_label.pack(pady=20)

        self.root_label = tk.Label(root, font=("Arial", 32))
        self.root_label.pack(pady=10)

        self.gesture_label = tk.Label(root, font=("Arial", 20))
        self.gesture_label.pack(pady=10)

        self.display_time = display_time  # Use the chosen display time
        self.repeat_count = repeat_count
        self.current_repeat = 0
        self.current_verb_index = -1
        self.last_verb_index = -1  # To store the index of the last displayed verb

        self.after_id = None  # Initialize after_id

        # Bind key press events
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<space>", self.replay_audio)

        # Read the verb-binyan mapping
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.verb_info = read_verb_binyan_mapping(os.path.join(script_dir, 'verb_binyan.csv'))

        # Define binyan colors
        self.binyan_colors = {
            "PA'AL": 'blue',
            "NIF'AL": 'purple',
            "PI'EL": 'red',
            "PU'AL": 'brown',
            "HIF'IL": 'green',
            "HUF'AL": 'pink',
            "HITPA'EL": 'orange'
        }

        # Define gestures for each binyan
        self.binyan_gestures = {
            "PA'AL": "Pushing forward movement with your hand.",
            "NIF'AL": "Pushing towards your other hand.",
            "PI'EL": "Punching forward motion.",
            "PU'AL": "Punching towards your other hand.",
            "HIF'IL": "Pointing forward with one hand as if instructing someone.",
            "HUF'AL": "Pointing towards your other hand.",
            "HITPA'EL": "Interlocking fingers of both hands."
        }

        # Store settings file path
        self.settings_file = os.path.join(script_dir, 'settings.txt')

        self.start_random_selection()  # Start with an initial random selection

        # Handle window close event to save settings
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Change Resource Directory", command=self.change_resource_dir)
        file_menu.add_command(label="Return to Main Menu", command=self.return_to_main_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Change Display Time", command=self.change_display_time)
        settings_menu.add_command(label="Set Repeat Count", command=self.set_repeat_count)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Instructions", command=self.show_instructions)

    def load_resources(self):
        for resource_dir in self.resource_dirs:
            try:
                for filename in os.listdir(resource_dir):
                    name, ext = os.path.splitext(filename)
                    if ext.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
                        self.images.append(os.path.join(resource_dir, filename))
                        self.verbs.append(name)
                    elif ext.lower() == '.mp3':
                        self.audios.append(os.path.join(resource_dir, filename))
            except FileNotFoundError:
                messagebox.showerror("Error", f"Directory not found: {resource_dir}")
            except PermissionError:
                messagebox.showerror("Error", f"Permission denied accessing directory: {resource_dir}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred loading resources: {str(e)}")

        if not self.images or not self.audios:
            messagebox.showwarning("Warning", "No image or audio files found in the specified directories.")
            self.root.quit()

    def display_random_verb(self):
        if self.current_repeat >= self.repeat_count:
            new_index = self.current_verb_index
            while new_index == self.current_verb_index:
                new_index = random.randint(0, len(self.verbs) - 1)
            self.current_verb_index = new_index
            self.current_repeat = 0
        self.display_current_verb()
        self.current_repeat += 1

        # Cancel any existing after() job before scheduling a new one
        if self.after_id:
            try:
                self.root.after_cancel(self.after_id)
            except Exception as e:
                print(f"Error canceling after callback: {e}")
        self.after_id = self.root.after(self.display_time, self.display_random_verb)

    def start_random_selection(self):
        if not self.verbs:
            messagebox.showwarning("Warning", "No verbs loaded to display.")
            return
        self.current_verb_index = random.randint(0, len(self.verbs) - 1)  # Initial random selection
        self.display_random_verb()

    def display_current_verb(self):
        image_path = self.images[self.current_verb_index]
        audio_path = self.audios[self.current_verb_index]
        verb = self.verbs[self.current_verb_index]

        try:
            # Display image
            image = Image.open(image_path)
            image = image.resize((1240, 700), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo

            # Get the verb info
            verb_info = self.verb_info.get(verb, {"binyan": "Unknown", "root": "Unknown"})
            binyan = verb_info["binyan"]
            root = verb_info["root"]
            color = self.binyan_colors.get(binyan, "black")
            gesture = self.binyan_gestures.get(binyan, "No gesture available.")

            # Format root with dashes between each character
            formatted_root = '-'.join(root)

            # Update labels
            self.verb_label.config(text=verb, fg=color)
            self.root_label.config(text=f"Root: {formatted_root}", fg="black")
            self.gesture_label.config(text=f"Binyan: {binyan}\nGesture: {gesture}")

            # Play audio
            pygame.mixer.music.stop()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()

        except Exception as e:
            print(f"Error displaying verb {verb}: {str(e)}")

    def replay_audio(self, event=None):
        if self.current_verb_index >= 0:
            audio_path = self.audios[self.current_verb_index]
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Error replaying audio: {e}")

    def on_key_press(self, event):
        if event.char == 'q':
            self.return_to_main_menu()
        elif event.char == 't':
            self.change_display_time()

    def change_display_time(self):
        new_time = simpledialog.askinteger("Change Display Time",
                                           "Enter new display time (in milliseconds):",
                                           parent=self.root,
                                           minvalue=1000,
                                           maxvalue=10000)
        if new_time:
            self.display_time = new_time

    def set_repeat_count(self):
        new_count = simpledialog.askinteger("Set Repeat Count",
                                            "Enter repeat count:",
                                            parent=self.root,
                                            minvalue=1)
        if new_count:
            self.repeat_count = new_count

    def change_resource_dir(self):
        new_dir = filedialog.askdirectory(title="Select Resource Directory")
        if new_dir:
            self.resource_dirs = [new_dir]
            self.images.clear()
            self.audios.clear()
            self.verbs.clear()
            self.load_resources()
            self.display_random_verb()

    def return_to_main_menu(self):
        self.save_settings()
        # Cancel any pending after callbacks
        if self.after_id:
            try:
                self.root.after_cancel(self.after_id)
            except Exception as e:
                print(f"Error canceling after callback during return to main menu: {e}")
        self.root.destroy()
        main()

    def exit_app(self):
        self.save_settings()
        # Cancel any pending after callbacks
        if self.after_id:
            try:
                self.root.after_cancel(self.after_id)
            except Exception as e:
                print(f"Error canceling after callback during exit: {e}")
        self.root.destroy()

    def save_settings(self):
        # Read current settings from the app
        current_display_time = self.display_time
        current_repeat_count = self.repeat_count
        write_settings(self.settings_file, current_display_time, current_repeat_count)

    def show_about(self):
        messagebox.showinfo("About", "TPR Game\nVersion 0.2\n© 2024 Jeremy Steinberg")

    def show_instructions(self):
        instructions = """
        Instructions:
        1. Images and audio will automatically change every few seconds.
        2. Press the 'Replay Audio' button or spacebar to replay the current audio.
        3. Use the File menu to change settings or exit the application.
        4. Press 'q' to return to the main menu, 't' to change display time.
        """
        messagebox.showinfo("Instructions", instructions)

def main():
    root = tk.Tk()
    script_dir = os.path.dirname(os.path.abspath(__file__))

    settings_file = os.path.join(script_dir, "settings.txt")
    settings = read_settings(settings_file)  # Read settings from the file

    def start_game(selected_dirs):
        if not selected_dirs:
            messagebox.showerror("No Selection", "Please select at least one milim folder to start the game.")
            return

        try:
            display_time_val = int(display_time_entry.get())
            repeat_count_val = int(repeat_count_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers for display time and repeat count.")
            return

        button_window.destroy()
        app = HebrewVerbApp(root, selected_dirs, display_time_val, repeat_count_val, settings_file)
        app.repeat_count = repeat_count_val  # Use repeat_count from entry
        root.deiconify()  # Show the root window after selection
        root.mainloop()

    def choose_random_10_words():
        milim_dir = os.path.join(script_dir, "milim")
        subdirs = [d for d in os.listdir(milim_dir) if os.path.isdir(os.path.join(milim_dir, d))]

        if not subdirs:
            messagebox.showerror("Error", "No subdirectories found in the milim directory.")
            return

        # Collect all file groups across all subdirectories
        all_file_groups = {}
        for subdir in subdirs:
            subdir_path = os.path.join(milim_dir, subdir)
            try:
                all_files = [f for f in os.listdir(subdir_path) if f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp3'))]
            except Exception as e:
                messagebox.showerror("Error", f"Failed to list files in {subdir_path}: {e}")
                return

            for file in all_files:
                base_name = os.path.splitext(file)[0]
                if base_name not in all_file_groups:
                    all_file_groups[base_name] = {'image': None, 'audio': None}
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    all_file_groups[base_name]['image'] = os.path.join(subdir_path, file)
                elif file.lower().endswith('.mp3'):
                    all_file_groups[base_name]['audio'] = os.path.join(subdir_path, file)

        # Filter out groups that don't have both image and audio
        valid_groups = [k for k, v in all_file_groups.items() if v['image'] and v['audio']]

        if not valid_groups:
            messagebox.showerror("Error", "No valid word groups found (each must have both image and audio).")
            return

        # Select up to 10 random groups (verbs)
        selected_groups = random.sample(valid_groups, min(len(valid_groups), 10))

        # Create a temporary directory to store selected resources
        temp_dir = tempfile.mkdtemp(prefix="selected_words_")

        # Copy selected files to temporary directory
        for group in selected_groups:
            image_src = all_file_groups[group]['image']
            audio_src = all_file_groups[group]['audio']
            try:
                shutil.copy(image_src, temp_dir)
                shutil.copy(audio_src, temp_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy files for '{group}': {e}")
                shutil.rmtree(temp_dir)  # Clean up
                return

        try:
            display_time_val = int(display_time_entry.get())
            repeat_count_val = int(repeat_count_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers for display time and repeat count.")
            shutil.rmtree(temp_dir)  # Clean up
            return

        button_window.destroy()
        app = HebrewVerbApp(root, [temp_dir], display_time_val, repeat_count_val, settings_file)

        # Optional: Ensure temporary directory is deleted when the app exits
        def on_exit():
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Failed to delete temporary directory {temp_dir}: {e}")
            app.exit_app()

        app.root.protocol("WM_DELETE_WINDOW", on_exit)

        app.repeat_count = repeat_count_val
        root.deiconify()
        root.mainloop()

    milim_dir = os.path.join(script_dir, "milim")
    if not os.path.exists(milim_dir):
        messagebox.showerror("Error", f"'milim' directory not found at {milim_dir}. Please ensure the directory exists.")
        return

    subdirs = [d for d in os.listdir(milim_dir) if os.path.isdir(os.path.join(milim_dir, d))]

    if not subdirs:
        messagebox.showerror("Error", "No milim folders found in the 'milim' directory.")
        return

    button_window = tk.Toplevel(root)
    button_window.title("TPR Game Setup")
    center_window(button_window, 400, 600)  # Center the window
    button_window.resizable(True, True)  # Allow resizing
    button_window.configure(bg="#f0f0f0")

    # Create a main frame with padding
    main_frame = ttk.Frame(button_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Title
    title_label = ttk.Label(main_frame, text="TPR Game Setup", font=("Helvetica", 18, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="W")

    # Resource Directory Selection
    dir_label = ttk.Label(main_frame, text="Select milim folders to load:", font=("Helvetica", 12))
    dir_label.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="W")

    # Create a frame for directory checkboxes with vertical scrolling
    dir_frame = ttk.Frame(main_frame)
    dir_frame.grid(row=2, column=0, columnspan=2, sticky="NSEW")

    # Configure grid weights for responsiveness
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(2, weight=1)

    # Add a canvas and vertical scrollbar for directories
    canvas = tk.Canvas(dir_frame, borderwidth=0, background="#f0f0f0")
    scrollbar = ttk.Scrollbar(dir_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas, padding="0 0 0 0")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Define number of columns per row
    columns = 3

    # Dictionary to hold the state of each checkbox
    checkbox_vars = {}

    # Add directory checkboxes arranged in a grid with multiple rows
    for idx, subdir in enumerate(subdirs):
        var = tk.BooleanVar()
        checkbox_vars[subdir] = var
        row = idx // columns
        col = idx % columns
        chk = ttk.Checkbutton(scrollable_frame, text=subdir, variable=var)
        chk.grid(row=row, column=col, padx=5, pady=5, sticky="W")

    # "Select All" and "Deselect All" buttons
    select_all_btn = ttk.Button(scrollable_frame, text="Select All", command=lambda: [v.set(True) for v in checkbox_vars.values()])
    select_all_btn.grid(row=(len(subdirs) // columns) + 1, column=0, padx=5, pady=5, sticky="EW")

    deselect_all_btn = ttk.Button(scrollable_frame, text="Deselect All", command=lambda: [v.set(False) for v in checkbox_vars.values()])
    deselect_all_btn.grid(row=(len(subdirs) // columns) + 1, column=1, padx=5, pady=5, sticky="EW")

    # Configure column weights in scrollable_frame to make checkboxes expand equally
    for col in range(columns):
        scrollable_frame.columnconfigure(col, weight=1)

    # Start Button
    start_button = ttk.Button(main_frame, text="Start", command=lambda: start_game(
        [os.path.join(milim_dir, subdir) for subdir, var in checkbox_vars.items() if var.get()]
    ))
    start_button.grid(row=3, column=0, columnspan=2, pady=20, sticky="EW")

    # Random 10 Words Button
    random_button = ttk.Button(main_frame, text="Random 10 Words", command=choose_random_10_words)
    random_button.grid(row=4, column=0, columnspan=2, pady=10, sticky="EW")

    # Display Time Entry
    display_time_label = ttk.Label(main_frame, text="Set Display Time (ms):", font=("Helvetica", 12))
    display_time_label.grid(row=5, column=0, columnspan=2, pady=(20, 5), sticky="W")
    display_time = tk.StringVar(value=str(settings.get('display_time', 2500)))
    display_time_entry = ttk.Entry(main_frame, textvariable=display_time, font=("Helvetica", 12))
    display_time_entry.grid(row=6, column=0, columnspan=2, pady=5, sticky="EW")

    # Repeat Count Entry
    repeat_count_label = ttk.Label(main_frame, text="Set Repeat Count:", font=("Helvetica", 12))
    repeat_count_label.grid(row=7, column=0, columnspan=2, pady=(20, 5), sticky="W")
    repeat_count = tk.StringVar(value=str(settings.get('repeat_count', 1)))
    repeat_count_entry = ttk.Entry(main_frame, textvariable=repeat_count, font=("Helvetica", 12))
    repeat_count_entry.grid(row=8, column=0, columnspan=2, pady=5, sticky="EW")

    # Tooltip function
    def create_tooltip(widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        label = ttk.Label(tooltip, text=text, background="#ffffe0", relief='solid', borderwidth=1, padding=5)
        label.pack()

        def enter(event):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + widget.winfo_height() + 10
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    # Add tooltips
    create_tooltip(display_time_entry, "Enter the time each verb is displayed in milliseconds (1000-10000).")
    create_tooltip(repeat_count_entry, "Enter how many times each verb should repeat.")

    # Initially hide the root window
    root.withdraw()
    button_window.grab_set()
    button_window.mainloop()

if __name__ == "__main__":
    main()
