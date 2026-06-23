# Quick Start Guide (Explorer)
- download the latest TermLink.zip file
- unpack the zip file
- open the data folder
- open the example.json (i used notepad++ (https://notepad-plus-plus.org/downloads) for editing it)
- edit the file to your needs

### Examples to copy and paste your own explorer terminal
Base Structure
```
{
"terminal": {
		"title": "NAME OF THE TERMINAL",
		"unlock_code": "OPTIONAL PASSWORD",
		"type": "explorer",
		"categories": [
                          # Paste your categories here, comma seperated
                      ]
            }
}
```

Category (Folder) Structure
```
{
	"title": "NAME OF THE FOLDER",
	"entries": [
                   # Paste your entries here, comma seperated
               ]
} # comma here but only if needed
```

TEXT Entry (FILE) Structure
```
{
	"title": "TITLE OF THE ENTRY",
	"type": "text",
	"lines": ["YOUR TEXT"],
	"unlock_code": "OPTIONAL PASSWORD"
} # comma here but only if needed
```

AUDIO Entry (FILE) Structure
```
{
	"title": "NAME OF THE ENTRY",
	"type": "audio",
	"audio": "PATH/TO/YOUR/AUDIO.mp3"
	"unlock_code": "OPTIONAL PASSWORD"
} # comma here but only if needed
```

SWITCH Entry (FILE) Structure
```
{
	"title": "NAME OF THE ENTRY",
	"type": "switch",
	"unlock_code": "OPTIONAL PASSWORD"
	"default_state": false,
	"state_labels": [
			"ADJECTIVE1 LIKE CLOSED",
			"ADJECTIVE2 LIKE OPENED"
					],
	"action_verbs": [
			"VERB1 LIKE CLOSE",
		    "VERB2 LIKE OPEN"
				    ]
} # comma here but only if needed
```

BUTTON Entry (FILE) Structure
```
{
	"title": "NAME OF THE ENTRY",
	"type": "button",
	"unlock_code": "OPTIONAL PASSWORD"
	"default_state": false,
	"state_labels": [
			"ADJECTIVE LIKE ACTIVE"
					],
	"action_verbs": [
			"VERB LIKE ACTIVATE"
				    ]
   	"message": "MESSAGE TO POPUP"
} # comma here but only if needed
```

QUIT Entry (FILE) Structure
```
{
	"title": "NAME OF THE ENTRY",
	"type": "quit",
	"unlock_code": "OPTIONAL PASSWORD"
} # comma here but only if needed
```
---
Simple Example
```
{
	"terminal": {
		"title": "Eriks Private Terminal",
		"unlock_code": "",
		"type": "explorer",
		"categories": [
			{
				"title": "Private",
				"entries": [
					{
						"title": "Secret Code",
						"type": "text",
						"lines": ["I need to remember the code 12345"]
					},
					{
						"title": "I forgot my code again",
						"type": "text",
						"lines": ["What was my code again?\nI should write it down..."]
					}
				]
			},
			{
				"title": "Utility",
				"entries": [
					{
						"title": "Self-destruction",
						"type": "button",
						"default_state": false,
						"state_labels": [
							"Activated"
						],
						"action_verbs": [
							"Activate"
						],
						"message": "Self-destruction\ninitiated"
					}
				]
			},
			{
				"title": "Leave",
				"entries":	[
					{
						"title": "Leave",
						"type": "quit"
					}
				]
			}
		]
	}
}
```