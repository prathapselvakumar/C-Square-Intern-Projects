# C-Square Intern Projects

This repository collects five tools I built during my internship at C-Square Info-Solutions. They range from a retrieval-based HR chatbot to small automation scripts for sales reporting and Telegram messaging. Each tool sits in its own folder with its own dependencies and can be run on its own.

> [!IMPORTANT]
> For security and privacy reasons, C-Square allowed me to publish only the code in this repository. Production credentials have been removed from the code, so each tool needs your own configuration before it will run.

## Projects

| No. | Folder | What it does | Main libraries |
| --- | --- | --- | --- |
| T1 | `T1.HR Connect Bot` | Answers employee HR questions from company documents | Flask, LlamaIndex, OpenAI, MongoDB |
| T2 | `T2.Sales Target Evaluator` | Marks each salesperson as a winner or loser against their target | pandas |
| T3 | `T3.Sales Report Image` | Draws a day-on-day sales comparison card and posts it to Telegram | Pillow, python-telegram-bot, MySQL |
| T4 | `T4.URL Shortener` | Shortens URLs and redirects short links to the original address | Flask, MongoDB |
| T5 | `T5.Telegram Holiday Bot` | Lets a Telegram chat record and list holidays | pyTelegramBotAPI, MySQL |

## T1. HR Connect Bot

### Purpose

The HR Connect Bot answers employee questions about HR policies and procedures through a web chat page, using the content of company documents as its source.

### Method

The bot uses retrieval-augmented generation. At start-up, every file in the `docs/` folder is read with LlamaIndex's `SimpleDirectoryReader` and embedded into a `VectorStoreIndex`. When a user sends a question, the query engine retrieves the passages most similar to it and passes them to an OpenAI model, which writes the answer. Each question and answer is saved to MongoDB, in a `session_mst` collection (one document per chat session) and a `session_det` collection (one document per exchange). A user can clear the history, which closes the current session and opens a new one.

Users can sign in in two ways. In production, C-Square's single sign-on (SSO) service redirects users back with an `auth_token`, which the app validates against the SSO server before starting a session. For local use, the app also has signup and login pages that store usernames and bcrypt-hashed passwords in MongoDB. Values kept in the Flask session cookie are encrypted with AES-256 using a key generated for each session.

### Structure

| File | Role |
| --- | --- |
| `app.py` | Entry point; registers all routes and serves static assets |
| `core.py` | Flask app, document index, SSO handling, and session helpers |
| `config.py` | Settings, read from environment variables |
| `models/chat.py` | Chat sessions, history storage, and the chat API |
| `views/chat.py` | Chat page |
| `views/auth.py` | Signup, login, and logout pages |
| `user_database.py` | Local user accounts |
| `utils/crypto.py` | AES and RSA helpers |
| `utils/mongo_connector.py` | Pooled MongoDB client |
| `app.wsgi` | Apache mod_wsgi entry point |

### Running it

```bash
cd "T1.HR Connect Bot"
pip install -r requirements.txt
cp .env.example .env    # then fill in OPENAI_API_KEY, FLASK_SECRET_KEY, and MONGO_HOST
python app.py           # serves on http://localhost:5003
```

Place the HR documents to be indexed in `docs/` before starting the app.

## T2. Sales Target Evaluator

`evaluate_sales_targets.py` reads `data.xlsx`, which lists each salesperson's code, name, date of birth, sales, and target. It labels a row `winner` when sales meet or exceed the target and `loser` otherwise, then writes the labelled table to `winners.xlsx`. The input file is left unchanged.

```bash
cd "T2.Sales Target Evaluator"
pip install -r requirements.txt
python evaluate_sales_targets.py
```

## T3. Sales Report Image

### Purpose

This tool turns two days of sales figures into a single image and posts it to a Telegram chat as a daily comparison.

### Method

`report_image.py` loads `sales_data.json`, which holds one record for the current day and one for the previous day. For six metrics (invoice total, invoice count, average invoice value, customer count, line count, and net sales) it compares the two days numerically and places an up or down arrow on the template image. It then writes both days' figures beside the arrows, with net sales converted to lakhs. The layout coordinates are defined once at the top of the module, so moving a field only means changing one number.

Three entry points use this module:

| Script | What it does |
| --- | --- |
| `preview_report.py` | Opens the card in an image viewer, without sending it |
| `send_report.py` | Saves the card and sends it using `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` |
| `send_report_from_db.py` | Does the same, but reads the token and chat ID from MySQL (schema in `telegram_credentials.sql`) |

```bash
cd "T3.Sales Report Image"
pip install -r requirements.txt
python preview_report.py
```

## T4. URL Shortener

The shortener is a Flask app with a single page. A user pastes a long URL and receives a short link made of the host name and a random six-character code drawn from letters and digits. The app first checks MongoDB for the long URL and returns the existing short link if there is one, so the same address is never stored twice. New codes are also checked against the database before use, so no two short links collide. Visiting a short link returns an HTTP 302 redirect to the original address, and the home page lists every link created, with its creation time.

```bash
cd "T4.URL Shortener"
pip install flask pymongo
python app.py           # serves on http://localhost:5000
```

## T5. Telegram Holiday Bot

The bot keeps a list of holidays for each Telegram chat. Users type `add holiday <date> <name>` (for example, `add holiday 2023-12-25 Christmas`) or `list holidays`, or use the two buttons on the reply keyboard. There are two versions:

- `bot_in_memory.py` stores holidays in a Python dictionary, so they are lost when the bot restarts. It also answers `/sayhello`, `/echo`, and `/time`.
- `bot_mysql.py` stores holidays in a MySQL `holidays` table, which it creates on first run.

```bash
cd "T5.Telegram Holiday Bot"
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=<your token>   # on Windows: set TELEGRAM_BOT_TOKEN=<your token>
python bot_in_memory.py
```

## Configuration

No credentials are stored in the code. Each tool reads them from environment variables:

| Variable | Used by |
| --- | --- |
| `OPENAI_API_KEY`, `FLASK_SECRET_KEY`, `MONGO_HOST`, `MONGO_DB`, `AUTH_MONGO_HOST`, `CSQ_SSO_BASE_URL`, `APP_BASE_URL` | T1 |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | T3 (`send_report.py`), T5 |
| `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` | T3 (`send_report_from_db.py`), T5 (`bot_mysql.py`) |
| `MONGO_HOST` | T4 (defaults to a local MongoDB) |

## Limitations

These tools were built as internship exercises and prototypes, and they have the following known gaps.

- T1 rebuilds the document index every time it starts, which calls the OpenAI embedding API for every document. A production version would save the index to disk and reload it.
- T1 has `ALLOW_DUMMY_SESSION` switched on, which lets anyone reach the chat page as a placeholder user. It should be switched off outside local testing.
- T1 saves chat history, but the reply endpoint uses a stateless query engine, so the model does not see earlier messages in the conversation.
- T1 targets the LlamaIndex API from before version 0.10, which later releases changed. `requirements.txt` pins the older version.
- The T5 MySQL bot does not validate the date that users type, so an invalid date makes the database insert fail.

## Requirements

- Python 3.8 or later
- MongoDB for T1 and T4
- MySQL for the database versions of T3 and T5
- A Telegram bot token from BotFather for T3 and T5
- An OpenAI API key for T1
