import os
import subprocess
ffmpeg_path = 'C:\\Users\\wyk\\PycharmProjects\\audio-detect\\ffmpeg-4.4-full_build\\bin\\ffmpeg.exe' # On Windows, you will probably need this to be \path\to\ffmpeg.exe
content_path="C:\\Users\\wyk\\PycharmProjects\\arisa\\src\\poc\\cache\\encore-une-histoire"
for file in [i for i in os.listdir("C:\\Users\\wyk\\PycharmProjects\\arisa\\src\\poc\\cache\\encore-une-histoire") if i.endswith(".mp3")]:
    subprocess.call([ffmpeg_path, '-ss', "0", '-t', str(60), '-i', f"{content_path}\\{file}", '-acodec', 'copy', '-y',
                     f".\\samples_mp3\\{file}"])
