#!/usr/bin/env python3
import os
import sys
import string
import unicodedata as ud
import random
import re
import pathlib
import subprocess
from shutil import rmtree
from pydub import AudioSegment
import pydub.effects as effects
from split_audio import detect_sound
from builtins import list

include_o_form: bool = True

if __name__ == "__main__":

    if sys.argv[0].strip() != "":
        os.chdir(os.path.dirname(sys.argv[0]))

    MASTER_TEXTS: list = ["AudioQualityVotes.txt"]
    max_duration: float = 10.0

    use_augmented: bool = False
    if use_augmented:
        MASTER_TEXTS.append("augmented.txt")

    # cleanup any previous runs
    for dir in ["linear_spectrograms", "spectrograms", "wav"]:
        rmtree(dir, ignore_errors=True)

    pathlib.Path(".").joinpath("wav").mkdir(exist_ok=True)

    entries: dict = {}
    for MASTER_TEXT in MASTER_TEXTS:
        with open(MASTER_TEXT, "r") as f:
            for line in f:
                fields = line.split("|")
                speaker: str = fields[0].strip()
                mp3: str = fields[1].strip()
                text: str = ud.normalize("NFC", fields[2].strip())
                dedupeKey = speaker + "|" + mp3 + "|" + text
                if text == "" or "XXX" in text:
                    continue
                if not include_o_form and "\u030a" in text:
                    continue
                entries[dedupeKey] = (speaker, mp3, text)

    print(f"Loaded {len(entries):,} entries with audio and text.")

    # the voice id to use for any "?" marked entries
    voiceid: str = ""
    with open("voice-id.txt", "r") as f:
        for line in f:
            voiceid = line.strip()
            break

    # to map any non "?" marked entries from annotation short hand id to ML assigned sequence id
    voiceids: dict = {}
    with open("../voice-ids.txt") as f:
        for line in f:
            mapping = line.strip()
            fields = mapping.split("|")
            if len(fields) < 2 or fields[1].strip() == "":
                break
            id = fields[0].strip()
            if id.strip() == "":
                continue
            for field in fields[1:]:
                if field.strip() == "":
                    continue
                voiceids[field.strip()] = id

    id: int = 1

    shortestLength: float = -1
    longestLength: float = 0.0
    totalLength: float = 0.0
    print("Creating wavs")
    rows: list = []
    for speaker, mp3, text in entries.values():
        wav: str = "wav/" + os.path.splitext(os.path.basename(mp3))[0] + ".wav"
        text: str = ud.normalize('NFC', text)
        mp3_segment: AudioSegment = AudioSegment.from_file(mp3)
        segments: list = detect_sound(mp3_segment)
        if len(segments) > 1:
            mp3_segment = mp3_segment[segments[0][0]:segments[-1][1]]
        if mp3_segment.duration_seconds > max_duration:
            continue
        audio: AudioSegment = AudioSegment.silent(125, 22050)
        audio = audio.append(mp3_segment, crossfade=0)
        audio = audio.append(AudioSegment.silent(125, 22050))
        audio = effects.normalize(audio)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(22050)
        audio.export(wav, format="wav")
        totalLength += audio.duration_seconds
        if shortestLength < 0 or shortestLength > audio.duration_seconds:
            shortestLength = audio.duration_seconds
        if longestLength < audio.duration_seconds:
            longestLength = audio.duration_seconds
        vid: str = speaker
        if vid in voiceids.keys():
            vid = voiceids[vid]
        if vid == "?":
            vid = voiceid
        rows.append(f"{id:06d}|{vid}|chr|{wav}|||{text}|")
        id += 1

    totalLength = int(totalLength)
    minutes = int(totalLength / 60)
    seconds = int(totalLength % 60)
    print(f"Total duration: {minutes:,}:{seconds:02}")

    shortestLength = int(shortestLength)
    minutes = int(shortestLength / 60)
    seconds = int(shortestLength % 60)
    print(f"Shortest duration: {minutes:,}:{seconds:02}")

    longestLength = int(longestLength)
    minutes = int(longestLength / 60)
    seconds = int(longestLength % 60)
    print(f"Longest duration: {minutes:,}:{seconds:02}")

    print("Creating training files")
    # save all copy before shuffling
    with open("all.txt", "w") as f:
        for line in rows:
            f.write(line)
            f.write("\n")

    # create train/val sets
    random.Random(id).shuffle(rows)
    trainSize: int = (int)(len(rows) * .95)
    valSize: int = len(rows) - trainSize

    with open("train.txt", "w") as f:
        for line in rows[:trainSize]:
            f.write(line)
            f.write("\n")

    with open("val.txt", "w") as f:
        for line in rows[trainSize:]:
            f.write(line)
            f.write("\n")

    print(f"Train size: {trainSize}")
    print(f"Val size: {valSize}")
    print(f"All size: {len(rows)}")
    print("Folder:", pathlib.Path(".").resolve().name)

    sys.exit()
