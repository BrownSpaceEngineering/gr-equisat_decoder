#!/usr/bin/env bash
# converts all .ogg files to .wav files in the current directory
find ./*.ogg -exec ffmpeg -i {} {}.wav \;
