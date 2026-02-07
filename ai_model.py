import pandas as pd
import re
import time
import os
from rapidfuzz import process, fuzz
from huggingface_hub import InferenceClient
from sklearn.metrics import accuracy_score

# --- CONFIGURATION ---
HF_TOKEN = os.getenv("HF_TOKEN", "add-your-token-here")
MODEL_ID = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"
CSV_FILE = "test_need_loc.csv"
CANDIDATE_LABELS = ["food", "drinking water", "fire engine", "ambulance", "medicine", "rescue boat", "helicopter", "shelter"]

client = InferenceClient(token=HF_TOKEN)

def extract_p1_need(text):
    try:
        result = client.zero_shot_classification(
            text=text, candidate_labels=CANDIDATE_LABELS, model=MODEL_ID,
            hypothesis_template="This emergency message indicates a need for {}."
        )
        return result[0]['label']
    except: return "error"

def extract_p2_location(text, landmark_list):
    text = str(text).lower().strip()
    for loc in landmark_list:
        if re.search(rf'\b{re.escape(loc)}\b', text): return loc
    res = process.extractOne(text, landmark_list, scorer=fuzz.partial_ratio)
    if res and res[1] > 85: return res[0]
    return "chennai general"

def extract_p3_quantity(text):
    text = str(text).lower().strip()
    match = re.search(r'(\d+)\s*(people|ppl|pp|members|kids|children|infants|persons|adults|family|person)', text)
    if match: return match.group(0)
    family_match = re.search(r'family of (\d+)', text)
    if family_match: return f"{family_match.group(1)} family members"
    return "not given"

def calculate_p4_metrics(need, quantity_str):
    weights = {"ambulance": 10, "fire engine": 10, "rescue boat": 9, "helicopter": 9, 
               "medicine": 7, "drinking water": 5, "food": 4, "shelter": 3, "error": 1}
    nums = re.findall(r'\d+', str(quantity_str))
    qty_val = int(nums[0]) if nums else 1
    qty_score = min(qty_val * 5, 50) 
    need_score = weights.get(need, 2) * 5
    urgency_score = round((qty_score * 0.6) + (need_score * 0.4), 2)
    color = "red" if urgency_score >= 30 else "yellow" if urgency_score >= 15 else "green"
    return urgency_score, color

# Pipeline logic omitted for brevity in script version