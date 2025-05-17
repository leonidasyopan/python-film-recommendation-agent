[English](README_en-US.md) | [Português (Brasil)](README.md)
---

# Movie Picker POC with TMDb and Google Gemini

This Proof of Concept (POC) is a Python command-line application that recommends movies or TV shows for children based on their age, interests, preferred streaming platforms, and country. It uses The Movie Database (TMDb) API for movie data and streaming availability, and Google Gemini API for generating helpful justifications.

## Features

* Collects user preferences (child's age, interests, streaming services, country).
* Searches for movies/shows on TMDb.
* Retrieves detailed information, including country-specific age ratings.
* Checks availability on specified streaming platforms in the user's country.
* Uses Gemini to generate a friendly explanation for recommendations.
* Displays results in the console.

## Setup

1.  **Clone the repository (or create the files as described):**
    ```bash
    # If you have it on GitHub:
    # git clone [https://github.com/yourusername/python-film-recommendation-agent.git](https://github.com/yourusername/python-film-recommendation-agent.git)
    # cd python-film-recommendation-agent
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up API Keys:**
    * Create a file named `.env` in the `python-film-recommendation-agent` root directory.
    * Add your API keys to the `.env` file in the following format:
        ```env
        GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
        TMDB_API_KEY="YOUR_TMDB_API_KEY"
        ```
    * Replace `YOUR_GEMINI_API_KEY` with your actual Google Gemini API Key.
    * Replace `YOUR_TMDB_API_KEY` with your actual TMDb API Key (v3 auth).

## How to Run

Execute the main script from the project's root directory:

```bash
python main.py
```

The application will then prompt you for input in the console.

Project Structure
movie_picker_poc/
├── .env                     # Stores API keys (ignored by Git)
├── .gitignore               # Specifies intentionally untracked files
├── main.py                  # Main application script
├── requirements.txt         # Python dependencies
└── README.md                # This file
Notes
This is a Proof of Concept. Error handling is basic.
TMDb API has rate limits. If you make too many requests quickly, you might encounter errors.
Age certification mapping is simplified for this POC.
Streaming provider name matching is based on common names.
<!-- end list -->


---

**6. `main.py`**

This is where all the Python code will go. It will be long, so I'll break it down into logical sections (imports, configuration, agent functions, main execution block).

```python