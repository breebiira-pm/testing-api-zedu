# Zedu-API-automation
Python-based API testing project using Pytest and Requests, built to demonstrate engineering discipline and automation maturity for Stage 3 of the QA Engineering Track.


# Zedu API Automation

This repository contains automated tests and utilities for the **Zedu API**.  
It is designed to streamline API validation, improve reliability, and support continuous integration workflows.


##  Features
- Automated test cases for core Zedu API endpoints
- Utility functions for authentication and request handling
- Environment configuration via `.env.example`
- Easy setup with `requirements.txt`


##  Project Structure
testing-api-zedu/

├── tests/            # Test cases for API endpoints

├── utils/            # Helper modules (e.g., auth.py)

├── .env.example      # Example environment variables

├── requirements.txt  # Python dependencies

└── README.md         # Project documentation



##  Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/breebiira-pm/testing-api-zedu.git
   cd testing-api-zedu
Create a virtual environment and install dependencies:

bash
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
pip install -r requirements.txt
Configure environment variables:

Copy .env.example to .env

Update values with your API credentials

Run tests:

bash
pytest
 Notes
Ensure you have Python 3.9+ installed.

Update requirements.txt if you add new dependencies.

Contributions and improvements are welcome!

 License
This project is licensed under the MIT License.
