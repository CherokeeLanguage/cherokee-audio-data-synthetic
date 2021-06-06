#!/usr/bin/env -S conda run -n cherokee-audio-data python
import random
import shutil
import sys
import unicodedata as ud
import subprocess
from pathlib import Path
from typing import List
import os
from typing import Dict
from typing import Tuple

from progressbar import ProgressBar
from pydub import AudioSegment
from pydub import effects

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    home = str(Path.home())
    tts_bin: str = os.path.join(home, "git", "Cherokee-TTS", "tts-wrapper", "tts.sh")
    tts_checkpoint: str = "2a-2021-05-01-epoch_300-loss_0.0740"

    # "360-en-m" "329-en-f" "361-en-f" "308-en-f" "311-en-m" "334-en-m" "362-en-f" "330-en-f" "339-en-f" "294-en-f"
    # "310-en-f" "318-en-f" "333-en-f" "305-en-f" "297-en-f" "301-en-f" "341-en-f" "299-en-f" "300-en-f" "345-en-m"
    # "306-en-f"
    # "01-m-wwacc"

    # 345-en-m, 299-en-f, 311-en-m?,
    tts_voice: str = "360-en-m"

    ced_file: str = os.path.join("..", "ced-mco-alt.txt")

    shutil.rmtree(tts_voice, ignore_errors=True)
    os.mkdir(tts_voice)

    ced_entries: List[str] = []
    with open(ced_file, "r") as f:
        line: str
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            if "|" not in line:
                continue
            ced_entries.append(line)

    random.Random(0).shuffle(ced_entries)

    bar: ProgressBar = ProgressBar(maxval=len(ced_entries))
    bar.start()

    line: str
    for line in ced_entries:
        bar.update(bar.currval+1)
        fields: List[str] = line.split("|")
        id_num: str = fields[0]
        syllabary: str = fields[1]
        pronounce: str = fields[2]
        definition: str = fields[3]
        pronounce = ud.normalize("NFD", pronounce)
        cmd: List[str] = [tts_bin, "--gpu", "--checkpoint", tts_checkpoint, "--lang", "chr", "--voice", tts_voice,
                          "--wav", "tmp.wav", "--text", pronounce]
        subprocess.run(cmd, check=True)
        audio: AudioSegment = AudioSegment.from_file("tmp.wav")
        audio = effects.normalize(audio)
        audio.export(os.path.join(tts_voice, f"{tts_voice}_{id_num}.mp3"), format="mp3", parameters=["-qscale:a", "3"])
        with open(os.path.join(tts_voice, f"{tts_voice}_{id_num}.txt"), "w") as f:
            f.write(f"[{tts_voice}]")
            f.write("\n")
            f.write(f"{syllabary} ({pronounce})")
            f.write("\n")
            f.write(f"{definition}")
            f.write("\n")

        os.remove("tmp.wav")

    bar.finish()
    print("DONE")
    sys.exit()
