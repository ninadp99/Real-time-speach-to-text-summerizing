from flask import Flask, render_template, request, jsonify, send_file
import json
from record import output_text_buffer, read_text_file, record_text
from together_ai import load_api_key, initialize_together_client, summarize_text, output_summary_to_docx
import time
import threading
import os
import io

app = Flask(__name__)

# Global variables
text_buffer = []
recording_active = False
client = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording_active, client, text_buffer
    
    # Remove summary.docx if it exists
    if os.path.exists("summary.docx"):
        try:
            os.remove("summary.docx")
            print("Existing summary.docx file removed.")
        except OSError as e:
            print(f"Error removing summary.docx: {e}")
    
    if not recording_active:
        # Clear the output.txt file before starting recording
        with open("output.txt", "w") as f:
            f.write("")
        
        # Load TOGETHER_API_KEY and initialize client
        config_path = "config.json"
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
            llama = config.get("TOGETHER_API_KEY")
        client = initialize_together_client(llama)
        
        recording_active = True
        text_buffer = []
        threading.Thread(target=record_and_summarize).start()
        return jsonify({"status": "Recording started"})
    return jsonify({"status": "Recording already in progress"})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording_active
    recording_active = False
    return jsonify({"status": "Recording stopped"})

@app.route('/check_summary', methods=['GET'])
def check_summary():
    if os.path.exists("summary.docx") and os.path.getsize("summary.docx") > 0:
        return jsonify({"ready": True})
    else:
        return jsonify({"ready": False})

@app.route('/get_summary', methods=['GET'])
def get_summary():
    global summary
    if not os.path.exists("summary.docx"):
        return jsonify({"error": "Summary not ready yet"}), 404
    
    with open("summary.docx", "rb") as file:
        file_content = file.read()
    
    file_stream = io.BytesIO(file_content)
    return send_file(
        file_stream,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        as_attachment=True,
        download_name='summary.docx'
    )

def record_and_summarize():
    global text_buffer, summary, recording_active
    buffer_limit = 5

    while recording_active:
        text = record_text()
        if text:
            text_buffer.append(text)
            print(f"Recorded: {text}")
        
        if len(text_buffer) >= buffer_limit:
            output_text_buffer(text_buffer)
            text_buffer = []

    # Write any remaining buffered text to file
    if text_buffer:
        output_text_buffer(text_buffer)
    
    # Check if the output.txt file is empty
    if os.path.getsize("output.txt") == 0:
        print("No text recorded. Skipping summarization.")
        return

    # Read text file
    conversation_text = read_text_file("output.txt")

    # Summarize text using the GPT model
    summary = summarize_text(conversation_text, client)

    # Output summary to a .docx file
    output_summary_to_docx(summary)

    print(f"Summary: {summary}")

if __name__ == "__main__":
    # print(pkg_resources.get_distribution('flask-mail').version)
    app.run(debug=True)
