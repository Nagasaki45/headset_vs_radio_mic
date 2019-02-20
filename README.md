This is an attempt to test the effect of moving from the HTC Vive internal microphone to a radio mic on IBM Watson speech-to-text results. We didn't expect any difference, but apparently there are many.

First, install dependencies with `pip install -r requirements.txt` (or even better, use pip-tools).

If you want to regenerate the transcripts obtain credentials from IBM as [described here](https://watson-streaming.readthedocs.io/en/latest/installation.html), place the `credentials.json` in the root directory of this project, and run `python prepare_transcripts.py`.

Start the analysis notebook with `jupyter-notebook`.
