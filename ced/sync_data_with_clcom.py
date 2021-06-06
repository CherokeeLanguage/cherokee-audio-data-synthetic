#!/usr/bin/env -S conda run -n cherokee-audio-data python
import os
import sys

if __name__ == "__main__":
    os.system("ssh clcom@vhost.cherokeelessons.com mkdir /home/CED-AudioQualityVote/audio 2> /dev/null")

    for speaker in ["360-en-m"]:
        print(f"Syncing {speaker}", flush=True)
        os.system(f"ssh clcom@vhost.cherokeelessons.com mkdir -p /home/CED-AudioQualityVote/audio/{speaker} 2> /dev/null")
        rsync: str = f"rsync --delete-before -a --verbose --progress --human-readable {speaker}/ " \
                     f"clcom@vhost.cherokeelessons.com:/home/CED-AudioQualityVote/audio/{speaker}/ "
        os.system(rsync)

    sys.exit()
