# TTS-Automation

This folder consists of 2 different parts for the TTS Automation which consists of TTS Loans and TTS KFS.

<h1>TTS Loans</h1>

This part of the project aims to help in automating the script generation using Microsoft Azure Speech AI service.
The scripts would be done for the static part of the audio which consists of 3 products. 
1. Quick Cash (QC)
2. EPP 1
3. EPP 2

It is also possible to use this automation for any other audio file generation.

The audio will also be generated using 3 languages being english, chinese and cantonese.

<h1>TTS KFS</h1>

This automation process here is to compare the list from prive and the list from the internal DB to check for any outdated funds that needs to be updated.

Important files:
1. TTS_KFS_Updates.py
This is the main code to run the comparisons between the dates from prive and TTS internal DB.

2. Updated_TTS_FUNDS_Results.csv
This is output of the main code required for manual update on TTS Scraper UI.

<h1>TTS webapp</h1>

In this folder, it contains the POC of the TTS UI created for easy audio generation without the need of having someone with technical background to run the codes. However, the codes here are not completed and requires additional work to improve the user experience

Important files:
1. script_automation.py
This is the backend function of the UI to generate audio files with the edited text file on the UI.

2. app.py
This is the main code to run the UI for testing. Main framework is using Flask.