#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import math


def convert_to_seconds(time):
    time = time.split(":")
    hours = 0
    minutes = 0
    seconds = 0
    if len(time) == 2:
        minutes, seconds = time[0], time[1]
    else:
        hours, minutes, seconds = time[0], time[1], time[2]
    hours = int(hours)
    minutes = int(minutes)
    seconds = float(seconds)
    result = int(3600 * hours + 60 * minutes + seconds)
    return result


def find(s, ch):  # gives indexes of all of the spaces so we don't split words apart
    return [i for i, ltr in enumerate(s) if ltr == ch]


def transcript_to_vtt(transcript: str, duration: float) -> str:
    pieceLength = 68
    wordIndexes = find(transcript, " ")
    splitIndex = [0]
    for k in range(1, len(wordIndexes)):
        for l in range(1, len(wordIndexes)):
            if wordIndexes[l] > pieceLength * k:
                splitIndex.append(wordIndexes[l])
                break
    splitIndex.append(len(transcript))
    amountOfChunks = math.ceil(len(transcript) / pieceLength)
    vtt_str = "WEBVTT FILE:\n\n"
    for j in range(len(splitIndex) - 1):  # this uses a constant piece length
        secondsStart = round((duration / amountOfChunks) * j, 2) + 0.85
        secondsEnd = round((duration / amountOfChunks) * (j + 1), 2) + 0.85
        outputStart = (
            str(math.floor(secondsStart / 60)).zfill(2)
            + ":"
            + ("%.3f" % (secondsStart % 60)).zfill(6)
        )
        outputEnd = (
            str(math.floor(secondsEnd / 60)).zfill(2)
            + ":"
            + ("%.3f" % (secondsEnd % 60)).zfill(6)
        )
        vtt_str += f"00:{outputStart} --> 00:{outputEnd}\n"
        vtt_str += f"{transcript[splitIndex[j] : splitIndex[j + 1]]}\n\n"
    return vtt_str
