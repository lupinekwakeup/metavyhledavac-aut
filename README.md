# Metavyhledavač aut

## Introduction

Metavyhledavač Aut is a Python-based program designed to streamline the process of searching for the best value-for-money used cars across leading Czech car listing websites. By aggregating data from SBazar, Bazos, and Autoesa, it provides users with a ranked list of vehicles based on a calculated score of price to performance ratio.

## Technologies

This project is implemented using Python and leverages the following libraries:

- Selenium: For automating web browser interaction and scraping car listing data from various sources.
- FuzzyWuzzy: For string matching and determining the similarity between user-input car models and listing titles.

## Setup

To use the metavyhledavač, you must have Python installed on your system along with the required libraries. Here is how you can set up the program:

### Requirements

Ensure you have Python 3.6 or higher installed. You can download it from [Python's official website](https://www.python.org/downloads/).

### Installation

1. Clone the repository to your local machine.
2. Navigate to the project directory and install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### Usage
Run the main.py script from your command line interface (CLI) and follow the on-screen prompts to input the car model and the desired accuracy level for the search results:

```bash
python main.py
```

### How it Works

The program starts by asking the user to enter the desired car model and threshold for search accuracy.
It then searches through SBazar, Bazos, and Autoesa for the most recent listings matching the input criteria.
The data is then normalized, and scores are calculated based on the vehicle's age, mileage, and power output.
Finally, it displays up to 10 cars with the best score, or fewer if less are found, sorted by their score.





 
