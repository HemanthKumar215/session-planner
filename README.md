📚 Session Planner
A personalized study schedule generator powered by Grok AI, designed to help students optimize their preparation based on Previous Year Questions (PYQs) analysis and textbook content. This application provides a web-based interface (HTML, CSS, JavaScript) to input study parameters and a Python Flask backend that leverages Grok AI to analyze educational materials and generate a tailored study plan.

✨ Features
Personalized Scheduling: Generate study plans based on subject, desired preparation days, and target score.

AI-Powered Content Analysis: Utilizes Grok AI to analyze PYQ documents and textbook content to identify high-priority topics.

Curriculum Alignment: Integrates with a pre-defined biology curriculum to ensure relevant topic suggestions.

Responsive Frontend: A user-friendly web interface that works across devices.

📁 Project Structure
session-planner/  # Your main project directory (e.g., C:\Users\YourUser\sheduler)
├── frontend/                  # Your HTML, CSS, and JS Frontend
│   ├── index.html             # Main HTML file for the UI
│   ├── style.css              # Custom CSS for styling (uses Tailwind CSS CDN)
│   └── script.js              # JavaScript logic for frontend interactivity
|
├── backend/                   # Your Grok AI powered Backend
│   ├── data/
│   │   ├── pyqs/              # Folder for Previous Year Question papers (.txt, .pdf)
│   │   │   └── <your_pyq_files_here>
│   │   ├── textbooks/         # Folder for textbook content (.txt, .pdf)
│   │   │   └── <your_textbook_files_here>
│   │   └── biology_curriculum.json # Biology curriculum topics/keywords
│   |
│   ├── models/                # (Optional) Directory for trained ML models or artifacts
│   ├── app.py                 # Main Flask backend application; handles API, data analysis, Grok AI integration
│   ├── requirements.txt       # Python dependencies for the backend
│   ├── utils.py               # (Optional) Utility functions for text processing, etc.
│   ├── config.py              # (Optional) Configuration settings for the backend
│   └── .env                   # Environment variables (e.g., Grok API Key - IMPORTANT: excluded from Git)
|
├── README.md                  # This README file
└── .gitignore                 # Specifies files/folders to be ignored by Git

⚙️ Setup and Installation
Follow these steps to get the Session Planner up and running on your local machine.

1. Prerequisites
Python 3.8+: Make sure Python is installed.

pip: Python package installer (comes with Python).

Git: For cloning the repository and version control.

Web Browser: To run the frontend.

Grok AI API Key: Obtain one from Groq Cloud.

2. Clone the Repository (If starting from scratch)
If you haven't already, clone this repository:

git clone https://github.com/your-username/session-planner.git
cd session-planner # Make sure this is the actual name of your cloned project root folder

Replace your-username and session-planner with your actual GitHub details.

3. Backend Setup
Navigate to the backend directory:

cd backend

Install Python dependencies:

pip install -r requirements.txt

Place your data files:

Create data/pyqs and data/textbooks folders inside backend/data/.

Place your .pdf and .txt PYQ files in backend/data/pyqs/.

Place your .pdf and .txt textbook files in backend/data/textbooks/.

Ensure biology_curriculum.json is in backend/data/.

Configure Environment Variables:

Create a file named .env in the backend/ directory (if it doesn't exist).

Add your Grok API key to this file:

GROQ_API_KEY=your_grok_api_key_here

IMPORTANT: Replace your_grok_api_key_here with your actual Grok API key. Keep this file private and never commit it to public repositories.

4. Frontend Setup
The frontend is built with pure HTML, CSS (Tailwind CDN), and JavaScript. No separate installation steps are required beyond having the files in place.

▶️ How to Run
Start the Backend Server:
Open a terminal, navigate to the session-planner/backend/ directory, and run:

python app.py

Keep this terminal window open; the Flask server will be running on http://127.0.0.1:5000.

Open the Frontend:
Open your web browser. Navigate to your session-planner/frontend/ directory in your file explorer and double-click index.html. This will open the application in your browser.

Generate Schedule:

In the web interface, select a subject (currently "Biology" is supported).

Enter the "Number of Days for Preparation".

Enter your "Target Score (%)".

Click the "Generate Schedule" button.

The backend will then process your request, use Grok AI to analyze your documents, and generate a personalized study schedule, which will be displayed on the frontend.

🛠️ Technologies Used
Frontend: HTML, CSS (Tailwind CSS), JavaScript

Backend: Python 3, Flask, Groq AI API

PDF Parsing: PyPDF2

Environment Management: python-dotenv

Version Control: Git, GitHub