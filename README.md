# Text-to-Speech
A small python project that converts text or SSML to speech using Google's TTS API.

As of now, works only on Windows (as far as I know)!

#Install FFmpeg
## Visit the FFmpeg Official Website and download the FFmpeg build for Windows.
Choose the "ffmpeg-6.0-full_build" or a newer version.  
Once the download is complete, extract the files from the zip folder.  
## Add FFmpeg to your System Path
Locate the bin folder inside the extracted FFmpeg directory.  
Copy the path to this folder.  
Open the System Properties (Right-click on 'This PC' > Properties > Advanced system settings).  
Click on 'Environment Variables'.  
In the 'System Variables' section, find and select the 'Path' variable, then click 'Edit'.  
Click 'New' and paste the path to the FFmpeg bin folder.  
Click 'OK' to close all dialogs.  
## Verify the Installation
Open Command Prompt and type ffmpeg -version.  
If FFmpeg is installed correctly, you should see the version information displayed.

Before you can use the program, you need an API key for Google's TTS API as ".json" file.  
Put this .json file wherever you want on your computer, then navigate to the environment variables  (see above)  
and add an entry to your system environment variables that looks like this:  
name: GOOGLE_APPLICATION_CREDENTIALS  
value: C:\Path\to\your\API\key\whatever-you-called-your-file.json  

After that, you can edit any of the constants at the beginning of the code (main.py) to your liking
and you should be good to go.

Remember to monitor the costs of your API usage.
