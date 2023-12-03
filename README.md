# Text-to-Speech
A small python project that converts text or SSML to speech using Google's TTS API.

As of now, works only on Windows (as far as I know)!
Before you can use the program, you need an API key as .json file.
Put this .json file wherever you want on your computer, then navigate to the environment variables
and add an entry to your system environment variables that looks like this:
name: GOOGLE_APPLICATION_CREDENTIALS
value: C:\Path\to\your\API\key\whatever-you-called-your-file.json

After that, you can edit any of the constants at the beginning of the code (main.py) to your liking
and you should be good to go.

Remember to monitor the costs of your API usage.
