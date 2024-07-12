import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import random
import pygame

class HebrewVerbApp:
    def __init__(self, root, resource_dirs):
        self.root = root
        self.root.title("Hebrew Verb TPR Learning")
        self.root.geometry("800x900")

        self.resource_dirs = resource_dirs
        self.images = []
        self.audios = []
        self.verbs = []
        self.load_resources()

        pygame.mixer.init()

        self.image_label = tk.Label(root)
        self.image_label.pack(pady=20)

        self.verb_label = tk.Label(root, font=("Arial", 44))
        self.verb_label.pack(pady=20)

        self.display_random_verb()

        # Bind key press event to return to selection screen
        self.root.bind("<KeyPress>", self.on_key_press)

    def load_resources(self):
        try:
            for resource_dir in self.resource_dirs:
                for filename in os.listdir(resource_dir):
                    name, ext = os.path.splitext(filename)
                    if ext.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
                        self.images.append(os.path.join(resource_dir, filename))
                        self.verbs.append(name)
                    elif ext.lower() == '.mp3':
                        self.audios.append(os.path.join(resource_dir, filename))
        except FileNotFoundError:
            messagebox.showerror("Error", f"Directory not found: {resource_dir}")
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.root.quit()

        if not self.images or not self.audios:
            messagebox.showwarning("Warning", "No image or audio files found in the specified directory.")
            self.root.quit()

    def display_random_verb(self):
        if self.images and self.audios:
            index = random.randint(0, len(self.verbs) - 1)
            image_path = self.images[index]
            audio_path = self.audios[index]
            verb = self.verbs[index]

            try:
                # Display image
                image = Image.open(image_path)
                image = image.resize((700, 700), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo)
                self.image_label.image = photo
                self.verb_label.config(text=verb)

                # Play audio
                pygame.mixer.music.stop()  # Stop any currently playing audio
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Error displaying verb {verb}: {str(e)}")

        self.root.after(5000, self.display_random_verb)

    def on_key_press(self, event):
        self.root.destroy()
        main()

def main():
    root = tk.Tk()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    def set_resource_dirs(choice):
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
        app = HebrewVerbApp(root, resource_dirs)
        root.deiconify()  # Show the root window after selection
        root.mainloop()

    button_window = tk.Toplevel(root)
    button_window.title("Choose Directory")
    button_window.geometry("300x200")

    tk.Label(button_window, text="Choose a directory to load:").pack(pady=10)
    tk.Button(button_window, text="Milim 1", command=lambda: set_resource_dirs('1')).pack(pady=5)
    tk.Button(button_window, text="Milim 2", command=lambda: set_resource_dirs('2')).pack(pady=5)
    tk.Button(button_window, text="All", command=lambda: set_resource_dirs('all')).pack(pady=5)

    root.withdraw()  # Hide the root window until a choice is made
    button_window.mainloop()

if __name__ == "__main__":
    main()
