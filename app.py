import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from PIL import Image, ImageTk
import os
import random
import pygame

def read_settings(file_path):
    settings = {}
    with open(file_path, 'r') as file:
        for line in file:
            name, value = line.strip().split('=')
            settings[name] = int(value)
    return settings

class HebrewVerbApp:
    def __init__(self, root, resource_dirs, display_time=2500):
        self.root = root
        self.root.title("TPR Game")
        self.root.geometry("1200x950")

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

        self.replay_button = tk.Button(root, text="Replay Audio", command=self.replay_audio)
        self.replay_button.pack(pady=10)

        self.display_time = display_time  # Use the chosen display time
        self.current_verb_index = -1
        self.repeat_count = 1
        self.current_repeat = 0
        self.last_verb_index = -1  # To store the index of the last displayed verb

        self.after_id = None  # Initialize after_id

        # Bind key press events
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<space>", self.replay_audio)

        self.start_random_selection()  # Start with an initial random selection


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
            self.root.after_cancel(self.after_id)
        self.after_id = self.root.after(self.display_time, self.display_random_verb)

    def start_random_selection(self):
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
            self.verb_label.config(text=verb)

            # Play audio
            pygame.mixer.music.stop()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()

        except Exception as e:
            print(f"Error displaying verb {verb}: {str(e)}")

    def replay_audio(self, event=None):
        if self.current_verb_index >= 0:
            audio_path = self.audios[self.current_verb_index]
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()

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
        self.root.destroy()
        main()

    def exit_app(self):
        self.root.destroy()

    def show_about(self):
        messagebox.showinfo("About", "TPR Game\nVersion 0.1\n© 2024 Jeremy Steinberg")

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
    
    def set_resource_dirs(choice):
        milim_dir = os.path.join(script_dir, "milim")
        if choice == 'all':
            resource_dirs = [os.path.join(milim_dir, d) for d in os.listdir(milim_dir) if os.path.isdir(os.path.join(milim_dir, d))]
        else:
            resource_dirs = [os.path.join(milim_dir, choice)]
        
        display_time = int(display_time_entry.get())
        repeat_count = int(repeat_count_entry.get())

        button_window.destroy()
        app = HebrewVerbApp(root, resource_dirs, display_time)  # Use display_time from entry
        app.repeat_count = repeat_count  # Use repeat_count from entry
        root.deiconify()  # Show the root window after selection
        root.mainloop()

    milim_dir = os.path.join(script_dir, "milim")
    subdirs = [d for d in os.listdir(milim_dir) if os.path.isdir(os.path.join(milim_dir, d))]

    button_window = tk.Toplevel(root)
    button_window.title("Choose Directory, Display Time, and Repeat Count")
    button_window.geometry("400x600")
    button_window.config(bg="#f0f0f0")

    title_label = tk.Label(button_window, text="TPR Game Setup", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
    title_label.pack(pady=20)

    dir_label = tk.Label(button_window, text="Choose a directory to load:", font=("Helvetica", 12), bg="#f0f0f0")
    dir_label.pack(pady=10)
    
    for subdir in subdirs:
        tk.Button(button_window, text=subdir, font=("Helvetica", 10), 
                  command=lambda subdir=subdir: set_resource_dirs(subdir)).pack(pady=5)
    tk.Button(button_window, text="All", font=("Helvetica", 10), 
              command=lambda: set_resource_dirs('all')).pack(pady=5)

    display_time_label = tk.Label(button_window, text="Set Display Time (ms):", font=("Helvetica", 12), bg="#f0f0f0")
    display_time_label.pack(pady=10)
    display_time = tk.StringVar(value=settings['display_time'])
    display_time_entry = tk.Entry(button_window, textvariable=display_time, font=("Helvetica", 10))
    display_time_entry.pack(pady=5)

    repeat_count_label = tk.Label(button_window, text="Set Repeat Count:", font=("Helvetica", 12), bg="#f0f0f0")
    repeat_count_label.pack(pady=10)
    repeat_count = tk.StringVar(value=settings['repeat_count'])
    repeat_count_entry = tk.Entry(button_window, textvariable=repeat_count, font=("Helvetica", 10))
    repeat_count_entry.pack(pady=5)

    root.withdraw()  # Hide the root window until a choice is made
    button_window.mainloop()


if __name__ == "__main__":
    main()


