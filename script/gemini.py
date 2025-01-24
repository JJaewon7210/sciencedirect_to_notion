import os
import time
import google.generativeai as genai
from scrap import load_config
from prompt import construct_prompt, construct_response_schema
from collections import deque

MAX_LEN = 10

def save_json(file_path, content):
    with open(file_path, "w", encoding='utf-8') as file:
        file.write(content)

def read_txt_files(folder_path):
    """
    Reads all .txt files in the specified folder.
    
    :param folder_path: Path to the folder containing .txt files.
    :return: A list of tuples containing full file paths and their contents.
    """
    txt_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                txt_files.append((file_path, content))
    return txt_files

def rate_limited_generate_summary(model, prompt, call_queue):
    """
    Generates a summary using the generative AI model with rate limiting.
    
    :param model: The generative AI model instance.
    :param prompt: The prompt string to guide the summary generation.
    :param call_queue: A deque to track the timestamps of API calls.
    :return: The generated summary text.
    """
    while True:
        if len(call_queue) < MAX_LEN:
            break
        else:
            oldest_call_time = call_queue[0]
            time_since_oldest = time.time() - oldest_call_time
            if time_since_oldest >= 60:
                call_queue.popleft()
                break
            else:
                wait_time = 60 - time_since_oldest
                print(f"Waiting for {wait_time:.2f} seconds to respect RPM limit.")
                time.sleep(wait_time)
    start_time = time.time()
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=construct_response_schema(),
        ),
    )
    call_queue.append(start_time)
    return response.text

def main():
    # Load configuration
    config = load_config("config.yaml")
    genai.configure(api_key=config['gemini_apikey'])
    model = genai.GenerativeModel(config['gemini_model'])
    
    # Specify the output folders
    scrap_output_folder = config.get("scrap_output_folder", None)
    if scrap_output_folder is None:
        raise ValueError("Output folder not specified in the configuration.")
    
    gemini_output_folder = config.get("gemini_output_folder", None)
    if gemini_output_folder is None:
        raise ValueError("Gemini output folder not specified in the configuration.")
    
    # Ensure gemini_output_folder exists
    if not os.path.exists(gemini_output_folder):
        os.makedirs(gemini_output_folder)
    
    # Read all .txt files in the output folder
    txt_files = read_txt_files(scrap_output_folder)
    
    if not txt_files:
        print("No .txt files found in the specified folder.")
    else:
        # Initialize the call queue for rate limiting
        call_queue = deque(maxlen=MAX_LEN)
        
        # Process each file
        for idx, (file_path, content) in enumerate(txt_files):
            prompt = construct_prompt(content)

            summary = rate_limited_generate_summary(model, prompt, call_queue)
            
            # Get the relative path of the file with respect to scrap_output_folder
            relative_path = os.path.relpath(file_path, start=scrap_output_folder)
            
            # Create the full output path within gemini_output_folder
            output_dir = os.path.join(gemini_output_folder, os.path.dirname(relative_path))
            
            # Create subdirectories if they don't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Create output file path
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_file_path = os.path.join(output_dir, f"{base_name}_summary.json")
            
            # Save
            save_json(output_file_path, summary)
            
            print(f"Finished processing file {idx+1}/{len(txt_files)}: {file_path}")
            
            # Introduce a delay between calls
            time.sleep(0.5)  # Adjust the sleep duration as needed

if __name__ == "__main__":
    main()
