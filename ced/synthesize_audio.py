#!/usr/bin/env -S conda run -n cherokee-audio-data python
import shutil
import sys

import subprocess
from pathlib import Path

from typing import List

import os

from typing import Dict
from typing import Tuple

from pydub import AudioSegment
from pydub import effects

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    home = str(Path.home())
    tts_bin: str = os.path.join(home, "git", "Cherokee-TTS", "tts-wrapper", "tts.sh")
    tts_checkpoint: str = "2a-2021-05-01-epoch_300-loss_0.0740"
    tts_voice: str = "345-en-m"

    ced_file: str = os.path.join("..", "ced-mco-alt.txt")
    ced_entries: Dict[str, Tuple[str, str, str]]

    shutil.rmtree(tts_voice, ignore_errors=True)
    os.mkdir(tts_voice)

    with open(ced_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            if "|" not in line:
                continue
            fields: List[str] = line.split("|")
            id_num: str = fields[0]
            pronounce: str = fields[1]
            definition: str = fields[2]
            cmd: List[str] = [tts_bin, "--checkpoint", tts_checkpoint, "--lang", "chr", "--voice", tts_voice, "--wav", "tmp.wav", "--text", pronounce]
            subprocess.run(cmd, check=True)
            audio: AudioSegment = AudioSegment.from_file("tmp.wav")
            audio = effects.normalize(audio)
            audio.export(os.path.join(tts_voice, f"{tts_voice}_{id_num}.mp3"), format="mp3", parameters=["-qscale:a", "3"])
            os.remove("tmp.wav")

    sys.exit()
