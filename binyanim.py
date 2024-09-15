import tkinter as tk
from tkinter import font as tkfont

# Dictionary containing information for each binyan (unchanged)
binyan_info = {
    "Pa'al (פָּעַל)": {
        "Characteristics": "Basic form; most common verbs; simple actions.",
        "Mnemonic": '"Pal" Doing Actions: Visualize a friend (pal) performing everyday actions.',
        "Gesture": 'Pushing forward movement with your hand. Represents basic, straightforward actions.',
        "Example": "לִכְתּוֹב (lichtov) - to write.",
        "Color": "#3498db"  # Soft blue
    },
    "Pi'el (פִּעֵל)": {
        "Characteristics": "Intensive, frequentative, or causative actions.",
        "Mnemonic": '"Peeling Layers": Visualize peeling layers to intensify an action.',
        "Gesture": 'Punching forward motion. Represents intensified or repeated actions.',
        "Example": "לְדַבֵּר (ledaber) - to speak.",
        "Color": "#e74c3c"  # Soft red
    },
    "Hif'il (הִפְעִיל)": {
        "Characteristics": "Causative action; causing something to happen.",
        "Mnemonic": '"He Feels" to Cause: Associate "he feels" with causing an action.',
        "Gesture": 'Pointing forward with one hand as if instructing someone. Signifies causing an action to happen.',
        "Example": "לְהַדְלִיק (lehadlik) - lit (to cause to light).",
        "Color": "#2ecc71"  # Soft green
    },
    "Hitpa'el (הִתְפַּעֵל)": {
        "Characteristics": "Reflexive or reciprocal actions; the subject acts upon themselves.",
        "Mnemonic": '"Hit Yourself": Associate "hit" with actions done to oneself.',
        "Gesture": 'Interlocking fingers of both hands. Represents mutual or reflexive actions.',
        "Example": "לְהִתְרַחֵץ (lehitrachetz) - to wash oneself.",
        "Color": "#f39c12"  # Soft orange
    },
    "Huf'al (הֻפְעַל)": {
        "Characteristics": "Passive of HIF'IL; causative passive.",
        "Mnemonic": '"Who Fell": Sounds like "hu", indicating passive causation.',
        "Gesture": 'Palms upturned, as if accepting something. Reflects being caused to experience an action.',
        "Example": "לְהַחֲלִיף (lehachalif) - to be replaced.",
        "Color": "#e84393"  # Soft pink
    },
    "Pu'al (פֻּעַל)": {
        "Characteristics": "Passive of PI'EL; denotes intensive passive actions.",
        "Mnemonic": '"Pool" Immersion: Imagine being immersed in a pool, representing passive action.',
        "Gesture": 'Placing both hands over your head in a protective manner. Indicates receiving an intensive action passively.',
        "Example": "דֻּבַּר (dubar) - was spoken. Note Pu'al doesn't have an infinitive form",
        "Color": "#f1c40f"  # Soft yellow
    },
    "Nif'al (נִפְעַל)": {
        "Characteristics": "Passive voice or reflexive; action happening to the subject.",
        "Mnemonic": '"Kneel" (sounds like "ni-"): Imagine kneeling to receive an action. Indicates the action is happening to oneself or is passive.',
        "Gesture": 'Pointing towards yourself. Indicates the action is happening to oneself or is passive.',
        "Example": "לְהִיכָּנֵס (lehikanes) - to enter.",
        "Color": "#9b59b6"  # Soft purple
    }
}

class BinyanMenorah:
    def __init__(self, master):
        self.master = master
        self.master.title("Interactive Binyan Menorah")
        self.master.geometry("900x950")
        self.master.configure(bg="#f0f0f0")

        self.canvas = tk.Canvas(self.master, width=900, height=600, bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack(pady=20)

        self.info_frame = tk.Frame(self.master, bg="#f0f0f0")
        self.info_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.info_label = tk.Label(self.info_frame, text="Hover over a branch to learn about the Binyan",
                                   font=tkfont.Font(family="Helvetica", size=14),
                                   bg="#f0f0f0", wraplength=800, justify="center")
        self.info_label.pack(pady=10)

        self.draw_menorah()
        self.create_binyan_branches()

    def draw_menorah(self):
        # Base
        self.canvas.create_rectangle(350, 550, 550, 600, fill="#D4AF37", outline="#B8860B", width=2)
        
        # Main stem
        self.canvas.create_rectangle(435, 200, 465, 550, fill="#D4AF37", outline="#B8860B", width=2)

        # Decorative circles
        for y in range(240, 451, 70):
            self.canvas.create_oval(425, y, 475, y+30, fill="#FFD700", outline="#B8860B", width=2)

    def create_binyan_branches(self):
        branch_positions = [
            (75, 200), (200, 200), (325, 200), (450, 180),
            (575, 200), (700, 200), (825, 200)
        ]

        self.branches = []  # Store branch ids for resetting colors

        for i, (binyan, pos) in enumerate(zip(binyan_info.keys(), branch_positions)):
            # Create stylized branch
            branch = self.canvas.create_rectangle(pos[0]-25, pos[1], pos[0]+25, pos[1]+200,
                                                  fill="#D4AF37", outline="#B8860B", width=2)
            # Create flame
            flame = self.canvas.create_oval(pos[0]-20, pos[1]-40, pos[0]+20, pos[1],
                                            fill="#FFD700", outline="#FFD700")

            self.branches.append(branch)
            
            # Bind hover events
            self.canvas.tag_bind(branch, "<Enter>", lambda event, b=binyan, br=branch: self.on_enter(b, br))
            self.canvas.tag_bind(branch, "<Leave>", lambda event, br=branch: self.on_leave(br))
            self.canvas.tag_bind(flame, "<Enter>", lambda event, b=binyan, br=branch: self.on_enter(b, br))
            self.canvas.tag_bind(flame, "<Leave>", lambda event, br=branch: self.on_leave(br))

        # Draw curved connections
        self.draw_curved_connection(80, 400, 830, 400, 150)  # Pa'al to Nif'al
        self.draw_curved_connection(205, 400, 705, 400, 100)  # Pi'el to Pu'al
        self.draw_curved_connection(330, 400, 580, 400, 50)   # Hif'il to Huf'al
        self.draw_vertical_connection(450, 380)  # Hitpa'el

    def draw_curved_connection(self, x1, y1, x2, y2, offset):
        control_x = (x1 + x2) // 2
        control_y = y1 + offset
        self.canvas.create_line(x1, y1, control_x, control_y, x2, y2,
                                smooth=True, width=2, fill="#B8860B")

    def draw_vertical_connection(self, x, y):
        self.canvas.create_line(x, y, x, y+170, width=2, fill="#B8860B")

    def on_enter(self, binyan, branch):
        info = binyan_info[binyan]
        self.canvas.itemconfig(branch, fill=info['Color'])  # Change branch color on hover
        self.display_info(binyan)

    def on_leave(self, branch):
        self.canvas.itemconfig(branch, fill="#D4AF37")  # Reset branch color when not hovered
        self.reset_info(None)

    def display_info(self, binyan):
        info = binyan_info[binyan]
        self.info_label.config(
            text=f"{binyan}\n\n{info['Characteristics']}\n\n"
                 f"Mnemonic: {info['Mnemonic']}\n\n"
                 f"Gesture: {info['Gesture']}\n\n"
                 f"Example: {info['Example']}",
            fg=info['Color'],
            font=tkfont.Font(family="Helvetica", size=14, weight="bold")
        )

    def reset_info(self, event):
        self.info_label.config(
            text="Hover over a branch to learn about the Binyan",
            fg="black",
            font=tkfont.Font(family="Helvetica", size=14)
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = BinyanMenorah(root)
    root.mainloop()
