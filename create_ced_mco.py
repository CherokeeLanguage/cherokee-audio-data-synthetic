#!/usr/bin/env -S conda run -n cherokee-audio-data python

import os
import sys
import unicodedata as ud
import re
import csv
from typing import List

from chrutils import ascii_ced2mco

if __name__ == "__main__":

    os.chdir(os.path.dirname(__file__))

    CED: str = "full_dictionary_202106051036.csv"
    CEDMCO: str = "ced-mco-alt.txt"

    PRESENT_3RD: str = "entrytone"
    PRESENT_3RD_PLURAL: str = "nounadjpluraltone"
    PRESENT_1ST: str = "vfirstprestone"
    IMMEDIATE_2ND: str = "vsecondimpertone"
    DEVERBAL_3RD: str = "vthirdinftone"
    REMOTE_3RD: str = "vthirdpasttone"
    HABITUAL_3RD: str = "vthirdprestone"

    PRONOUNCE_KEYS: List[str] = [PRESENT_3RD, PRESENT_3RD_PLURAL, PRESENT_1ST, IMMEDIATE_2ND, DEVERBAL_3RD,
                                 REMOTE_3RD, HABITUAL_3RD]

    PRESENT_3RD_SYLLABARY: str = "syllabaryb"
    PRESENT_3RD_PLURAL_SYLLABARY: str = "nounadjpluralsyllf"
    PRESENT_1ST_SYLLABARY: str = "vfirstpresh"
    IMMEDIATE_2ND_SYLLABARY: str = "vsecondimpersylln"
    DEVERBAL_3RD_SYLLABARY: str = "vthirdinfsyllp"
    REMOTE_3RD_SYLLABARY: str = "vthirdpastsyllj"
    HABITUAL_3RD_SYLLABARY: str = "vthirdpressylll"

    SYLLABARY_KEYS: List[str] = [PRESENT_3RD_SYLLABARY, PRESENT_3RD_PLURAL_SYLLABARY, PRESENT_1ST_SYLLABARY,
                                 IMMEDIATE_2ND_SYLLABARY, DEVERBAL_3RD_SYLLABARY, REMOTE_3RD_SYLLABARY,
                                 HABITUAL_3RD_SYLLABARY]

    DEFINITION: str = "definitiond"

    ced2mco = []

    CGRAVEACCENT = "\u0300"
    CACUTEACCENT = "\u0301"
    CCARON = "\u0302"
    CMACRON = "\u0304"
    CDOUBLEACUTE = "\u030b"
    CCIRCUMFLEX = "\u030c"
    CMACRONBELOW = "\u0331"

    # Build guessing pronunciation lookup for transliterated text
    with open(CED, "r", newline='', encoding='utf-8-sig') as csvfile:
        rows = csv.DictReader(csvfile)
        for row in rows:
            if row["source"] != "ced":
                continue
            entry_id: str = row["id"]
            if not re.match("\\d+", entry_id):
                continue

            #if "99713" == entry_id:
            #    continue

            values: List[str]
            syl_values: List[str]
            for (key, syl_key) in zip(PRONOUNCE_KEYS, SYLLABARY_KEYS):
                pronounce: str = row[key]
                syllabary: str = row[syl_key]

                values = [pronounce]
                syl_values = [syllabary]
                if "," in pronounce and "," in syllabary:
                    psplit: List[str] = pronounce.split(",")
                    ssplit: List[str] = syllabary.split(",")
                    if len(psplit) == len(ssplit):
                        values = psplit
                        syl_values = ssplit

                idx: int = 0
                value: str
                syl_value: str
                for (value, syl_value) in zip(values, syl_values):
                    value = value.strip()
                    syl_value = syl_value.strip()
                    if not value or not syl_value:
                        continue

                    value = ud.normalize("NFC", ascii_ced2mco(value)).lower().capitalize()
                    syl_value = ud.normalize("NFC", syl_value.upper())

                    if "--" in value or "--" in syl_value:
                        continue
                    if value.startswith("-") or syl_value.startswith("-"):
                        continue
                    if value.endswith("-") or syl_value.endswith("-"):
                        continue

                    if value[-1] not in ".?!":
                        value += "."

                    definition: str = row[DEFINITION].capitalize()

                    if "see Gram." in definition:
                        continue

                    # definition = definition.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt")

                    definition = re.sub("(?i)\\b(she), (it)'s", "\\1 is", definition)
                    definition = re.sub("(?i)\\b(he), (it)'s", "\\1 is", definition)
                    definition = re.sub("(?i)\\b(it)'s", "\\1 is", definition)
                    definition = re.sub("(?i)\\b(she)'s", "\\1 is", definition)
                    definition = re.sub("(?i)\\b(he)'s", "\\1 is", definition)

                    if key == PRESENT_3RD_PLURAL:
                        definition += " (plural)"

                    if key == PRESENT_1ST:
                        definition = re.sub("(?i)\\b(she) (is)", "I am", definition)
                        definition = re.sub("(?i)\\b(he) (is)", "I am", definition)
                        definition = re.sub("(?i)\\b(it) (is)", "I am", definition)
                        definition = re.sub("(?i)\\b(she) (has)", "I have", definition)
                        definition = re.sub("(?i)\\b(he) (has)", "I have", definition)
                        definition = re.sub("(?i)\\b(it) (has)", "I have", definition)
                        definition = re.sub("(?i)\\b(himself|herself|itself)", "myself", definition)
                        definition += " (I am...)"

                    if key == IMMEDIATE_2ND:
                        definition = re.sub("(?i)\\b(she) (is)", "Let you be", definition)
                        definition = re.sub("(?i)\\b(he) (is)", "Let you be", definition)
                        definition = re.sub("(?i)\\b(it) (is)", "Let you be", definition)
                        definition = re.sub("(?i)\\b(she) (has)", "Let you have", definition)
                        definition = re.sub("(?i)\\b(he) (has)", "Let you have", definition)
                        definition = re.sub("(?i)\\b(it) (has)", "Let you have", definition)
                        definition += " (Let you...)"

                    if key == DEVERBAL_3RD:
                        definition = re.sub("(?i)\\b(she) (is)", "For her to be", definition)
                        definition = re.sub("(?i)\\b(he) (is)", "For him to be", definition)
                        definition = re.sub("(?i)\\b(it) (is)", "For him to be", definition)
                        definition = re.sub("(?i)\\b(she) (has)", "For her to have", definition)
                        definition = re.sub("(?i)\\b(he) (has)", "For him to have", definition)
                        definition = re.sub("(?i)\\b(it) (has)", "For him to have", definition)
                        definition += " (For him to...)"

                    if key == REMOTE_3RD:
                        definition = re.sub("(?i)\\b(she) (is)", "A while ago she did", definition)
                        definition = re.sub("(?i)\\b(he) (is)", "A while ago he did", definition)
                        definition = re.sub("(?i)\\b(it) (is)", "A while ago he did", definition)

                        definition = re.sub("(?i)\\bA while ago she (did \\w+)ing", "She \\1", definition)
                        definition = re.sub("(?i)\\bA while ago he (did \\w+)ing", "He \\1", definition)

                        definition = re.sub("(?i)\\b(she) (has)", "A while ago she had", definition)
                        definition = re.sub("(?i)\\b(he) (has)", "A while ago he had", definition)
                        definition = re.sub("(?i)\\b(it) (has)", "A while ago he had", definition)

                        definition += " (He did...a while ago)"

                    if key == HABITUAL_3RD:
                        definition = re.sub("(?i)\\b(she) (is)", "\\1 \\2 usually", definition)
                        definition = re.sub("(?i)\\b(he) (is)", "\\1 \\2 usually", definition)
                        definition = re.sub("(?i)\\b(it) (is)", "\\1 \\2 usually", definition)

                        definition = re.sub("(?i)\\b(she) (has)", "\\1 usually \\2", definition)
                        definition = re.sub("(?i)\\b(he) (has)", "\\1 usually \\2", definition)
                        definition = re.sub("(?i)\\b(it) (has)", "\\1 usually \\2", definition)

                        definition += " (He usually...)"

                    idx += 1
                    ced2mco.append(f"{entry_id}-{idx}-{key.lower()}|{syl_value}|{value}|{definition}")

    with  open(CEDMCO, "w") as f:
        for line in ced2mco:
            f.write(line)
            f.write("\n")

    sys.exit()
