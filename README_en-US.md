[English](README_en-US.md) | [Português (Brasil)](README.md)
---

# Proof of Concept (POC): Movie Picker with TMDb and Google Gemini

This Proof of Concept (POC) is a Python command-line application that recommends movies or TV shows for children based on their age, interests, preferred streaming platforms, and country. It uses The Movie Database (TMDb) API for movie data and streaming availability, and the Google Gemini API for generating helpful justifications for the recommendations.

## Features

* Collects user preferences: child's age, current interests, preferred streaming services, and country of residence.
* Searches TMDb for relevant movies and TV shows based on the provided interests.
* Retrieves detailed information for prospective titles, including genres, TMDb user ratings, and attempts to find country-specific age certifications.
* Checks for availability of these titles on the user's specified streaming platforms within their country.
* Uses the Google Gemini API to generate a friendly, contextual paragraph explaining why a selection might be a good choice.
* Displays the final, detailed recommendations directly to the user in the console.

## Setup Instructions

1.  **Project Directory:**
    Ensure all project files (`main.py`, `requirements.txt`, `.env`, this `README.md`, `README_pt-BR.md`, and `.gitignore`) are in the same main project directory (e.g., `movie_picker_poc/`).

2.  **Create a Python Virtual Environment (Highly Recommended):**
    Open your computer's terminal or command prompt. Navigate to your project directory.
    Execute the following command to create a virtual environment (named `venv` here):
    ```bash
    python3 -m venv .venv
    ```
    Activate the created virtual environment:
    * If you are using Windows:
        ```bash
        venv\Scripts\activate
        ```
    * If you are using macOS or Linux:
        ```bash
        source .venv/bin/activate
        ```
    Your command prompt should now typically show `(venv)` at the beginning of the line, indicating the virtual environment is active.

3.  **Install Dependencies:**
    While the virtual environment is active, install the required Python libraries listed in `requirements.txt` by running:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up API Keys (Crucial Step) in `.env` File:**
    * In the root of your project directory (the same place as `main.py`), create a new file named exactly `.env`.
    * Open this `.env` file with a plain text editor.
    * Add your secret API keys to this file in the following format:
        ```env
        GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"
        TMDB_API_KEY="YOUR_ACTUAL_TMDB_API_KEY_V3"
        ```
    * **Important:** Replace `"YOUR_ACTUAL_GEMINI_API_KEY"` with your real API key obtained from Google AI Studio (makersuite.google.com).
    * **Important:** Replace `"YOUR_ACTUAL_TMDB_API_KEY_V3"` with your real TMDb API Key (specifically, the "API Key (v3 auth)" version). You can get this by signing up or logging in at themoviedb.org, then navigating to your account Settings -> API section.

## How to Run the Application

1.  Ensure your Python virtual environment (e.g., `venv`) is activated (you should see `(venv)` in your prompt).
2.  In your terminal or command prompt, make sure you are in the project's root directory (where `main.py` is located).
3.  Execute the main script using the Python interpreter:
    ```bash
    python main.py
    ```
4.  The application will then start running in the console and will ask you a series of questions to gather preferences. Please answer them as prompted.

## Project File Structure

The project should have the following files and folders:

* `movie_picker_poc/` (Your main project folder)
    * `.env` (This file stores your secret API keys. It should be listed in `.gitignore`.)
    * `.gitignore` (This file tells Git version control which files/folders to ignore.)
    * `main.py` (This is the main Python script containing all the application's logic and agent functions.)
    * `requirements.txt` (This file lists the Python package dependencies required for the project.)
    * `README.md` (This file, providing instructions and information about the project in English.)
    * `README_pt-BR.md` (The README file in Brazilian Portuguese.)
    * `venv/` (This folder contains your Python virtual environment, if you created one. It's usually ignored by Git.)

## Important Notes for this POC

* **API Keys are Essential:** The application relies heavily on valid API keys for both TMDb and Google Gemini. It will not function correctly, or at all for certain features, if these keys are missing or invalid.
* **TMDb API Rate Limiting:** The Movie Database API enforces rate limits (typically around 40-50 requests per 10 seconds from a single IP address). If you run the script too many times in rapid succession, you might encounter temporary errors from TMDb. If this happens, please wait a few minutes before trying again.
* **Age Certification Logic (Simplified):** The logic implemented in `main.py` to determine if a movie's age certification (e.g., "L", "10" for Brazil; "G", "PG" for the USA) is appropriate for the child's given age is a **basic simplification for this Proof of Concept**. A production-level application would need a much more comprehensive and accurate system for mapping various international age rating systems.
* **Streaming Platform Mapping (Simplified):** The mapping of user-entered streaming platform names (like "Netflix" or "Disney Plus") to the internal numerical IDs used by TMDb is also simplified in this POC. It uses a small, hardcoded list of common providers. A more robust application would involve fetching the complete list of available providers from TMDb for the user's specific region and implement a more flexible matching or selection mechanism.
* **Language Settings:** The TMDb queries in this POC are currently configured to use `language=en-US` for fetching content details. This can be modified within the `main.py` script if you wish to prioritize results or descriptions in other languages (e.g., `pt-BR` for Brazilian Portuguese). However, the availability of fully localized data can vary on TMDb.
* **Error Handling:** Basic error handling for API requests and some user inputs is included. A production application would require significantly more comprehensive error management and user feedback mechanisms.
* **Console-Based Interface:** This Proof of Concept is entirely operated through the command line (console). It does not include a graphical user interface (GUI).

---