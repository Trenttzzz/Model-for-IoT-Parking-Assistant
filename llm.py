import os
import json
import requests
from groq import Groq
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db

# Inisialisasi Aplikasi
app = Flask(__name__)
CORS(app)
load_dotenv()

# Inisialisasi Firebase
try:
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://fp-iot-kelompok2-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })
except Exception as e:
    print(f"Firebase inisialisasi error: {e}")

def get_parking_data():
    """Ambil data parkir dari Firebase"""
    try:
        ref = db.reference('parking')
        parking_data = ref.get()
        return json.dumps(parking_data)
    except Exception as e:
        return json.dumps({"error": str(e)})

def analyze_query(query):
    """Analyze the query to determine its nature and requirements"""
    tool_keywords = [
        'api', 'request', 'fetch', 'http', 'data', 
        'send', 'get', 'post', 'call', 'function', 
        'parkir', 'parking', 'status'
    ]
    
    query_lower = query.lower()
    requires_tools = any(keyword in query_lower for keyword in tool_keywords)
    
    return {
        'requires_tools': requires_tools,
        'query_type': 'tool_based' if requires_tools else 'general'
    }

def select_model(query_analysis):
    """Select the appropriate model based on query analysis"""
    if query_analysis['requires_tools']:
        return {
            'model': 'llama3-groq-70b-8192-tool-use-preview',
            'handler': handle_tool_based_query
        }
    return {
        'model': 'llama-3.3-70b-versatile',
        'handler': handle_general_query
    }

def handle_general_query(client, messages):
    """Handle general conversation queries"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    return response.choices[0].message.content

def handle_tool_based_query(client, messages):
    """Handle queries requiring tool use"""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_firebase_parking_data",
                "description": "Ambil data status parkiran dari Firebase, value 1 merupakan parkir sudah di pakai, value 0 merupakan parkir kosong",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]

    response = client.chat.completions.create(
        model="llama3-groq-70b-8192-tool-use-preview",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        messages.append(response_message)
        
        for tool_call in tool_calls:
            function_response = get_parking_data()
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_call.function.name,
                "content": function_response
            })

        second_response = client.chat.completions.create(
            model="llama3-groq-70b-8192-tool-use-preview",
            messages=messages,
            temperature=0.7
        )
        return second_response.choices[0].message.content
    
    return response_message.content

def run_conversation(user_input):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Analyze the query
    query_analysis = analyze_query(user_input)
    
    # Select appropriate model and handler
    model_config = select_model(query_analysis)
    
    messages = [
        {
            "role": "system",
            "content": "Anda adalah asisten yang membantu menjelaskan status parkiran. Gunakan data yang diterima untuk memberikan informasi yang jelas dan mudah dipahami dalam bahasa Indonesia. Fokus pada status parkiran, ruang tersedia, dan kondisi gate."
        },
        {
            "role": "user",
            "content": user_input,
        }
    ]

    # Route to appropriate handler
    return model_config['handler'](client, messages)

@app.route('/query', methods=['POST'])
def process_query():
    try:
        data = request.json
        user_input = data.get('query')
        
        if not user_input:
            return jsonify({'error': 'Tidak ada kueri yang diberikan'}), 400
        
        response = run_conversation(user_input)
        return jsonify({'response': response})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
