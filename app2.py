import json
from record import output_text_buffer, read_text_file, record_text
from together_ai import load_api_key, initialize_together_client, summarize_text, output_summary_to_docx
import time

def main():
    config_path = "config.json"  # Define the path to the config file

    # Load TOGETHER_API_KEY key
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
        llama = config.get("TOGETHER_API_KEY")
        
    # Initialize Together client
    client = initialize_together_client(llama)

    # Voice recording parts
    text_buffer = []
    buffer_limit = 5  # Adjust the buffer limit as needed
    total_duration = 40  # Total recording duration in seconds
    start_time = time.time()

    # Clear the output.txt file before starting recording
    with open("output.txt", "w") as f:
        f.write("")

    while time.time() - start_time < total_duration:
        text = record_text()
        if text:
            text_buffer.append(text)
            print(f"Recorded: {text}")
        
        # Check if buffer limit is reached and write to file
        if len(text_buffer) >= buffer_limit:
            output_text_buffer(text_buffer)
            text_buffer = []  # Clear the buffer

        print("Write something")
    
    # Write any remaining buffered text to file
    if text_buffer:
        output_text_buffer(text_buffer)
    
    # Read text file
    conversation_text = read_text_file("output.txt")

    # Summarize text using the GPT model
    summary = summarize_text(conversation_text, client)

    # Output summary to a .docx file
    output_summary_to_docx(summary)

    print(f"Summary: {summary}")

if __name__ == "__main__":
    main()
