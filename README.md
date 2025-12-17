# SciOlyBugWeb - Bug Identification Flashcards 🐞

A static web application designed to help students practice entomology identification for Science Olympiad. This project is a web-based adaptation of the [Bugbo Discord Bot](https://github.com/tctree333/Bugbo).

## Features

-   **Interactive Flashcards**: dynamic bug identification game using real data.
-   **Multiple Game Modes**:
    -   **Easy**: Identification with the Order provided as a hint.
    -   **Hard**: Pure family identification.
    -   **Training**: Practice identifying insect Orders.
-   **Filtering**: Focus your study by filtering bugs by their Order (e.g., Coleoptera, Lepidoptera).
-   **Hints & Sources**: Built-in hint system and direct links to iNaturalist observations to learn more.
-   **Comprehensive Data**: Includes over 100 bug families sourced directly from the original Bugbo repository and iNaturalist.

## How to Play

1.  Visit the [live website](https://Slooquie.github.io/SciOlyBugWeb/web/).
2.  Choose your **Game Mode** and **Filter** from the controls.
3.  Type your guess (Common Name or Scientific Family Name) and hit Enter or Submit.
4.  Use the **Hint** button if you're stuck, or **Reveal Answer** to learn.

## Running Locally

To run this project on your own machine:

1.  Clone the repository.
2.  Open a terminal in the project folder.
3.  Run the Python web server:
    ```bash
    python -m http.server --directory web 8000
    ```
4.  Open `http://localhost:8000` in your browser.

## Data Generation

The bug data is generated using the `convert_repo_data.py` script, which parses the original text files from the Bugbo repository and fetches representative images and taxonomy details from the iNaturalist API.
