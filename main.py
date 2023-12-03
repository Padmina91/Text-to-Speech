import io
import os
from google.cloud import texttospeech
from google.api_core.exceptions import InvalidArgument
import pydub
import re

# ------ constant variable definitions ------

NPC_PROSODY = "<prosody rate=\"medium\" pitch=\"medium\" volume=\"0dB\">"
# If there's different characters talking, you can make that audible by giving each character their own prosody, pitch, volume etc.
# This is ONLY possible if you use SSML. You need to define a new constant here for each situation, then prepend the dialogue with the name
# of the constant in brackets. Plus you have to add the constant to the method "replace_dialogue_prosody(ssml)" by simply copy-pasting the line
# ssml = ssml.replace("(NPC)", f"{NPC_PROSODY}") and replacing the "NPC" with whatever you called your constant. There's no need to explicitly
# reset the prosody etc after the dialogue closes because the code does that automatically.
# Read the SSML documentation for further information on what options you have to manipulate the voice.


OUTPUT_DIRECTORY = "outputs" # directory gets created if it does not already exist
TEXT_FILE_NAME = "Curse of Blades 34.txt" # Replace with actual file name
OUTPUT_FILE_NAME = "Curse of Blades 34.mp3" # name of the output file. Change name if needed.
IS_PURE_TEXT = True # if SSML format is in use, change this variable to False. Otherwise True.
DIALOGUE_MARKER = '"' # if the dialogue marker is different in your text, change it here.
LANGUAGE_CODE = "en-GB" # change to the appropriate language (check API documentation for the correct string representation)
VOICE = "en-US-Wavenet-J" # change to your preferred voice (check API documentation for the available voices)

output_file_path = os.path.join(OUTPUT_DIRECTORY, OUTPUT_FILE_NAME)

# ------ method definitions ------

def replace_special_breaks(chunk):
    # This function replaces certain special characters in the text with SSML break tags.
    # The '...' is replaced with a 2 second break, '~~~' with a 2 second break, and '—' (the em-dash) with a 1 second break.
    chunk = chunk.replace("...", " <break time=\"1s\"/>")
    chunk = chunk.replace("~~~", "<break time=\"2s\"/>")
    chunk = chunk.replace("—", "<break time=\"1s\"/>")
    return chunk

def split_at_quotation_marks(paragraph):
    # Initialize a list to store the chunks
    chunks = []
    # Initialize variables for tracking
    within_dialogue = False
    current_chunk = ""
    # Iterate over each character in the paragraph
    for char in paragraph:
        if char == DIALOGUE_MARKER:
            if within_dialogue:
                # append the quotation mark at the end of the dialogue and reset prosody settings to normal
                current_chunk += char
                current_chunk += "</prosody>" # Close the prosody tag
            # Toggle the dialogue state
            within_dialogue = not within_dialogue
            # Add the current chunk to the list and reset it
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            if within_dialogue:
                # insert the starting quotation mark at the beginning of the dialogue
                current_chunk += char
        else:
            # Add the character to the current chunk
            current_chunk += char
    # Add the last chunk to the list
    chunks.append(current_chunk)
    return chunks

def replace_dialogue_prosody(ssml):
    # This function replaces certain character names in the text with SSML prosody tags.
    # The character names are enclosed in brackets, and the corresponding prosody tag is defined as a constant at the start of the script.
    ssml = ssml.replace("(NPC)", f"{NPC_PROSODY}")
    return ssml

def split_into_paragraphs(ssml):
    # Split the SSML into paragraphs based on newline characters
    paragraphs = ssml.split("\n")
    # Initialize a list to store the result
    result = []
    # Iterate over each paragraph
    for paragraph in paragraphs:
        # Split the paragraph at double quotation marks while preserving the quotation marks
        paragraph_chunks = split_at_quotation_marks(paragraph)
        # Add the resulting chunks to the result list
        result.extend(paragraph_chunks)
    return result

def synthesize_speech(ssml):
    # This function uses Google's Text-to-Speech API to synthesize speech from the provided SSML.
    # It sets the input text, voice parameters, and audio configuration, then makes the API call.
    # If the API call is successful, it returns the audio data. If not, it prints the error and returns None.
    input_text = texttospeech.SynthesisInput(ssml=ssml)
    voice = texttospeech.VoiceSelectionParams(
        language_code=LANGUAGE_CODE,
        ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        name=VOICE)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    try:
        response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
        return response.audio_content
    except InvalidArgument as err:
        print(f"Error: {err}")
        return None

def split_ssml(ssml, max_bytes=3000):
    # Split SSML into paragraphs
    paragraphs = split_into_paragraphs(ssml)
    # Initialize result list and current chunk
    result = []
    chunk = "<speak><break time=\"1s\"/>"
    for paragraph in paragraphs:
        # Strip leading and trailing whitespace from the paragraph
        paragraph = paragraph.strip()
        # Calculate the byte lengths of the current chunk and the paragraph
        paragraph_bytes = len(paragraph.encode("utf-8"))
        chunk_bytes = len(chunk.encode("utf-8"))
        if chunk_bytes + paragraph_bytes + len("</speak>") > max_bytes:
            # If adding the paragraph would exceed the maximum byte limit, complete the current chunk and add it to the result
            # But first, check if the chunk ends in the middle of a dialogue
            if chunk.count('"') % 2 != 0 or re.search(r"\(.*\)$", chunk):
                # If it does, move the entire dialogue or annotation to the next chunk
                last_special_start = max(chunk.rfind('"'), chunk.rfind("("))
                paragraph = chunk[last_special_start:] + paragraph
                chunk = chunk[:last_special_start]
            chunk += "</speak>"
            chunk = replace_special_breaks(chunk)
            result.append(chunk.strip())
            # Start a new chunk
            chunk = "<speak><break time=\"1s\"/>"
        # Add the paragraph to the current chunk with a break tag
        chunk += f"{paragraph}<break time=\"1s\"/>"
        chunk = replace_dialogue_prosody(chunk)
    # If there is remaining content in the last chunk, complete it and add it to the result
    if chunk.strip() != "<speak><break time=\"1s\"/>":
        chunk = replace_special_breaks(chunk)
        chunk += "</speak>"
        result.append(chunk.strip())
    return result

def split_text(text, max_bytes=4000):
    segments = text.split('.')
    result = []
    chunk = ""
    for segment in segments:
        next_char = ""
        if len(segment) > 0 and segment[-1] in ['"', '”', '’', "'"]:
            next_char = segment[-1]
            segment = segment[:-1]
        segment_bytes = len((segment + next_char).encode("utf-8"))
        chunk_bytes = len(chunk.encode("utf-8"))
        if chunk_bytes + segment_bytes + len(".") > max_bytes:
            result.append(chunk.strip())
            chunk = ""
        chunk += f"{segment}.{next_char}"
    if chunk.strip() != "":
        result.append(chunk.strip())
    return result

def concatenate_audio_files(audio_data_list, output_file):
    # This function concatenates multiple audio files into one.
    # It creates a silent audio segment, then iterates over the audio data list.
    # For each item in the list, it creates an audio segment from the data and adds it to the output.
    # Finally, it exports the output as an MP3 file.
    output = pydub.AudioSegment.silent(duration=0)
    for audio_data in audio_data_list:
        segment = pydub.AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
        output += segment
    output.export(output_file, format="mp3")


# ------ start of actual code ------
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    client = texttospeech.TextToSpeechClient()
    with open(f"./resources/{TEXT_FILE_NAME}", "r", encoding="utf-8") as file:
        ssml_content = file.read()
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
    if IS_PURE_TEXT:
        chunks = split_text(ssml_content)
    else:
        chunks = split_ssml(ssml_content)
    temp_audio_data = []
    for chunk in chunks:
        audio_data = synthesize_speech(chunk)
        if audio_data is not None:
            temp_audio_data.append(audio_data)
    concatenate_audio_files(temp_audio_data, output_file_path)
    print("Generated " + output_file_path)
