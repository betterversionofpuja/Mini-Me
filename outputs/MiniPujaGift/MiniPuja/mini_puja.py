"""Mini Puja: a small, transparent Windows desktop companion.

No network, accounts, installers, or third-party packages are required beyond
Pillow (the included launcher uses the bundled Codex runtime when available).
"""
from __future__ import annotations

import random
import sys
import time
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
SIZE = (112, 150)  # Default on-screen full-body pet size.
IDLE_SECONDS = 35
MESSAGES = [
    "Sarthakkk, look at me! ❤️",
    "Sending you a virtual hug!",
    "Take a little break, please.",
    "Good night, handsome! 🌙",
]


def load_frames(folder: str) -> list[ImageTk.PhotoImage]:
    frames = []
    for file in sorted((ASSETS / folder).glob("*.png")):
        image = Image.open(file).convert("RGBA")
        image.thumbnail(SIZE, Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        canvas.alpha_composite(image, ((SIZE[0] - image.width) // 2, SIZE[1] - image.height))
        frames.append(ImageTk.PhotoImage(canvas))
    if not frames:
        raise FileNotFoundError(f"No PNG frames found in {ASSETS / folder}")
    return frames


class MiniPuja:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Mini Puja")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#00ff00")
        # Windows makes the exact key color transparent. The artwork itself is RGBA.
        self.root.wm_attributes("-transparentcolor", "#00ff00")
        self.root.resizable(False, False)

        self.frames = {
            "idle": load_frames("idle"),
            "happy": load_frames("waving"),
            "love": load_frames("jumping"),
            "sleep": load_frames("waiting"),
        }
        self.state = "idle"
        self.frame_index = 0
        self.last_interaction = time.monotonic()
        self.drag_offset = (0, 0)
        self.animation_id: str | None = None
        self.reaction_id: str | None = None

        self.pet = tk.Label(self.root, bg="#00ff00", bd=0, highlightthickness=0)
        self.pet.pack()
        self.pet.bind("<ButtonPress-1>", self.start_drag)
        self.pet.bind("<B1-Motion>", self.drag)
        self.pet.bind("<ButtonRelease-1>", self.click)
        self.pet.bind("<Button-3>", self.menu)
        self.root.bind("<Escape>", lambda _event: self.root.destroy())

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{SIZE[0]}x{SIZE[1]}+{screen_w - SIZE[0] - 24}+{screen_h - SIZE[1] - 80}")
        self.animate()
        self.root.after(1500, self.check_inactivity)

    def animate(self) -> None:
        frames = self.frames[self.state]
        self.pet.configure(image=frames[self.frame_index % len(frames)])
        self.frame_index += 1
        delay = 520 if self.state in {"idle", "sleep"} else 145
        self.animation_id = self.root.after(delay, self.animate)

    def start_drag(self, event: tk.Event) -> None:
        self.drag_offset = (event.x_root - self.root.winfo_x(), event.y_root - self.root.winfo_y())
        self.last_interaction = time.monotonic()

    def drag(self, event: tk.Event) -> None:
        x = event.x_root - self.drag_offset[0]
        y = event.y_root - self.drag_offset[1]
        # Keep every pixel of Mini Puja on screen.
        x = max(0, min(x, self.root.winfo_screenwidth() - SIZE[0]))
        y = max(0, min(y, self.root.winfo_screenheight() - SIZE[1]))
        self.root.geometry(f"+{x}+{y}")

    def click(self, event: tk.Event) -> None:
        if abs(event.x_root - (self.root.winfo_x() + self.drag_offset[0])) > 5 or abs(event.y_root - (self.root.winfo_y() + self.drag_offset[1])) > 5:
            return
        self.last_interaction = time.monotonic()
        reaction = random.choice(["happy", "love"])
        self.set_state(reaction)
        if reaction == "love":
            self.show_heart()
        self.show_message(random.choice(MESSAGES))
        if self.reaction_id:
            self.root.after_cancel(self.reaction_id)
        self.reaction_id = self.root.after(2800, lambda: self.set_state("idle"))

    def show_heart(self) -> None:
        heart = tk.Toplevel(self.root)
        heart.overrideredirect(True)
        heart.attributes("-topmost", True)
        heart.configure(bg="#00ff00")
        heart.wm_attributes("-transparentcolor", "#00ff00")
        tk.Label(heart, text="♥", fg="#d9486c", bg="#00ff00", font=("Segoe UI Emoji", 20, "bold")).pack()
        heart.update_idletasks()
        heart.geometry(f"+{self.root.winfo_x() + SIZE[0] - 16}+{max(0, self.root.winfo_y() - 8)}")
        heart.after(1200, heart.destroy)

    def set_state(self, state: str) -> None:
        self.state = state
        self.frame_index = 0

    def check_inactivity(self) -> None:
        if time.monotonic() - self.last_interaction >= IDLE_SECONDS and self.state == "idle":
            self.set_state("sleep")
        self.root.after(1500, self.check_inactivity)

    def show_message(self, message: str) -> None:
        # Separate, short-lived tooltip placed above the pet; never covers the character.
        tip = tk.Toplevel(self.root)
        tip.overrideredirect(True)
        tip.attributes("-topmost", True)
        label = tk.Label(tip, text=message, bg="#fff9e9", fg="#56333f", padx=9, pady=5,
                         font=("Segoe UI", 9), relief="solid", bd=1)
        label.pack()
        tip.update_idletasks()
        x = self.root.winfo_x() + (SIZE[0] - tip.winfo_width()) // 2
        y = max(0, self.root.winfo_y() - tip.winfo_height() - 8)
        tip.geometry(f"+{x}+{y}")
        tip.after(2500, tip.destroy)

    def menu(self, event: tk.Event) -> None:
        menu = tk.Menu(self.root, tearoff=False)
        menu.add_command(label="Wave", command=lambda: self.set_state("happy"))
        menu.add_command(label="Sleep", command=lambda: self.set_state("sleep"))
        menu.add_separator()
        menu.add_command(label="Quit Mini Puja", command=self.root.destroy)
        menu.tk_popup(event.x_root, event.y_root)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    try:
        MiniPuja().run()
    except Exception as error:
        tk.Tk().withdraw()
        messagebox.showerror("Mini Puja", str(error))
        raise
