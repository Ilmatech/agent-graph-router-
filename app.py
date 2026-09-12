import os
import networkx as nx
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize the Free Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def agent_categorizer(prompt):
    print(f"\n[Categorizer] Inspecting prompt complexity using Gemini...")
    response = client.models.generate_content(
        model="gemini-3.6-flash",  
        contents=f"Analyze the user prompt. Respond with exactly one word: 'easy' if it is a simple text cleanup/formatting task, or 'hard' if it requires heavy math, complex coding, or deep logical reasoning. Prompt: {prompt}"
    )
    return response.text.strip().lower()

def agent_formatter(data):
    print("[Formatter Agent] Triggering low-cost formatting node...")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"Take this input and format it into a neat valid JSON structure wrapper with a success status code: {data}"
    )
    return response.text

def agent_expert(data):
    print("[Expert Agent] CRITICAL ALERT: Routing to high-reasoning execution node...")
    response = client.models.generate_content(
        model="gemini-3.6-flash",  # Using the robust 3.6 Flash model
        contents=f"You are a senior computer science researcher. Provide a detailed, highly accurate algorithmic solution to this complex problem: {data}"
    )
    return response.text

# --- Graph Engine Map Configuration ---
G = nx.DiGraph()
G.add_edge("USER_PROMPT", "CATEGORIZER", weight=0)
G.add_edge("CATEGORIZER", "FORMATTER", weight=1)
G.add_edge("CATEGORIZER", "EXPERT", weight=15)
G.add_edge("FORMATTER", "OUTPUT", weight=0)
G.add_edge("EXPERT", "OUTPUT", weight=0)

def run_routing_engine(user_prompt):
    try:
        complexity = agent_categorizer(user_prompt)
        print(f"-> AI classified this prompt as: {complexity.upper()}")
        
        if "hard" in complexity:
            target_path = ["USER_PROMPT", "CATEGORIZER", "EXPERT", "OUTPUT"]
            result = agent_expert(user_prompt)
        else:
            target_path = ["USER_PROMPT", "CATEGORIZER", "FORMATTER", "OUTPUT"]
            result = agent_formatter(user_prompt)
            
        path_cost = sum(G[target_path[i]][target_path[i+1]]['weight'] for i in range(len(target_path)-1))
        print(f"Calculated Trajectory: {' -> '.join(target_path)} (Weight Factor: {path_cost})")
        print(f"\n[FINAL OUTPUT]:\n{result}\n")
        
    except Exception as e:
        print(f"\n❌ API Error: Details: {e}")

if __name__ == "__main__":
    # Test Run with a hard computer science prompt to trigger the expert node path
    run_routing_engine("Write a complex Python script to calculate dynamic matrix structures using custom Graph Theory edge weights and explain the mathematical runtime.")
