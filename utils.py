from pprint import pprint

def log_documents(documents):
    # Pretty print the list of Documents
    for doc in documents:
        print("\nDocument:")
        print("---------")
        pprint(doc)
