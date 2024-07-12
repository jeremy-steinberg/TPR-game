import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from PIL import Image, ImageTk
import os
import random
import pygame

class HebrewVerbApp:
    def __init__(self, root, resource_dirs, display_time=5000):
        self.root = root
        self.root.title("TPR Game")
        self.root.geometry("800x950")

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

        self.after_id = None  # To store the after() job ID
        self.display_random_verb()

        # Bind key press events
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<space>", self.replay_audio)

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
        if self.images and self.audios:
            self.current_verb_index = random.randint(0, len(self.verbs) - 1)
            self.display_current_verb()

        # Cancel any existing after() job before scheduling a new one
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.after_id = self.root.after(self.display_time, self.display_random_verb)

    def display_current_verb(self):
        image_path = self.images[self.current_verb_index]
        audio_path = self.audios[self.current_verb_index]
        verb = self.verbs[self.current_verb_index]

        try:
            # Display image
            image = Image.open(image_path)
            image = image.resize((700, 700), Image.LANCZOS)
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
    
    def set_resource_dirs(choice, display_time):
        if choice == '1':
            resource_dirs = [os.path.join(script_dir, "milim1")]
        elif choice == '2':
            resource_dirs = [os.path.join(script_dir, "milim2")]
        elif choice == 'all':
            resource_dirs = [os.path.join(script_dir, "milim1"), os.path.join(script_dir, "milim2")]
        else:
            messagebox.showerror("Invalid Choice", "Invalid choice. Please restart the application and choose a valid option.")
            button_window.destroy()
            root.quit()
            return
        button_window.destroy()
        app = HebrewVerbApp(root, resource_dirs, display_time)
        root.deiconify()  # Show the root window after selection
        root.mainloop()

    button_window = tk.Toplevel(root)
    button_window.title("Choose Directory and Display Time")
    button_window.geometry("300x300")

    tk.Label(button_window, text="Choose a directory to load:").pack(pady=10)
    tk.Button(button_window, text="Milim 1", command=lambda: set_resource_dirs('1', display_time.get())).pack(pady=5)
    tk.Button(button_window, text="Milim 2", command=lambda: set_resource_dirs('2', display_time.get())).pack(pady=5)
    tk.Button(button_window, text="All", command=lambda: set_resource_dirs('all', display_time.get())).pack(pady=5)

    tk.Label(button_window, text="Set Display Time (ms):").pack(pady=10)
    display_time = tk.StringVar(value="5000")
    tk.Entry(button_window, textvariable=display_time).pack(pady=5)

    root.withdraw()  # Hide the root window until a choice is made
    button_window.mainloop()

if __name__ == "__main__":
    main()
