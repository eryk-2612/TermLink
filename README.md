# TermLink

TermLink lets you create and use fictional retro computer terminals. You can browse notes and files in an Explorer terminal, or use a Chat terminal connected to a compatible AI service.

## Screenshots

<img width="1920" height="1080" alt="TermLink main menu" src="https://github.com/user-attachments/assets/046b3567-f5ac-4b3c-8c1d-3ec7ce3e08bd" />
<img width="1920" height="1080" alt="TermLink Explorer terminal" src="https://github.com/user-attachments/assets/e724f640-804b-4208-b5d8-b3e284bc695f" />
<img width="1920" height="1080" alt="TermLink terminal screen" src="https://github.com/user-attachments/assets/d3de4929-8410-4654-84ff-7bff55f33aab" />
<img width="1920" height="1080" alt="TermLink terminal screen" src="https://github.com/user-attachments/assets/ca3e97e0-885b-4a25-a023-d8dc37966a96" />
<img width="1920" height="1080" alt="TermLink terminal screen" src="https://github.com/user-attachments/assets/39e11b82-77d1-420f-b741-6384b2b42339" />
<img width="1920" height="1080" alt="TermLink terminal screen" src="https://github.com/user-attachments/assets/c00204e5-afda-445c-9288-05185672506f" />

## Start here

### Linux: run the ready-to-use app

The project includes a ready-to-use app in `dist/`. Open a terminal in the TermLink folder and run:

```bash
./dist/main
```

If your computer says that you do not have permission to run it, right-click `dist/main`, open **Properties**, and enable **Allow executing file as a program**.

### Run from the Python source

You need Python 3.10 or later. Install the required packages:

```bash
python3 -m pip install pygame-ce requests
```

Then, from the project folder, start TermLink with:

```bash
python3 main.py
```

If `python3` is not recognized, install Python using the instructions for your operating system. Removable disk features currently work on Linux and need `lsblk` and `udisksctl`, usually included with common Linux installations.

## Using TermLink

TermLink opens a menu of the terminals found in the `data` folder. Use the **Up** and **Down** arrow keys to choose an item, then press **Enter**.

- **Explorer terminal:** Use **Up** and **Down** to choose a folder or item, **Enter** to open it, and **Esc** to go back. Press **Left** to return from an item's list to the folder list. Press **Space** to play or pause audio.
- **Chat terminal:** Type a message and press **Enter** to send it. Press **Esc** to leave.
- **Load from Disk:** On Linux, this can open a complete terminal saved on a removable USB drive. Press **Esc** to return to the menu.
- **Leave:** Closes TermLink.

You can try the included examples: `data/example.json` is an Explorer terminal and `data/example_chat.json` is a Chat terminal. The Chat example needs a compatible AI service and your own settings before it can connect.

## Build a terminal JSON file

Terminal definitions are JSON text files. Save a complete terminal file in `data/` with a `.json` ending, for example `my_terminal.json`. TermLink reads the files in this folder when it starts. If JSON is new to you, copy `data/example.json` and edit the copy. Keep the quotation marks, commas, and brackets in place; a typo can stop the file from loading. You can check your file with any JSON validator before opening TermLink.

Every complete terminal starts with a `terminal` object. Its `type` decides which kind of terminal TermLink opens:

- `explorer` displays folders and entries that you define.
- `chat` sends messages to a compatible AI service.

### Explorer terminal: complete example

```json
{
  "terminal": {
    "title": "My Terminal",
    "type": "explorer",
    "categories": [
      {
        "title": "Notes",
        "entries": [
          {
            "title": "Welcome",
            "type": "text",
            "lines": ["Hello!", "This is my first terminal."]
          }
        ]
      }
    ]
  }
}
```

### Terminal settings

These settings go inside the top-level `terminal` object.

| Setting | Required? | What it does |
| --- | --- | --- |
| `title` | Recommended | Name shown for the terminal in the menu and on its screen. |
| `type` | Yes | Use `explorer` or `chat`. |
| `categories` | Explorer | The folders shown in an Explorer terminal. Each folder has a `title` and an `entries` list. |
| `unlock_code` | No | Passcode required to enter the terminal. Write it as text in quotation marks, such as `"1234"`. |
| `skip_signin` | No | Set to `true` to skip the sign-in screen; otherwise it defaults to `false`. A terminal passcode is still required if `unlock_code` is set. |
| `model` | Chat | Name of the model accepted by your AI service. |
| `apikey` | Chat | API key for that service. Keep it private. |
| `url` | Chat | Full API address that TermLink should contact. |
| `instruction_file` | Chat | Name of a text file in `data/` containing instructions for the AI. |

### Explorer folders and entries

An Explorer terminal's `categories` is a list of folders. Each folder has a `title` and an `entries` list. Each entry has a `title` and a `type`. The entry type determines which other settings it uses.

| Entry type | Settings | What it does |
| --- | --- | --- |
| `text` | `lines` | Shows the text. `lines` is a list of strings; each item appears as a line. Use `\n` inside a string to add a line break. |
| `switch` | `default_state`, `state_labels`, `action_verbs` | Shows a two-state control. `default_state` is `true` or `false`. Give `state_labels` two labels and `action_verbs` two action words or phrases. |
| `button` | `default_state`, `state_labels`, `action_verbs`, `message` | Shows a button. `message` is displayed when it is activated. Supply one item in `state_labels` and one in `action_verbs`. |
| `audio` | `audio` | Plays an audio file from `data/` when **Space** is pressed. |
| `leave` | None | Returns to the main menu. |
| `sign_out` | None | Restarts the terminal at its sign-in screen. |
| `quit` | None | Older name for `leave`; use `leave` for new files. |

Any entry can also have an `unlock_code` to require a passcode before it opens. If `state_labels`, `action_verbs`, or a button's `message` is omitted, TermLink uses its default interface text. For a switch or button, make sure the label and action lists have the number of items described above.

### Chat terminal settings

Here is a template for a Chat terminal. The example values are placeholders; replace them with the settings from your AI service.

```json
{
  "terminal": {
    "title": "My Chat",
    "type": "chat",
    "model": "your-model-name",
    "apikey": "your-api-key",
    "url": "http://localhost:1234/api/v1/chat",
    "instruction_file": "prompt.txt",
    "skip_signin": false
  }
}
```

The instruction file named by `instruction_file` must exist in `data/`. The service must accept the request format used by TermLink. The included `data/example_chat.json` and `data/prompt.txt` are examples, not a ready-to-connect service. Keep real API keys private and out of files you share or publish.

### Audio files

Audio files go in `data/`. For example, if an entry uses `"audio": "audio/song.mp3"`, put the file at `data/audio/song.mp3`.

## Load a terminal from a removable drive

This feature currently works on Linux. Put a complete Explorer or Chat terminal JSON file in the top level of a recognized removable USB drive, then choose **Load from Disk** and insert the drive. If there is more than one terminal file, choose one with the arrow keys and press **Enter**. Press **Esc** to return to the menu.

The drive file must contain a complete `terminal` object. For a Chat terminal, its instruction file must also be in the computer's local `data/` folder. Audio used by an Explorer terminal is also read from the local `data/` folder.

You can also add categories temporarily to an open Explorer terminal. Put a JSON file with a top-level `categories` list on the drive and insert it while the Explorer is open. Those categories disappear when the drive is removed. See `example_floppy.json` for an example.

## Change interface text

The labels and prompts are stored in `locales/tokens.json`. You can edit the displayed text, but keep the existing key names and value types. `locales/de_tokens.json` is also included; TermLink currently reads `locales/tokens.json` when it starts.

## Credits

TermLink was created with AI assistance. For retro visual effects in OBS, see [OBS Retro Effects](https://github.com/FiniteSingularity/obs-retro-effects).
