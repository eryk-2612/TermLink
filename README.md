# TermLink
Build using pygame and curses. 
- Needs a "data" folder to operate and at least one json describing the Terminal in the "data" folder. 
  - Use the example.json or example_chat.json as a template.
- UI language is easy to change by editing tokens.json 
- AI Chat only supports LM Studio API

- See the NEW QUICK START GUIDE: https://github.com/eryk-2612/TermLink/blob/380f7840d849195a11368224223b3df8ab7cf5ae/docs/Quick%20Start%20Guide.md

## Dependencies
  - pip install windows-curses
  - pip install pygame-ce 
  - pip install requests

## Features
- customize your terminal using the example json files from the data/ folder
- Support for two types of terminals:
  - explorer
    - a fake file explorer
  - chat
    - an LLM chat interface
- Lock each terminal or entries (for an explorer type terminal) with a passcode
- Entry Types:
  - text
    - just plain text
  - button
    - when pressed shows a popup
  - switch
    - can change states
  - audio
    - can play an audio file
  - quit
    - optional button to leave the specific terminal
- **Languages**: 
  - update locales/tokens.json to your needs, I provided an english example in en_tokens.json (just rename the files)

## Recommendation
- I recommend to use https://github.com/FiniteSingularity/obs-retro-effects for nice visual effects

## Screenshots
<img width="1115" height="586" alt="image" src="https://github.com/user-attachments/assets/2ca1ae0b-c5c5-43bd-86d9-a6da0d63f985" />

## Video
https://github.com/user-attachments/assets/2f0e48ea-7b95-4f3d-9fcb-09f97fcf8e0c
