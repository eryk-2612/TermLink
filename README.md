# TermLink

TermLink is a customizable retro-style terminal interface built with Python, `curses`, and Pygame. Create fictional computer terminals from JSON files, browse information in Explorer terminals, or connect a Chat terminal to a compatible local AI service.

**Created with AI assistance.**

## Features

- Create multiple terminals and launch them from the main menu.
- Build Explorer terminals with categories, entries, optional passcodes, and interactive controls.
- Create Chat terminals that send prompts to an LM Studio-compatible API endpoint.
- Load a complete Explorer or Chat terminal from a removable disk using **Load from Disk**.
- Import individual categories from a disk while using an Explorer terminal.
- Customize interface text through `locales/tokens.json`.

## Requirements

- Python 3.10 or later
- Pygame CE
- Requests
- On Windows, `windows-curses`
- For disk detection on Linux, `lsblk` and `udisksctl` (usually provided by `util-linux` and `udisks2`)

Install the Python dependencies:

```bash
python -m pip install pygame-ce requests
```

On Windows, also install curses support:

```bash
python -m pip install windows-curses
```

## Run TermLink

Keep `main.py` in the project directory. TermLink loads optional local terminal JSON files from `data/` and reads interface strings from `locales/tokens.json` when that file is available.

Start the application from the project directory:

```bash
python main.py
```

Local terminal JSON files are optional. If `data/` is missing or contains no JSON files, the main menu still opens with **Load from Disk** and **Leave**, so you can use terminals stored on removable media. The project includes `data/example.json` and `data/example_chat.json` as optional starting points. Chat instruction files and audio assets referenced by terminals must still be available in `data/`.

## Main menu and controls

- Use **Up** and **Down** to move through menu items and **Enter** to select one.
- **Load from Disk** is shown immediately above **Leave**. Insert a disk to scan it; press **Esc** to return to the main menu.
- If one complete terminal is found on the disk, it starts immediately. If several are found, choose one with **Up** and **Down**, then press **Enter**.
- In an Explorer terminal, use **Up** and **Down** to navigate, **Enter** to open a category or entry, and **Esc** to close the current entry or category. **Left** returns from an entry list to its category list. **Space** starts or stops audio.
- In a Chat terminal, type a message and press **Enter** to send it. Press **Esc** to leave the terminal.

## Create an Explorer terminal

An Explorer terminal is a JSON object with a `terminal` section, a title, a type, and a list of categories. Optional `unlock_code` values lock the whole terminal or an individual entry.

```json
{
  "terminal": {
    "title": "Research Terminal",
    "type": "explorer",
    "unlock_code": "password",
    "skip_signin": true,
    "categories": [
      {
        "title": "Logs",
        "entries": [
          {
            "title": "Welcome",
            "type": "text",
            "lines": ["System online.", "No incidents reported."],
            "unlock_code": "other_pwd"
          }
        ]
      }
    ]
  }
}
```

Set `skip_signin` to `true` to go directly to the normal boot sequence when this terminal is selected. The boot animation and any terminal passcode remain active. The default is `false`, so existing terminal files continue to show the sign-in screen.

### Explorer entry types

| Type | Fields | Behavior |
| --- | --- | --- |
| `text` | `lines` | Displays text lines. |
| `switch` | `default_state`, optional `state_labels`, `action_verbs` | Lets the user change a state with the arrow keys and confirm with **Enter**. |
| `button` | optional `default_state`, `state_labels`, `action_verbs`, `message` | Shows a message when activated. |
| `audio` | `audio` | Plays an audio file from the `data/` folder when the user presses **Space**. |
| `leave` | — | Returns directly to the main menu when opened. |
| `sign_out` | — | Restarts the terminal at its sign-in screen, even when `skip_signin` is `true`. |
| `quit` | — | Legacy alias for `leave`. |

For a switch or button, `state_labels` and `action_verbs` can be customized. If omitted, TermLink uses the default values from `locales/tokens.json`. An entry can also include an `unlock_code`.

Audio paths are relative to the `data/` folder. For example, an entry with `"audio": "audio/test.mp3"` uses `data/audio/test.mp3`.

## Create a Chat terminal

Chat terminals use the `chat` type and specify the model, API token, endpoint URL, and an instruction file. The instruction file is read from the `data/` folder.

```json
{
  "terminal": {
    "title": "Local Assistant",
    "type": "chat",
    "unlock_code": "password",
    "skip_signin": false,
    "model": "your-model-name",
    "apikey": "your-api-token",
    "url": "http://localhost:1234/api/v1/chat",
    "instruction_file": "prompt.txt"
  }
}
```

Place the referenced instruction file in `data/`. The configured service must accept the request and response format used by TermLink. `data/example_chat.json` and `data/prompt.txt` provide examples. Keep credentials local and do not commit real API tokens to a shared repository.

## Use removable disks

Disk support currently targets Linux and relies on the system identifying the medium as removable USB storage. The disk must have a recognized filesystem. TermLink uses `lsblk` to detect it and `udisksctl` to mount it.

### Load a complete terminal

Choose **Load from Disk** in the main menu and insert a disk with one or more `.json` files in its root directory. A file must contain a complete `terminal` object. Explorer and Chat terminal types are supported. A category-only JSON file does not count as a complete terminal. The interface displays a reading message while the disk is mounted and read. If no terminal is found, the screen waits for the disk to be ejected so another one can be inserted; **Esc** returns to the menu.

When loading a Chat terminal from disk, its `instruction_file` must also be available in the application's local `data/` folder. Audio referenced by an Explorer terminal is likewise read from the local `data/` folder.

### Import categories into an Explorer terminal

While an Explorer terminal is open, insert a disk containing JSON files in its root directory with a top-level `categories` array. Those categories are added temporarily to the Explorer and removed when the disk is ejected. This feature imports categories only; it does not start a terminal from those files.

Example category-only disk file:

```json
{
  "categories": [
    {
      "title": "Disk Archive",
      "entries": [
        {
          "title": "Recovered note",
          "type": "text",
          "lines": ["Data recovered from removable storage."]
        }
      ]
    }
  ]
}
```

## Customize the interface language

Edit the values in `locales/tokens.json` to change menu labels, prompts, and default entry text. Preserve the JSON keys and value types. `locales/de_tokens.json` is an additional German token set; the application currently loads `locales/tokens.json` at startup.

## Project layout

```text
controllers/   Input handling and application flow
core/          Constants, JSON loading, audio, and removable disk support
data/          Terminal definitions, prompts, and audio assets
locales/       Interface text
models/        Terminal, category, and entry data models
states/        UI state objects
views/         Curses-based screens
```

## Credits and related projects

TermLink was created with AI assistance. For retro visual effects in OBS, see [OBS Retro Effects](https://github.com/FiniteSingularity/obs-retro-effects).

## Screenshots

<img width="1115" alt="TermLink interface" src="https://github.com/user-attachments/assets/2ca1ae0b-c5c5-43bd-86d9-a6da0d63f985" />

## Video

[Watch the TermLink video](https://github.com/user-attachments/assets/2f0e48ea-7b95-4f3d-9fcb-09f97fcf8e0c)
