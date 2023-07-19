import os
import re
import logging
import html

# import directory constants
from constants import CONVERSATIONS_FOLDER
from constants import QA_FOLDER

# defining identifiers that belong to the recruiter
recruiter_identifiers = ["insquad.com", "gavnikal@gmail.com"]

# setting up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_recruiter(email):
    # checks if email belongs to the recruiter
    return any(identifier in email for identifier in recruiter_identifiers)

def read_conversations(conversations_folder):
    # reads all conversations from txt files
    conversations = {}
    for root, dirs, files in os.walk(conversations_folder):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), 'r') as f:
                    conversations[file] = f.readlines()
    return conversations

def parse_conversations(conversations):
    # parses conversations, extracting questions and answers
    qa_pairs = {}
    total_pairs = 0
    for file, conversation in conversations.items():
        question = ""
        answer = ""
        prev_line = None
        for line in conversation:
            line = line.strip()
            if line == prev_line or not line:  # ignores duplicate or empty lines
                continue
            prev_line = line
            if not re.match(r"\d+:\d+ [APM]* \d{2}-\d{2}-\d{4}", line):  # skips lines without timestamps
                continue
            try:
                _, remaining = line.split(" ", 1)
                email, text = re.split(r' - ', remaining, 1)  # extracts email and text from line
                text = html.unescape(text)  # unescapes HTML characters
            except ValueError:
                logging.warning(f"Unexpected line format: {line}")
                continue
            if is_recruiter(email):
                # if recruiter's message, treats it as an answer
                if question.strip():
                    answer = text
                    if file not in qa_pairs:
                        qa_pairs[file] = []
                    qa_pairs[file].append((question, answer))  # stores the QA pair
                    question = ""
                    answer = ""
                    total_pairs += 1
            else:
                # if candidate's message, treats it as a question
                question += " " + text
        if question.strip() and answer.strip():
            qa_pairs[file].append((question, answer))  # stores the last QA pair
            total_pairs += 1
    logging.info(f"Total QA pairs parsed: {total_pairs}")
    return qa_pairs

def write_qa(qa_pairs, qa_folder):
    # writes QA pairs to txt files
    os.makedirs(qa_folder, exist_ok=True)
    for file, pairs in qa_pairs.items():
        file_folder = os.path.join(qa_folder, os.path.splitext(file)[0])
        os.makedirs(file_folder, exist_ok=True)
        for i, (q, a) in enumerate(pairs):
            with open(os.path.join(file_folder, f"qa_{i}.txt"), 'w') as f:
                f.write(f"Q: {q}\n\nA: {a}\n")

# read, parse, and write conversations
conversations = read_conversations(CONVERSATIONS_FOLDER)
qa_pairs = parse_conversations(conversations)
write_qa(qa_pairs, QA_FOLDER)
