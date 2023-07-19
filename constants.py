from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

CONVERSATIONS_FOLDER = "conversation-samples"

QA_FOLDER = "qa"

# Use the variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

RECRUITER_SEQUENCE_MESSAGE_1 = "Hi <FIRST_NAME>! Thanks for connecting. I'm also looking for a mobile developer (React Native) for an ambitious San Fransisco based startup. They are transforming the analytics space for creators and have already helped millions of YouTube creators take their channels to the next level — grow their views and subscribers. The startup is currently scaling the team with talented React Native engineers. After looking at your background, I think you'd be a great fit!Are you open to such an opportunity, <FIRST_NAME>?"
RECRUITER_CONNECT_MESSAGE = "Hi <FIRST_NAME>! My name is <RECUITER_NAME>. I'm a tech recruiter at Insquad, a talent platform that connects developers with top-notch US tech jobs. Let's connect!"

RECRUITER_MODEL_BASE_PROMPT = "You are a Tech recruiter at Insquad. Insquad is a cloud platform, which constitutes a talent pool of developers which can be accessed by tech companies. " \
                              "Developers from the talent pool can be hired for remote only full-time jobs upon demand. Developers who register on the platform to become part of the talent pool pass an internal vetting process which includes a quiz and a coding challenge. " \
                              "This process is taken once only and takes 1 hour max. You're talking to a developer on LinkedIn about Insquad. " \
                              "Keep your responses under 200 symbols, use neutral style of written communication in English and focus on splitting your text into paragraphs with 3 sentences max in each one. " \
                              "You must not push candidate to call or any kind of live communication, as you are AI model and cannot do that. " \
                              "You must push candidates to our platform primarily: dev.insquad.com." \
                              "Answer to a candidate's question: {candidate_question} according to the chat context understanding: {conversation_context} and the basic prompt above."
