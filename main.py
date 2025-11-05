from openai import OpenAI
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

def load_knowledge_base() -> Dict[str, Any]:
    """Load all knowledge base files into memory"""
    knowledge_base = {}
    kb_directory = "knowledge_base"
    
    if not os.path.exists(kb_directory):
        return knowledge_base
    
    for filename in os.listdir(kb_directory):
        if filename.endswith('.json'):
            filepath = os.path.join(kb_directory, filename)
            try:
                with open(filepath, 'r') as f:
                    category = filename.replace('.json', '')
                    knowledge_base[category] = json.load(f)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return knowledge_base

def get_relevant_knowledge(query: str, knowledge_base: Dict[str, Any]) -> str:
    """Search knowledge base for relevant information based on query"""
    query_lower = query.lower()
    relevant_info = []
    
    # Search through different categories
    for category, data in knowledge_base.items():
        if any(keyword in query_lower for keyword in [category, 'help', 'how', 'what', 'technique']):
            relevant_info.append(f"\n--- {category.upper()} KNOWLEDGE ---")
            relevant_info.append(json.dumps(data, indent=2))
    
    # Search for specific terms
    search_terms = {
        'forehand': ['strokes'],
        'backhand': ['strokes'], 
        'serve': ['strokes'],
        'volley': ['strokes'],
        'strategy': ['strategy'],
        'fitness': ['fitness'],
        'equipment': ['equipment'],
        'racquet': ['equipment'],
        'string': ['equipment'],
        'grip': ['strokes', 'equipment']
    }
    
    for term, categories in search_terms.items():
        if term in query_lower:
            for cat in categories:
                if cat in knowledge_base:
                    relevant_info.append(f"\n--- {cat.upper()} KNOWLEDGE ---")
                    relevant_info.append(json.dumps(knowledge_base[cat], indent=2))
                    break
    
    return '\n'.join(relevant_info[:2000])  # Limit context length

# Load knowledge base at startup
knowledge_base = load_knowledge_base()

conversation_history = [
    {
        "role": "system", 
        "content": """You are an experienced tennis coach with over 15 years of coaching experience. 
        You specialize in helping players of all skill levels improve their game. You provide:
        
        - Technical advice on strokes (forehand, backhand, serve, volley)
        - Strategy and tactics for singles and doubles play
        - Mental game coaching and confidence building
        - Fitness and conditioning tips specific to tennis
        - Equipment recommendations
        - Match preparation and analysis
        
        Keep your responses encouraging, practical, and tailored to the player's skill level. 
        Ask follow-up questions to better understand their needs and current abilities.
        
        When relevant knowledge base information is provided, use it to give detailed, accurate answers.
        Always cite specific techniques, drills, or recommendations from the knowledge base when available."""
    }
]

def chat_with_tennis_coach(prompt):
    # Get relevant knowledge for this query
    relevant_knowledge = get_relevant_knowledge(prompt, knowledge_base)
    
    # Add user message
    conversation_history.append({"role": "user", "content": prompt})
    
    # If we have relevant knowledge, add it as context
    if relevant_knowledge:
        knowledge_message = {
            "role": "system",
            "content": f"Here is relevant knowledge base information to help answer the user's question:\n{relevant_knowledge}"
        }
        messages_with_knowledge = conversation_history + [knowledge_message]
    else:
        messages_with_knowledge = conversation_history
    
    response = client.chat.completions.create(
        model='gpt-3.5-turbo-0125',
        messages=messages_with_knowledge
    )
    
    assistant_message = response.choices[0].message.content.strip()
    conversation_history.append({"role": "assistant", "content": assistant_message})
    
    return assistant_message

if __name__ == "__main__":
    print("🎾 Welcome to your Personal Tennis Coach! 🎾")
    print("I'm here to help improve your tennis game.")
    print("Ask me about technique, strategy, fitness, or anything tennis-related!")
    print("Type 'quit', 'exit', or 'bye' to end our session.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("\nTennis Coach: Great session! Keep practicing and remember - every pro was once a beginner. See you on the court! 🎾")
            break
        
        response = chat_with_tennis_coach(user_input)
        print(f"Tennis Coach: {response}\n")