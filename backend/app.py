# scheduler/backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS # Used to handle Cross-Origin Resource Sharing for frontend communication
import json
import os
import PyPDF2
import re
from collections import Counter
from dotenv import load_dotenv # To load environment variables from .env
from groq import Groq # Uncommented: Import Groq client

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Define paths to your data directories relative to this app.py file
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
PYQS_DIR = os.path.join(DATA_DIR, 'pyqs')
TEXTBOOKS_DIR = os.path.join(DATA_DIR, 'textbooks')
CURRICULUM_PATH = os.path.join(DATA_DIR, 'biology_curriculum.json')

# --- Load the Biology Curriculum Topics ---
BIOLOGY_CURRICULUM = {}
FLATTENED_TOPICS = []
try:
    with open(CURRICULUM_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        BIOLOGY_CURRICULUM = data.get('biology', {})
    print(f"Successfully loaded biology curriculum from: {CURRICULUM_PATH}")
    # Flatten all subtopics into a single list for easier keyword matching/Grok AI prompting
    FLATTENED_TOPICS = [subtopic for chapter_topics in BIOLOGY_CURRICULUM.values() for subtopic in chapter_topics]
    print(f"Total {len(FLATTENED_TOPICS)} subtopics loaded for analysis.")
except FileNotFoundError:
    print(f"Error: {CURRICULUM_PATH} not found. Please ensure it's in the 'backend/data/' directory.")
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {CURRICULUM_PATH}. Check file format.")

# --- Initialize Groq Client ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY") # Uncommented: Get API key from environment
if not GROQ_API_KEY:
    print("Error: GROQ_API_KEY not found in environment variables. Please set it in .env file.")
    # You might want to raise an error or exit if the key is essential for your app
    raise ValueError("GROQ_API_KEY is not set. Cannot initialize Groq client.") # Uncommented: Raise error if key missing

groq_client = Groq(api_key=GROQ_API_KEY) # Uncommented: Initialize Groq client


# --- Helper Function to Extract Text from PDF (from utils.py, but keeping here for single file ease) ---
def extract_text_from_pdf(pdf_path):
    """
    Extracts text content from a PDF file.
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() or ''
        return text
    except PyPDF2.errors.PdfReadError:
        print(f"Warning: Could not read PDF file {pdf_path}. It might be corrupted or encrypted.")
        return ""
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

# --- Function to Read All PYQs and Textbook Content ---
def get_all_document_texts():
    """
    Reads all text content from PYQ and textbook files.
    Supports .txt and .pdf files.
    Returns a dictionary mapping file paths to their content.
    """
    all_texts = {}

    print("\nReading PYQ files...")
    for filename in os.listdir(PYQS_DIR):
        file_path = os.path.join(PYQS_DIR, filename)
        if os.path.isfile(file_path): # Ensure it's a file, not a directory
            if filename.endswith('.txt'):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        all_texts[file_path] = f.read()
                    print(f"  - Read: {filename} (TXT)")
                except Exception as e:
                    print(f"  - Error reading {filename} (TXT): {e}")
            elif filename.endswith('.pdf'):
                pdf_text = extract_text_from_pdf(file_path)
                if pdf_text:
                    all_texts[file_path] = pdf_text
                    print(f"  - Read: {filename} (PDF)")
                else:
                    print(f"  - Skipped: {filename} (PDF - no text extracted or error)")
            else:
                print(f"  - Skipped: {filename} (Unsupported format)")

    print("\nReading Textbook files...")
    for filename in os.listdir(TEXTBOOKS_DIR):
        file_path = os.path.join(TEXTBOOKS_DIR, filename)
        if os.path.isfile(file_path): # Ensure it's a file, not a directory
            if filename.endswith('.txt'):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        all_texts[file_path] = f.read()
                    print(f"  - Read: {filename} (TXT)")
                except Exception as e:
                    print(f"  - Error reading {filename} (TXT): {e}")
            elif filename.endswith('.pdf'):
                pdf_text = extract_text_from_pdf(file_path)
                if pdf_text:
                    all_texts[file_path] = pdf_text
                    print(f"  - Read: {filename} (PDF)")
                else:
                    print(f"  - Skipped: {filename} (PDF - no text extracted or error)")
            else:
                print(f"  - Skipped: {filename} (Unsupported format)")

    return all_texts # Return dictionary of {filepath: content}


# --- Global variable to store all combined text, loaded once at startup ---
# This will be a dictionary: {filepath: content_string}
ALL_DOCUMENT_CONTENTS = get_all_document_texts()


# --- Core ML Logic: Analyze PYQs and Generate Schedule ---
def analyze_and_generate_schedule(subject, days, target_score, curriculum_topics_list, document_contents):
    """
    This function will contain your Grok AI powered logic to:
    1. Process document contents (from PYQs and textbooks).
    2. Identify important topics based on frequency/weightage using `curriculum_topics_list`.
    3. Generate a comprehensive study schedule.
    """
    if not FLATTENED_TOPICS:
        print("Warning: No biology topics loaded from curriculum. Cannot generate specific schedule.")
        return [{"day": d, "topics": [f"General Study Day {d} - No specific topics (Curriculum not loaded)"]} for d in range(1, days + 1)]

    # --- Step 1: Topic Extraction and Weightage Calculation using Grok AI ---
    print("\nStarting topic analysis using Grok AI...")
    topic_weights = Counter() # Using Counter to store topic frequencies/importance scores

    # Iterate through each document (PYQ/Textbook Chapter)
    for doc_path, doc_content in document_contents.items():
        print(f"Analyzing document: {os.path.basename(doc_path)}")
        
        # Grok models have context windows (e.g., 8192 tokens).
        # It's crucial to ensure `doc_content` fits within the model's context.
        # For very large documents, you might need to chunk `doc_content` and send multiple prompts.
        # For demonstration, we'll use a slice, but in production, consider proper tokenization/chunking.
        max_prompt_length = 8000 # A conservative estimate for prompt + completion tokens
        content_to_send = doc_content[:max_prompt_length] # Take first N characters

        # --- Grok AI Prompt for Topic Extraction and Scoring ---
        prompt_for_topics = f"""
        Analyze the following text from a Biology exam paper or textbook.
        Identify which of the following 12th-grade Biology topics are discussed in this text.
        For each identified topic, assign a relevance score from 1 (low) to 5 (high) based on how prominently or frequently it appears, or how central it is to the text.
        
        List of 12th-grade Biology topics: {', '.join(curriculum_topics_list)}

        Text:
        ---
        {content_to_send}
        ---

        Provide the output as a JSON array of objects, where each object has "topic" (string) and "score" (integer).
        Example:
        [
          {{"topic": "Human Reproduction", "score": 4}},
          {{"topic": "Gametogenesis", "score": 3}}
        ]
        Only provide the JSON array in your response.
        """
        
        # --- Make a call to Grok AI ---
        try:
            chat_completion = groq_client.chat.completions.create( # Uncommented: Grok AI call
                messages=[
                    {"role": "user", "content": prompt_for_topics}
                ],
                model="llama3-8b-8192", # Choose an appropriate Groq model
                response_format={"type": "json_object"} # Request JSON output
            )
            grok_response_text = chat_completion.choices[0].message.content
            try:
                grok_topics_data = json.loads(grok_response_text)
                if isinstance(grok_topics_data, list): # Ensure it's a list
                    for item in grok_topics_data:
                        topic = item.get("topic")
                        score = item.get("score", 0)
                        if topic and score is not None and isinstance(score, (int, float)):
                            topic_weights[topic] += int(score) # Aggregate scores across documents
                            print(f"  - Grok identified '{topic}' with score {int(score)}")
                else:
                    print(f"  - Grok AI response was not a JSON list: {grok_response_text[:200]}...")
            except json.JSONDecodeError:
                print(f"  - Grok AI response was not valid JSON: {grok_response_text[:200]}...")
            except Exception as e:
                print(f"  - Error processing Grok AI response for {os.path.basename(doc_path)}: {e}")
        except Exception as e:
            print(f"  - Error calling Grok AI for {os.path.basename(doc_path)}: {e}")
            # Fallback to simple keyword matching if Grok AI call fails (optional)
            for topic in curriculum_topics_list:
                if re.search(r'\b' + re.escape(topic.lower()) + r'\b', doc_content.lower()):
                    topic_weights[topic] += 1 # Add a base weight for simple match


    if not topic_weights:
        print("No curriculum topics found in documents by Grok AI analysis. Generating generic schedule.")
        return [{"day": d, "topics": [f"General Study Day {d} - No specific topics found"]} for d in range(1, days + 1)]

    # Sort topics by their aggregated weightage in descending order
    sorted_weighted_topics = sorted(topic_weights.items(), key=lambda item: item[1], reverse=True)
    print("\nTopics by aggregated weightage (most important first):")
    for topic, weight in sorted_weighted_topics:
        print(f"  - {topic}: {weight}")

    # --- Step 2: Schedule Generation Logic (Further Grok AI integration) ---
    print(f"\nGenerating schedule for {days} days with target score {target_score}% using weighted topics...")

    prompt_for_schedule = f"""
    You are a study planner. Create a {days}-day study schedule for a student aiming for {target_score}% in Biology.
    Prioritize the following topics based on their importance/weightage (higher score means more important/frequent in past exams):
    {json.dumps(sorted_weighted_topics)}

    Ensure a balanced schedule. Suggest specific topics for each day.
    For revision days, suggest "Review" or "Practice PYQs" for high-weightage topics.
    Provide the output as a JSON array of objects, where each object has "day" (integer) and "topics" (array of strings).
    Ensure each day has at least one topic.
    Example:
    [
      {{"day": 1, "topics": ["Photosynthesis: Light Reactions", "Cellular Respiration: Glycolysis"]}},
      {{"day": 2, "topics": ["Mendelian Genetics", "Human Reproduction (Revision)"]}}
    ]
    Only provide the JSON array in your response.
    """

    final_schedule = []
    try:
        chat_completion_schedule = groq_client.chat.completions.create( # Uncommented: Grok AI call
            messages=[
                {"role": "user", "content": prompt_for_schedule}
            ],
            model="llama3-8b-8192", # Or another suitable Groq model
            response_format={"type": "json_object"}
        )
        grok_schedule_response_text = chat_completion_schedule.choices[0].message.content
        temp_parsed_schedule = json.loads(grok_schedule_response_text)
        
        # Validate the structure of the Grok AI generated schedule
        if isinstance(temp_parsed_schedule, list) and all(isinstance(item, dict) and 'day' in item and 'topics' in item and isinstance(item['topics'], list) for item in temp_parsed_schedule):
            final_schedule = temp_parsed_schedule
            print("Schedule generated by Grok AI.")
        else:
            print(f"Grok AI generated schedule in unexpected format: {grok_schedule_response_text[:200]}...")
            print("Falling back to basic schedule generation.")
            # Proceed to fallback logic
    except Exception as e:
        print(f"Error generating schedule with Grok AI: {e}")
        print("Falling back to basic schedule generation.")
        # Fallback if Grok AI schedule generation fails
        pass

    # --- FALLBACK/MOCK SCHEDULE GENERATION (IF GROK AI IS NOT USED OR FAILS) ---
    # This section will be executed if Grok AI call is commented or fails, or if its output is invalid.
    if not final_schedule: # Only run fallback if Grok AI didn't provide a valid schedule
        print("Using fallback schedule generation.")
        temp_schedule = [{"day": i + 1, "topics": []} for i in range(days)]
        current_topic_idx = 0
        
        # Prepare topics for scheduling based on their weight (simple repetition)
        all_topics_for_scheduling = []
        if sorted_weighted_topics: # Use weighted topics if available
            for topic, weight in sorted_weighted_topics:
                # Add topic multiple times based on its weight. Max repetition for very high weight.
                num_repetitions = max(1, int(weight / (sum(dict(sorted_weighted_topics).values()) / len(sorted_weighted_topics) / 2)))
                all_topics_for_scheduling.extend([topic] * num_repetitions)
        
        # If no weighted topics or all_topics_for_scheduling is still empty (e.g., if Grok AI failed and no initial topics)
        if not all_topics_for_scheduling and FLATTENED_TOPICS:
            all_topics_for_scheduling = list(FLATTENED_TOPICS) # Fallback to all topics from curriculum
        
        # Ensure there are topics to schedule, otherwise use general days
        if not all_topics_for_scheduling:
            return [{"day": d, "topics": [f"General Study Day {d} - No specific topics found"]} for d in range(1, days + 1)]


        # Distribute topics across days
        topics_per_slot = max(1, len(all_topics_for_scheduling) // days)

        for day_idx in range(days):
            topics_for_day = []
            for _ in range(topics_per_slot):
                if current_topic_idx < len(all_topics_for_scheduling):
                    topics_for_day.append(all_topics_for_scheduling[current_topic_idx])
                    current_topic_idx += 1
            
            # If a day ends up empty but there are remaining topics, add one
            if not topics_for_day and current_topic_idx < len(all_topics_for_scheduling):
                 topics_for_day.append(all_topics_for_scheduling[current_topic_idx])
                 current_topic_idx += 1

            # If all specific topics are assigned, add a general review/practice day
            if not topics_for_day:
                topics_for_day.append("Review & Practice PYQs")
            
            # Remove duplicates for the same day (maintain order)
            temp_schedule[day_idx]['topics'] = list(dict.fromkeys(topics_for_day))

        final_schedule = temp_schedule


    return final_schedule


# --- API Endpoint for Schedule Generation ---
@app.route('/api/generate-schedule', methods=['POST'])
def generate_schedule_endpoint():
    data = request.get_json()
    subject = data.get('subject')
    preparation_days = data.get('preparationDays')
    target_score = data.get('targetScore')

    # Basic validation
    if not all([subject, preparation_days, target_score]):
        return jsonify({'message': 'Missing required fields (subject, preparationDays, targetScore)'}), 400

    if subject.lower() != 'biology':
        return jsonify({'message': 'Currently only "Biology" subject is supported.'}), 400

    if not ALL_DOCUMENT_CONTENTS:
        return jsonify({'message': 'No PYQ or Textbook documents found or readable in data directories. Check data/pyqs and data/textbooks.'}), 500

    try:
        schedule = analyze_and_generate_schedule(
            subject,
            preparation_days,
            target_score,
            FLATTENED_TOPICS, # Pass the flattened list of curriculum topics
            ALL_DOCUMENT_CONTENTS # Pass the combined content of all documents
        )
        return jsonify({'schedule': schedule}), 200
    except Exception as e:
        print(f"An error occurred during schedule generation: {e}")
        import traceback
        traceback.print_exc() # Print full traceback to console
        return jsonify({'message': 'Failed to generate schedule due to an internal error.', 'error': str(e)}), 500

# --- Run the Flask app ---
if __name__ == '__main__':
    # Temporarily set debug=False to prevent immediate restarts and see the error
    app.run(debug=False, port=5000)