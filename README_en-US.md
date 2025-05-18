**README\_en-US.md (English Version - Translation of the above)**

````markdown
[English Version](README_en-US.md) | [Versão em Português (Brasil)](README_pt-BR.md)
---

# 🎬 Kids' Movie Picker (Proof of Concept)

## Short Description
This project is a **Proof of Concept (POC)** of a Python command-line application. Its goal is to help parents and guardians find suitable movie and TV show recommendations for children, considering age, interests, streaming platforms available in Brazil (current focus), and content ratings. It utilizes The Movie Database (TMDb) API for fetching title information and the Google Gemini API (via Google AI Studio) for expanding search ideas and generating user-friendly justifications for suggestions.

**Project Status:** Proof of Concept (POC) - Under Development / Refinement.

## ✨ Key Features
* **Preference Collection:** Asks for the child's age, current interests, and the family's subscribed streaming platforms. (Currently focused on Brazil).
* **Intelligent TMDb Search:**
    * Uses Google Gemini to expand user-provided interest terms, aiming for a broader range of relevant keywords.
    * Performs searches on TMDb using multiple strategies (keywords, direct terms, popular genres by age) to increase the chances of finding content.
* **Data Enrichment:** For each title found, it fetches detailed information such as genres, synopsis, TMDb user rating, and the official age rating in Brazil.
* **Streaming Availability Check:** Verifies on which of the user's preferred streaming platforms (in Brazil) the title is available for subscription.
* **AI-Powered Justifications:** Uses Google Gemini to create a friendly and personalized paragraph explaining why each suggestion might be a good choice for the child.
* **Existence Verification (Optional):** An additional agent uses Gemini with Google Search to try and confirm if the recommended title is widely known and relevant, adding an extra layer of checking.
* **Console Display:** Presents the final recommendations clearly in the terminal.

## 🚀 Technologies Used
* **Language:** Python 3
* **Main Python Libraries:**
    * `google-generativeai` (for the Google Gemini API)
    * `requests` (for interacting with the TMDb API)
    * `python-dotenv` (for managing API keys securely)
* **External APIs:**
    * The Movie Database (TMDb) API (v3)
    * Google Gemini API (via Google AI Studio)

## ⚙️ Environment Setup and Installation (For Beginners)

To run this project on your computer, you'll need to follow a few steps. Don't worry, we'll detail each one!

**Prerequisites:**
* Python 3 installed on your computer. If you don't have it, you can download it from [python.org](https://www.python.org/downloads/). During installation on Windows, make sure to check the "Add Python to PATH" option.
* A simple text editor (like Notepad, VS Code, Sublime Text, etc.) to create and edit files.
* Internet access to download libraries and for the program to query the APIs.

**Setup Steps:**

1.  **Create a Project Folder:**
    * On your computer, create a new folder. Let's call it, for example, `movie_picker_poc`.
    * Copy all the files from this project (`main.py`, `requirements.txt`, `.gitignore`, `README.md`, `README_pt-BR.md`) into this folder.

2.  **Open the Terminal (Command Prompt):**
    * **Windows:** Search for "cmd" or "PowerShell".
    * **macOS:** Search for "Terminal".
    * **Linux:** Usually Ctrl+Alt+T or search for "Terminal".
    * Navigate to the project folder you created. For example, if on Windows and your folder is at `C:\Projects\movie_picker_poc`, type:
        ```bash
        cd C:\Projects\movie_picker_poc
        ```

3.  **Create a Python Virtual Environment (Good Practice):**
    A virtual environment isolates this project's libraries from others installed on your system. In the terminal, inside your project folder, type:
    ```bash
    python -m venv .venv
    ```
    This will create a subfolder named `.venv` inside your project.

4.  **Activate the Virtual Environment:**
    * **Windows (cmd):**
        ```bash
        .venv\Scripts\activate.bat
        ```
    * **Windows (PowerShell):**
        ```bash
        .venv\Scripts\Activate.ps1
        ```
        (If you encounter an error about script execution in PowerShell, you might need to run `Set-ExecutionPolicy Unrestricted -Scope Process` and try again).
    * **macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```
    Your command prompt should change, typically showing something like `(.venv)` at the beginning, indicating the environment is active.

5.  **Install Necessary Libraries (Dependencies):**
    With the virtual environment active, install the libraries listed in the `requirements.txt` file. In the terminal, type:
    ```bash
    pip install -r requirements.txt
    ```
    Wait for the installation to complete.

6.  **Set Up Your API Keys (Crucial Step!):**
    This project requires API keys to function. They are like passwords that grant the program permission to use the TMDb and Google Gemini services.

    * **Create the `.env` file:**
        * Inside your main project folder (`movie_picker_poc`), create a new plain text file and save it with the exact name: `.env` (it starts with a period and has no extension like `.txt` at the end).
        * If your file explorer doesn't show file extensions, ensure it wasn't saved as `.env.txt`.

    * **Add your keys to the `.env` file:**
        Open the `.env` file with a text editor and copy the following content into it:
        ```env
        GEMINI_API_KEY="PASTE_YOUR_GOOGLE_AI_STUDIO_API_KEY_HERE"
        TMDB_API_KEY="PASTE_YOUR_TMDB_API_KEY_V3_HERE"
        GEMINI_MODEL_ID="gemini-1.5-flash-latest" # Optional: Gemini Model ID to use (e.g., 'gemini-1.5-flash-latest' or 'gemini-pro')
        ```
    * **How to get the Google AI Studio (Gemini) API Key:**
        1.  Go to [Google AI Studio (formerly MakerSuite)](https://makersuite.google.com/).
        2.  Sign in with your Google account.
        3.  In the left-hand menu, click on "**Get API key**".
        4.  Click on "**Create API key in new project**" or use an existing one if you already have one.
        5.  Copy the generated key and paste it in place of `"PASTE_YOUR_GOOGLE_AI_STUDIO_API_KEY_HERE"` in your `.env` file.
            *Note: The Gemini API has a generous free tier, but be mindful of usage limits.*

    * **How to get the TMDb API Key (v3 auth):**
        1.  Go to [The Movie Database (TMDb)](https://www.themoviedb.org/) website.
        2.  Create a free account or log in if you already have one.
        3.  Click on your profile icon (avatar) in the top right corner, then click on "**Settings**".
        4.  In the menu on the left of the settings page, click on "**API**".
        5.  Read the terms of use and, if you agree, request an API key (usually for use as a "Developer"). You will need to fill out a short form about your intended use.
        6.  After approval (it might be immediate or take some time), you will see your "**API Key (v3 auth)**". Copy this key.
        7.  Paste this key in place of `"PASTE_YOUR_TMDB_API_KEY_V3_HERE"` in your `.env` file.

    **Important:** The `.env` file should never be shared publicly (e.g., committed to GitHub), as it contains your secret keys. The `.gitignore` file is already configured to ignore it.

## ▶️ How to Run the Application

1.  **Ensure the virtual environment is active:** You should see `(.venv)` at the beginning of your command prompt. If not, activate it as per Step 4 of the Setup.
2.  **Navigate to the project folder:** If you are not already there, use the `cd` command in your terminal to enter the `movie_picker_poc` folder.
3.  **Run the main script:**
    ```bash
    python main.py
    ```
4.  The application will start running in the console. It will ask you a series of questions (child's age, interests, streaming platforms). Answer each one and press Enter.
5.  After a few moments (while it fetches and processes information), it should present the movie/TV show recommendations.

## 📂 Project File Structure

```

movie\_picker\_poc/
├── .venv/                   \# Python virtual environment folder (usually ignored by Git)
├── .env                     \# File to store your secret API keys (IGNORED BY GIT\!)
├── .gitignore               \# Specifies files and folders Git should ignore
├── main.py                  \# The main Python script for the application
├── requirements.txt         \# Lists Python package dependencies
├── README.md                \# This information file in English
└── README\_pt-BR.md          \# The README file in Brazilian Portuguese

```

## 📝 Important Notes for this POC

* **API Keys are Fundamental:** The application heavily relies on valid API keys for both TMDb and Google Gemini. Without them, or if they are incorrect, the program will not function as expected or will show errors.
* **TMDb API Rate Limits:** The Movie Database API has rate limits for how many requests you can make in a certain period (typically 40-50 requests every 10 seconds per IP). If you run the script too many times quickly, you might encounter temporary errors. Please wait a few minutes before trying again.
* **Simplified Age Certification Logic:** The way the program determines if a movie is age-appropriate for the child (based on ratings like "L", "10" for Brazil; "G", "PG" for the USA) is a **basic simplification for this Proof of Concept**. A real production system would need a much more comprehensive and accurate mapping for various international rating systems.
* **Simplified Streaming Platform Mapping:** The conversion of user-typed streaming platform names (like "Netflix") to the internal IDs used by TMDb is also simplified, using a small internal list of common platforms. A more robust solution would fetch the full list of providers from TMDb for your region.
* **TMDb Results Language:** The TMDb queries in this POC are set to `language=pt-BR` to fetch titles and descriptions in Brazilian Portuguese when available. The availability of such localized data can vary on TMDb.
* **Basic Error Handling:** The program includes basic error handling for API calls and some user inputs. A finished application would need more robust error management and clearer user feedback.
* **Console-Based Interface:** This Proof of Concept is operated entirely via the command line (terminal/console). It does not include a graphical user interface (GUI).

## 📜 License

This project is distributed under the MIT License. See the `LICENSE` file for more details.

---
Contributions and suggestions are welcome (if the project were public/open-source)!