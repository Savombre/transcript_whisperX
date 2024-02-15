############################# IMPORTS #############################

import json
import os
from dotenv import load_dotenv, find_dotenv
import re
import replicate

from cutter import cut_a_file, extract_filename_number ,reunite_transcripts

############################# CONSTANTS #############################

PATH = os.getcwd() + "/"
_ = load_dotenv(find_dotenv() )
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

############################# FUNCTIONS #############################

def get_transcript_from_replicate_public_api(replicate_client,audio_file):
    output = replicate_client.run(
        "thomasmol/whisper-diarization:7fa6110280767642cf5a357e4273f27ec10ebb60c107be25d6e15f928fd03147",
        input={
            "file": audio_file,
            "group_segments": True,
            "offset_seconds": 0,
            "language": "fr",
        }
    )
    return output

def get_transcript_from_replicate_private_api(replicate_client,audio_file):
    deployment = replicate_client.deployments.get("savombre/whisperx-transcription")
    prediction = deployment.predictions.create(
    input={
            "file": audio_file,
            "group_segments": True,
            "offset_seconds": 0,
            "language": "fr",
        }
    )
    prediction.wait()

    return prediction.output

def format_timestamps(timestamps):
    minutes = int(float(timestamps)) // 60  
    secondes = int(float(timestamps)) % 60
    # Formatage pour ajouter un zéro devant les secondes si nécessaire
    return f"{minutes}.{secondes:02d}"


def clean_json_transcript(json_transcript):

    for segment in json_transcript["segments"]:
        if "words" in segment:
            del segment["words"]
        if "start" in segment :
            segment["start"] = format_timestamps(segment["start"])
        if "end" in segment :
            segment["end"] = format_timestamps(segment["end"])

    return json_transcript

def create_txt_file(transcript_json, path_to_save):
    loaded_transcript_json = json.loads(transcript_json)

    lines = ["Number of speakers detected : " + str(loaded_transcript_json['num_speakers']) + "\n"]

    for segment in loaded_transcript_json['segments']:  
        line = f'{segment["speaker"]} [{segment["start"]} -> {segment["end"]}] : "{segment["text"]}"'
        lines.append(line)
    

    final_text = "\n\n".join(lines)

    # with open(path_to_save, 'w', encoding='utf-8') as file:
    #     file.write(final_text)

    reunite_transcripts(text=final_text,file_path=path_to_save)


def adjust_timecodes(transcript) :

    timecode_pattern = re.compile(r'SPEAKER_(\d+) \[(\d+\.\d+) -> (\d+\.\d+)\]')
    indicator_pattern = re.compile(r'Number of speakers detected')
    offset = -5
    adjusted_transcript = []

    for line in transcript.split('\n'):
        # Detect the indicator line for resetting
        if indicator_pattern.search(line):
            offset += 5  # Add 5 minutes to the offset

        timecode_match = timecode_pattern.search(line)
        if timecode_match:
            speaker_id, start, end = map(float, timecode_match.groups())
            # Adjust the timecodes
            adjusted_start = start + offset
            adjusted_end = end + offset
            line = timecode_pattern.sub(f'SPEAKER_{int(speaker_id)} [{adjusted_start:.2f} -> {adjusted_end:.2f}]', line)

        adjusted_transcript.append(line)


    return '\n'.join(adjusted_transcript)

def clean_final_transcript(transcript_path) :
    try:
        with open(transcript_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        adjusted_content = adjust_timecodes(content)
        
        with open(transcript_path, 'w', encoding='utf-8') as adjusted_file:
            adjusted_file.write(adjusted_content)
        
    except Exception as e:
        print(f'Erreur : {e}')

def make_transcription(folder) : 

    replicate_client = replicate.Client(REPLICATE_API_TOKEN)
    filenames = os.listdir(PATH + f"audios/{folder}/raw")

    for filename in filenames :

        print(f"{filename} transcription started 🚀")
        filename_root, filename_extension = os.path.splitext(filename)
        cut_a_file(filename_root, filename_extension, folder, duration=5)
        cutted_filenames = os.listdir(PATH + f"audios/{folder}/cutted/{filename_root}")
        print(f"--> {filename} cutted in {len(cutted_filenames)} parts ✂️")

        for cutted_filename in sorted(cutted_filenames, key=extract_filename_number) : 

            audio_file_path = PATH + f"audios/{folder}/cutted/{filename_root}/{cutted_filename}"
            audio_file = open(audio_file_path,"rb")

            json_transcript = get_transcript_from_replicate_private_api(replicate_client,audio_file)
            cleaned_json_transcript = clean_json_transcript(json_transcript)
            formated_json = json.dumps(cleaned_json_transcript, indent=4, ensure_ascii=False)

            path_to_save = PATH + f"transcripts/{folder}/{filename_root}.txt"
            create_txt_file(formated_json,path_to_save)
            print(f"----> {cutted_filename} transcription appended 👌")


        clean_final_transcript(PATH + f"transcripts/{folder}/{filename_root}.txt")
        print(f"--> Transcript's timecodes adjusted 🔧")

        print(f"--> {filename} transcription done ✅ \n")

        
############################# MAIN #############################
        
if __name__ == "__main__":

    clean_final_transcript("/Users/savombre/Documents/Code/Evelyn/transcript_whisperX/transcripts/st-valentin/Entretien en amont FEST 1 Abel  2.txt")

    #replicate_client = replicate.Client(REPLICATE_API_TOKEN)

    # filename = "Coralie FEST2 - Entretien après la M. en Situation.m4a"
    # folder="feb24"

    # print(f"{filename} transcription started 🚀")

    # filename_root, filename_extension = os.path.splitext(filename)
    # cut_a_file(filename_root, filename_extension, folder, duration=5)
    # cutted_filenames = os.listdir(PATH + f"audios/{folder}/cutted/{filename_root}")
    # print(f"--> {filename} cutted in {len(cutted_filenames)} parts ✂️")

    # for cutted_filename in sorted(cutted_filenames, key=extract_filename_number) : 

    #     audio_file_path = PATH + f"audios/{folder}/cutted/{filename_root}/{cutted_filename}"
    #     audio_file = open(audio_file_path,"rb")

    #     json_transcript = get_transcript_from_replicate_private_api(replicate_client,audio_file)
    #     cleaned_json_transcript = clean_json_transcript(json_transcript)
    #     formated_json = json.dumps(cleaned_json_transcript, indent=4, ensure_ascii=False)

    #     path_to_save = PATH + f"transcripts/{folder}/{filename_root}.txt"
    #     create_txt_file(formated_json,path_to_save)
    #     print(f"----> {cutted_filename} transcription appended 👌")

    # print(f"--> {filename} transcription done ✅ \n")
    