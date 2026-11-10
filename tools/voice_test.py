"""Ses testi: kullanıcının sesi (klon) ve hazır sesler, farklı duygularla."""
import os, sys, subprocess
from pocket_tts_turkish import TurkishTTS, save_wav

LINES = [
    "Dur, kaydırma! Sana bir sır vereyim. Bir zamanlar gemiler karada yürüdü. Hem de tek bir gecede!",
    "Yıl 1453. 21 yaşındaki Fatih Sultan Mehmet, İstanbul'u almaya kararlı.",
    "Sabah Bizanslılar uyanır ve Haliç'te 70 kadar Osmanlı gemisi görür!",
]
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
tts = TurkishTTS.from_pretrained(device="cpu")
variants = []
if os.path.exists("/tmp/ref.wav"):
    me = tts.voice_from_file("/tmp/ref.wav")
    variants += [("senin_sesin_normal", me, None), ("senin_sesin_mutlu", me, "mutlu"), ("senin_sesin_saskin", me, "şaşkın")]
variants += [("hazir_erkek2_mutlu", "male_2", "mutlu"), ("hazir_erkek1_anlatici", "male_1", None), ("hazir_erkek3_mutlu", "male_3", "mutlu")]
import numpy as np
for name, voice, emo in variants:
    parts = []
    for line in LINES:
        kw = {"voice": voice, "seed": 7}
        if emo:
            kw["emotion"] = emo
        parts.append(tts.generate(line, **kw))
        parts.append(np.zeros(int(tts.sample_rate * 0.4), dtype=np.float32))
    wav = os.path.join(out, name + ".wav")
    save_wav(wav, np.concatenate(parts), tts.sample_rate)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-b:a", "96k", wav[:-4] + ".mp3"], check=True)
    os.remove(wav)
    print("hazır:", name)
