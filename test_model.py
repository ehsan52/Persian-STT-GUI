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
import os
import wave
import numpy as np
from stt import Model

# مسیر فایل‌ها
MODEL = "persian_stt.tflite"
AUDIO_ORIGINAL = "input.wav"  # فایل ورودی
AUDIO = "input_16k.wav"      # فایل تبدیل‌شده

# 1️⃣ تبدیل فایل صوتی به فرمت مورد نیاز
subprocess.run([
    "./ffmpeg/bin/ffmpeg.exe",
    "-y",               # overwrite اگر فایل وجود داشت
    "-i", AUDIO_ORIGINAL,
    "-ar", "16000",     # نرخ نمونه 16kHz
    "-ac", "1",         # mono
    "-c:a", "pcm_s16le",# 16bit PCM
    AUDIO
], check=True)

# 2️⃣ بارگذاری مدل
model = Model(MODEL)  # بدون scorer

# 3️⃣ خواندن فایل صوتی
with wave.open(AUDIO, "rb") as wf:
    frames = wf.readframes(wf.getnframes())
    audio = np.frombuffer(frames, dtype=np.int16)

# 4️⃣ استنتاج
text = model.stt(audio)
print("OUTPUT:")
print(text)
