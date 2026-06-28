"""
Modern GUI using CustomTkinter with dark theme, cheat toggle cards, system tray.
"""
import customtkinter as ctk
import asyncio
import threading
from typing import Optional
from PIL import Image
import pystray
from .trainer import Trainer
from .memory import MemoryManager
from .config import config
import logging

logger = logging.getLogger(__name__)

class App(ctk.CTk):
    def __init__(self, trainer: Trainer, memory: MemoryManager):
        super().__init__()
        self.trainer = trainer
        self.memory = memory
        self.title("Deltarune Chapter 5 Ultimate Trainer")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(bg="#1a1a2e")
        self.tray_icon = None

        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _create_widgets(self):
        self.title_label = ctk.CTkLabel(self, text="⚔️ Deltarune Chapter 5 Trainer", font=("Roboto", 20))
        self.title_label.pack(pady=10)

        self.attach_btn = ctk.CTkButton(self, text="Attach to Game", command=self.attach_game)
        self.attach_btn.pack(pady=5)

        self.status_var = ctk.StringVar(value="Not attached")
        self.status_label = ctk.CTkLabel(self, textvariable=self.status_var, fg_color="gray")
        self.status_label.pack(pady=5)

        self.cheats_frame = ctk.CTkScrollableFrame(self, width=700, height=300)
        self.cheats_frame.pack(pady=10)

        self.cheat_switches = {}
        cheat_names = ["infinite_hp", "max_stats", "unlimited_items", "infinite_gold",
                       "one_hit_kill", "speed_hack", "freeze_timer", "unlock_all"]
        cheat_labels = ["Infinite HP", "Max Stats", "Unlimited Items", "Infinite Gold",
                        "One-Hit Kill", "Speed Hack", "Freeze Timer", "Unlock All"]
        for name, label in zip(cheat_names, cheat_labels):
            switch = ctk.CTkSwitch(self.cheats_frame, text=label,
                                   command=lambda n=name: self.toggle_cheat(n))
            switch.pack(pady=2, anchor="w")
            self.cheat_switches[name] = switch

        self.start_loop_btn = ctk.CTkButton(self, text="Start Cheat Loop", command=self.start_loop)
        self.start_loop_btn.pack(pady=5)

        self.stop_loop_btn = ctk.CTkButton(self, text="Stop Cheat Loop", command=self.stop_loop)
        self.stop_loop_btn.pack(pady=5)

        self.console = ctk.CTkTextbox(self, height=150)
        self.console.pack(fill="x", padx=10, pady=5)

    def attach_game(self):
        success = self.memory.attach()
        if success:
            self.status_var.set("Attached to DELTARUNE.exe")
            self.status_label.configure(fg_color="green")
        else:
            self.status_var.set("Failed to attach")
            self.status_label.configure(fg_color="red")

    def toggle_cheat(self, name):
        state = self.cheat_switches[name].get()
        self.trainer.toggle_cheat(name, state)

    def start_loop(self):
        asyncio.run_coroutine_threadsafe(self.trainer.start_loop(), main_loop)

    def stop_loop(self):
        asyncio.run_coroutine_threadsafe(self.trainer.stop_loop(), main_loop)

    def on_closing(self):
        self.stop_loop()
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()

    def setup_tray(self):
        image = Image.new("RGB", (64, 64), "black")
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window, default=True),
            pystray.MenuItem("Exit", self.on_closing)
        )
        self.tray_icon = pystray.Icon("trainer", image, "Deltarune Trainer", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self):
        self.after(0, self.deiconify)
        self.after(0, self.focus_force)
