# Copyright (C) 2025 Ehsan Eskandari
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# https://www.gnu.org/licenses/ for details.

import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import wave
import numpy as np
from stt import Model
import os
import pyperclip

# -------------------------------
# تنظیمات پیش‌فرض
# -------------------------------
MODEL_PATH = "./_internal/persian_stt.tflite"
FFMPEG_PATH = "./_internal/ffmpeg/bin/ffmpeg.exe"

model = Model(MODEL_PATH)
AUDIO_ORIGINAL = None

# -------------------------------
# توابع
# -------------------------------

def set_paths():
    """Change model or ffmpeg paths"""
    global MODEL_PATH, FFMPEG_PATH, model
    new_model = filedialog.askopenfilename(title="Select TFLite Model", filetypes=[("TFLite files", "*.tflite")])
    if new_model:
        MODEL_PATH = new_model
        model = Model(MODEL_PATH)
    new_ffmpeg = filedialog.askopenfilename(title="Select ffmpeg executable", filetypes=[("EXE files", "*.exe")])
    if new_ffmpeg:
        FFMPEG_PATH = new_ffmpeg
    messagebox.showinfo("Settings", "Paths updated successfully!")

def select_file():
    """Select audio file"""
    global AUDIO_ORIGINAL
    AUDIO_ORIGINAL = filedialog.askopenfilename(
        title="Select audio file",
        filetypes=[("Audio files", "*.wav *.mp3 *.flac *.ogg *.m4a"), ("All files", "*.*")]
    )
    if AUDIO_ORIGINAL:
        file_label.config(text=os.path.basename(AUDIO_ORIGINAL))
    else:
        file_label.config(text="No file selected")

def convert_to_wav(input_file):
    """Convert any audio to WAV 16kHz mono"""
    output_file = "temp_16k.wav"
    try:
        subprocess.run([
            FFMPEG_PATH,
            "-y",
            "-i", input_file,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            output_file
        ], check=True)
        return output_file
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", f"Failed to convert {os.path.basename(input_file)} to WAV")
        return None

def run_stt():
    """Convert audio to text with progress"""
    if not AUDIO_ORIGINAL:
        messagebox.showwarning("Warning", "Please select an audio file first")
        return

    wav_file = convert_to_wav(AUDIO_ORIGINAL)
    if not wav_file:
        return  # conversion failed

    try:
        with wave.open(wav_file, "rb") as wf:
            n_frames = wf.getnframes()
            chunk_size = 16000  # 1 second chunks
            frames_read = 0
            audio_data = np.array([], dtype=np.int16)
            
            while frames_read < n_frames:
                frames_to_read = min(chunk_size, n_frames - frames_read)
                frames = wf.readframes(frames_to_read)
                chunk = np.frombuffer(frames, dtype=np.int16)
                audio_data = np.concatenate((audio_data, chunk))
                frames_read += frames_to_read
                progress = int((frames_read / n_frames) * 100)
                progress_var.set(progress)
                root.update_idletasks()
    except Exception as e:
        messagebox.showerror("Error", f"Error reading audio file: {e}")
        return
    
    try:
        text = model.stt(audio_data)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, text)
        progress_var.set(100)
    except Exception as e:
        messagebox.showerror("Error", f"Error during STT: {e}")
        return

def copy_text():
    """Copy output text to clipboard"""
    text = output_text.get("1.0", tk.END).strip()
    if text:
        pyperclip.copy(text)
        messagebox.showinfo("Copied", "Output text copied to clipboard")
    else:
        messagebox.showwarning("Warning", "No text to copy")

def about():
    messagebox.showinfo(
        "About",
        "Persian STT GUI\n"
        "Author: ehsan52\n"
        "Version: 1.0\n"
        "Model based on Oct4Pie/persian-stt (GPLv3)\n"
        "Graphics designed by ehsan52"
    )

# -------------------------------
# GUI
# -------------------------------
root = tk.Tk()
root.title("Persian STT")
root.geometry("700x500")
root.resizable(False, False)
root.configure(bg="#1e1e2f")  # Dark theme background

# Menu
menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="About", command=about)
file_menu.add_command(label="Set Paths", command=set_paths)
file_menu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="Menu", menu=file_menu)
root.config(menu=menubar)

# File selection frame
file_frame = tk.Frame(root, bg="#1e1e2f")
file_frame.pack(pady=15)

file_btn = tk.Button(file_frame, text="Select Audio File", command=select_file,
                     bg="#4CAF50", fg="white", font=("Helvetica", 11, "bold"), width=20)
file_btn.pack(side=tk.LEFT, padx=10)

file_label = tk.Label(file_frame, text="No file selected", bg="#1e1e2f", fg="white", font=("Helvetica", 10))
file_label.pack(side=tk.LEFT)

# Run button
run_btn = tk.Button(root, text="Convert to Text", command=run_stt,
                    bg="#2196F3", fg="white", font=("Helvetica", 12, "bold"), width=22)
run_btn.pack(pady=10)

# Progress bar
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, maximum=100, variable=progress_var)
progress_bar.pack(fill=tk.X, padx=15, pady=5)

# Textbox with scrollbar
text_frame = tk.Frame(root, bg="#1e1e2f")
text_frame.pack(expand=True, fill=tk.BOTH, padx=15, pady=10)

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

output_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                      font=("Helvetica", 12), bg="#2e2e3e", fg="white", insertbackground="white")
output_text.pack(expand=True, fill=tk.BOTH)
scrollbar.config(command=output_text.yview)

# Copy button
copy_btn = tk.Button(root, text="Copy Output Text", command=copy_text,
                     bg="#FF5722", fg="white", font=("Helvetica", 11, "bold"), width=22)
copy_btn.pack(pady=10)

root.mainloop()
