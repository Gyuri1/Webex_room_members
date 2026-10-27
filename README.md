# Webex Room Members Email Exporter

A lightweight Python command-line tool that retrieves the email addresses of all members in a Webex room (space) using the official [Webex REST API](https://developer.webex.com/messaging/docs/getting-started).

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Authentication](#authentication)
- [Usage](#usage)
- [Command-Line Options](#command-line-options)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- List all Webex rooms available to the token owner, along with their room IDs
- Retrieve member email addresses by **room ID** or **room title**
- Automatic **pagination** (works with large rooms)
- Built-in handling of **rate limiting** (HTTP 429 with `Retry-After`)
- Removes duplicates and sorts the output alphabetically
- Optional export to a text file (one email per line)
- Token is read from an environment variable, never hard-coded

---

## Requirements

- **Python 3.10** or newer
- The [`requests`](https://pypi.org/project/requests/) library
- A valid **Webex access token** (personal, bot, or integration token)
- The token owner must be a **member of the target room**

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 2. Create and activate a virtual environment (recommended)

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` file, install the dependency directly:

```bash
pip install requests
```

### 4. Verify the installation

```bash
python webex_room_members.py --help
```

---

## Authentication

The script authenticates with a **Bearer token** read from the `WEBEX_TOKEN` environment variable.

### Obtaining a token

| Token type | Where to get it | Lifetime |
|---|---|---|
| Personal access token | [developer.webex.com](https://developer.webex.com/messaging/docs/getting-started) (log in, then copy your token) | 12 hours |
| Bot token | [Create a bot](https://developer.webex.com/my-apps/new/bot) | Long-lived |
| Integration (OAuth) token | [Create an integration](https://developer.webex.com/my-apps/new/integration) | Refreshable |

> **Note:** A bot can only see rooms it has been added to.

### Setting the environment variable

**Linux / macOS**

```bash
export WEBEX_TOKEN="your_token_here"
```

**Windows (PowerShell)**

```powershell
$env:WEBEX_TOKEN="your_token_here"
```

**Windows (Command Prompt)**

```cmd
set WEBEX_TOKEN=your_token_here
```

> The variable is valid only in the current terminal session. Set it again after opening a new terminal.

---

## Usage

```bash
python webex_room_members.py (--room-id ROOM_ID | --room-title TITLE | --list-rooms) [--output FILE]
```

A typical workflow:

1. Run `--list-rooms` to find the room you need.
2. Copy its room ID, or use its exact title.
3. Retrieve the members' email addresses, either on screen or saved to a file.

---

## Command-Line Options

| Option | Description |
|---|---|
| `--room-id ROOM_ID` | Webex room ID to read members from |
| `--room-title TITLE` | Exact room title (case-insensitive). If several rooms match, the first one is used and all matches are listed. |
| `--list-rooms` | Lists all rooms visible to the token owner (`ID <TAB> Title`) |
| `--output FILE` | Optional. Writes the emails to `FILE`, one per line. |
| `-h`, `--help` | Shows the help message |

> `--room-id`, `--room-title`, and `--list-rooms` are mutually exclusive. Exactly one of them is required.

---

## Examples

### List your rooms

```bash
python webex_room_members.py --list-rooms
```

```text
Y2lzY29zcGFyazovL3VzL1JPT00vYWJjZGVm...    Project Team
Y2lzY29zcGFyazovL3VzL1JPT00vMTIzNDU2...    Customer Escalations
```

### Get member emails by room ID

```bash
python webex_room_members.py --room-id Y2lzY29zcGFyazovL3VzL1JPT00vYWJjZGVm...
```

```text
alice@example.com
bob@example.com
carol@example.com

Total: 3 member(s)
```

### Get member emails by room title

```bash
python webex_room_members.py --room-title "Project Team"
```

### Export emails to a file

```bash
python webex_room_members.py --room-title "Project Team" --output members.txt
```

```text
3 email(s) written to members.txt
```

### Pipe the output to other tools

The summary line is written to `stderr`, so `stdout` contains only email addresses:

```bash
python webex_room_members.py --room-id <ROOM_ID> | grep "@example.com"
```

---

## Troubleshooting

| Symptom / Error | Likely cause | Solution |
|---|---|---|
| `Please set the WEBEX_TOKEN environment variable.` | The token is not set in the current shell | Set `WEBEX_TOKEN` as shown in [Authentication](#authentication), in the same terminal where you run the script. |
| `API error 401` | The token is invalid, expired, or copied incompletely | Generate a new token. Personal tokens expire after 12 hours. Check for extra spaces or quotes. |
| `API error 403` | The token lacks the required scope or access | Make sure the token has the `spark:memberships_read` and `spark:rooms_read` scopes (for integrations). |
| `API error 404` | Wrong room ID, or the token owner is not a member of the room | Run `--list-rooms` to confirm the room ID. Add the user or bot to the room. |
| `No room found with title: ...` | The title doesn't exactly match, or the room isn't visible to the token | Run `--list-rooms` and copy the exact title. For 1:1 rooms, the title is the other person's name. |
| `Multiple rooms match this title...` | Several rooms have the same title | Use `--room-id` with the specific ID shown in the output. |
| `Rate limited, retrying in Xs...` | Too many API requests (HTTP 429) | No action needed. The script retries automatically. |
| `ModuleNotFoundError: No module named 'requests'` | The dependency is not installed, or the virtual environment is not active | Activate the virtual environment, then run `pip install requests`. |
| `TypeError: unsupported operand type(s) for \|` | The Python version is older than 3.10 | Upgrade to Python 3.10+. Check with `python --version`. |
| `SSLError` / `ProxyError` / connection timeout | A corporate proxy or firewall is blocking `webexapis.com` | Set `HTTPS_PROXY` (e.g. `export HTTPS_PROXY=http://proxy:8080`), or allow outbound HTTPS to `webexapis.com`. |
| PowerShell: `running scripts is disabled on this system` | The execution policy blocks venv activation | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. |
| Fewer emails than expected | Some members may be hidden from bots, or the room is moderated | Try a personal token of a room member, or check the room's settings. |

### Quick token test

To verify that your token works, independently of the script:

```bash
curl -s -H "Authorization: Bearer $WEBEX_TOKEN" https://webexapis.com/v1/people/me
```

A valid token returns your profile as JSON. An invalid one returns a `401` error.

---

## Security Considerations

- **Never commit your token** to the repository. Keep it in environment variables or a secrets manager.
- Add a `.gitignore` that excludes local files such as `.env`, `.venv/`, and exported email lists (`*.txt`).
- Exported email addresses are **personal data**. Handle them according to your organization's privacy policies and applicable regulations, such as GDPR.
- Revoke or regenerate tokens that may have been exposed.

---

## API Reference

- [Getting Started with Webex APIs](https://developer.webex.com/messaging/docs/getting-started)
- [List Rooms](https://developer.webex.com/docs/api/v1/rooms/list-rooms)
- [List Memberships](https://developer.webex.com/docs/api/v1/memberships/list-memberships)
- [Pagination](https://developer.webex.com/docs/basics#pagination)
- [Rate Limiting](https://developer.webex.com/docs/basics#rate-limiting)

---

## Contributing

Contributions are welcome:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

> **Disclaimer:** This is an independent tool and is not an official Cisco or Webex product.
