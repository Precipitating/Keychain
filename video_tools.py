import discord
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

import helper_functions
from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
import numpy as np

from twitter_downloader import DOWNLOAD_PATH


def remove_audio(videoPath: str, outputPath: str):
    finalVid = VideoFileClip(videoPath)
    finalVidAudioless = finalVid.without_audio()
    finalVidAudioless.write_videofile(outputPath, fps=60)
    finalVid.close()
    finalVidAudioless.close()


def bgm_add(videoPath: str, audioPath: str, outputPath: str):
    videoFile = VideoFileClip(videoPath)
    audioFile = AudioFileClip(audioPath)
    # loop audio to video length
    loopedAudio = audio_loop(audioFile, duration=videoFile.duration)
    # combine both tracks
    if videoFile.audio is not None:
        addedAudio = CompositeAudioClip([videoFile.audio, loopedAudio])
    else:
        addedAudio = CompositeAudioClip([loopedAudio])
    # set to source video
    final = videoFile.set_audio(addedAudio)
    # save to disk
    final.write_videofile(outputPath, fps=60)
    audioFile.close()
    videoFile.close()


def extract_audio(filePath: str, outputPath: str):
    mp3Format = outputPath.replace(helper_functions.extract_file_format(outputPath), "")
    mp3Format += ".mp3"
    print(mp3Format)
    vid = VideoFileClip(filePath)
    audio = vid.audio
    audio.write_audiofile(mp3Format)
    audio.close()
    vid.close()

    return mp3Format


def audio_concatenate(clips):
    durations = [c.duration for c in clips]
    tt = np.cumsum([0] + durations)  # start times, and end time.
    newclips = [c.set_start(t) for c, t in zip(clips, tt)]
    return CompositeAudioClip(newclips).set_duration(tt[-1])


def audio_loop(clip, duration):
    nloops = int(duration / clip.duration) + 1
    return audio_concatenate(nloops * [clip]).set_duration(duration)


def trim_video(downloadPath: str, start: int, end: int, outputPath: str):
    # check if duration is valid
    clip = VideoFileClip(downloadPath)
    if end > clip.duration:
        end = clip.duration
    if start < 0 or start > clip.duration:
        start = 0
    clip.close()

    ffmpeg_extract_subclip(downloadPath, start, end, outputPath)
