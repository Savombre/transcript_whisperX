############################# IMPORTS #############################

from transcript_manager import make_transcription

############################# MAIN #############################

if __name__ == "__main__":


    folders_to_work_on = ["feb24"]

    for folder in folders_to_work_on :
        make_transcription(folder=folder)
