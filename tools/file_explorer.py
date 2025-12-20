import os
import tkinter as tk
from tkinter import messagebox


class FileExplorerPopup:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Mini File Explorer")
        self.window.geometry("400x500")
        self.window.configure(bg="#1e1e1e")

        self.listbox = tk.Listbox(
            self.window, bg="#2d2d2d", fg="white", font=("Courier", 10)
        )
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.refresh_btn = tk.Button(self.window, text="Refresh", command=self.refresh)
        self.refresh_btn.pack(pady=5)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        try:
            items = os.listdir(".")
            for item in items:
                prefix = "[DIR] " if os.path.isdir(item) else "[FILE] "
                self.listbox.insert(tk.END, f"{prefix}{item}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read directory: {e}")
