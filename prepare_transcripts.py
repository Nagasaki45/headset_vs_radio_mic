import concurrent.futures
import functools
import json
import os
import time
import wave

import deep_disfluency.asr.ibm_watson
import fluteline
import watson_streaming
import watson_streaming.utilities

CREDENTIALS_PATH = 'credentials.json'
WATSON_SETTINGS = {  # Copied from deep_disfluency_server
    'inactivity_timeout': -1,  # Don't kill me after 30 seconds
    'interim_results': True,
    'timestamps': True
}
AUDIO_DIR = 'audio'
TRANSCRIPTS_DIR = 'transcripts'
EXTRA_WAIT_IN_SECONDS = 20


def queue_generator(queue):
    while not queue.empty():
        yield queue.get()


def get_audio_duration(audio_filepath):
    with wave.open(audio_filepath) as f:
        return f.getnframes() / f.getframerate() / f.getnchannels()


def get_transcript_filepath(audio_filepath):
    return (
        audio_filepath
        .replace(AUDIO_DIR, TRANSCRIPTS_DIR)
        .replace('.wav', '.txt')
    )


def write_jsons(filepath, items):
    with open(filepath, 'w') as f:
        for item in items:
            json.dump(item, f)
            f.write('\n')


def transcribe(credentials, settings, audio_filepath):
    nodes = [
        watson_streaming.utilities.FileAudioGen(audio_filepath),
        watson_streaming.Transcriber(settings, credentials),
        deep_disfluency.asr.ibm_watson.IBMWatsonAdapter(),
    ]

    fluteline.connect(nodes)
    fluteline.start(nodes)

    try:
        time.sleep(get_audio_duration(audio_filepath) + EXTRA_WAIT_IN_SECONDS)
    finally:
        fluteline.stop(nodes)

    transcript_filepath = get_transcript_filepath(audio_filepath)
    os.makedirs(os.path.dirname(transcript_filepath), exist_ok=True)
    write_jsons(transcript_filepath, queue_generator(nodes[-1].output))


def audio_paths_generator(audio_dir):
    for dirpath, _, filenames in os.walk(audio_dir):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


def main():
    audio_filepaths = list(audio_paths_generator(AUDIO_DIR))
    f = functools.partial(transcribe, CREDENTIALS_PATH, WATSON_SETTINGS)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Consume the iterable to force raising exceptions
        list(executor.map(f, audio_filepaths))


if __name__ == '__main__':
    main()
