from agents.coordinator_agent import coordinate_chat

if __name__ == "__main__":
    user_question = "Describe the file"
    document_folder = "docs\Cars Datasets 2025.csv"
    answer = coordinate_chat(user_question, document_folder)
    print("\nFINAL ANSWER:\n", answer)
