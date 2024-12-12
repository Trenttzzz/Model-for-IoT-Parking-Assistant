# IoT Parking Assistant with LLM

This application implements a smart parking assistant using Large Language Models (LLM) through the Groq API. The system is capable of processing natural language queries about parking status and providing informative responses in Bahasa Indonesia.

## Model Information

The system uses two different LLM models depending on the query type:

1. **llama-3.3-70b-versatile**
   - Used for general conversation queries
   - Handles basic questions without requiring external data

2. **llama3-groq-70b-8192-tool-use-preview**
   - Used for tool-based queries
   - Capable of making API calls and processing parking data
   - Integrates with Firebase Realtime Database to fetch parking status

## Setup Instructions

### 1. Python Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install flask flask-cors groq python-dotenv firebase-admin

# or just type
pip install -r requirements.txt
```

### 2. Firebase Setup
1. Go to Firebase Console (https://console.firebase.google.com/)
2. Go to your project
3. Go to Project Settings > Service Accounts
4. Generate new private key
5. Download the JSON file and rename it to `firebase_credentials.json`
6. Place it in the project root directory

### 3. Groq API Setup
1. Create an account at Groq (https://console.groq.com)
2. Generate an API key
3. Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

## Running the Application

1. Ensure all setup steps are completed
2. Make Sure you've activate the virtual environment if not already activated
3. Run the application:
```bash
python llm.py
```
4. The server will start on `http://localhost:5000`

## API Usage

Send POST requests to `/query` endpoint:
```bash
curl -X POST http://localhost:5000/query \
     -H "Content-Type: application/json" \
     -d '{"query": "bagaimana status parkir saat ini?"}'
```

The system will automatically detect whether the query needs to access parking data and use the appropriate model to handle the request.
