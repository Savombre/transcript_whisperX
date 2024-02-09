############################# IMPORTS #############################

from pydub import AudioSegment
import os

############################# CONSTANTS #############################

PATH = os.getcwd() + "/"

############################# FUNCTIONS #############################

def cut_a_file(filename_root, filename_extension, folder, duration):
    #Duration have to be in minutes

    audio_file = AudioSegment.from_file(f"audios/{folder}/raw/{filename_root}{filename_extension}", format=filename_extension[1:])
    pydub_duration = duration * 60 * 1000

    for i in range(0, len(audio_file), pydub_duration):
        step = int(i/pydub_duration) + 1
        os.makedirs(f'audios/{folder}/cutted/{filename_root}/', exist_ok=True)
        audio_file[i : i + pydub_duration].export(f"audios/{folder}/cutted/{filename_root}/{step}_{filename_root}.mp3", format="mp3")

def extract_filename_number(file):
    number = file.split('_')[0]
    return int(number)

def reunite_transcripts(text,file_path):
    with open(file_path, "a") as file:
        file.write("\n\n\n--------------------------------------\n\n\n" + str(text))