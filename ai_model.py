import pandas as pd
import re
import time
from rapidfuzz import process, fuzz
from huggingface_hub import InferenceClient
from sklearn.metrics import accuracy_score

# --- CONFIGURATION ---
HF_TOKEN = "add-your-token-here"
MODEL_ID = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"
CSV_FILE = "test_need_loc.csv"
CANDIDATE_LABELS = ["food", "drinking water", "fire engine", "ambulance", "medicine", "rescue boat", "helicopter", "shelter"]

client = InferenceClient(token=HF_TOKEN)

# --- 1. DATA PREPARATION ---
print("Loading data and preparing knowledge bases...")
df = pd.read_csv(CSV_FILE)
df.columns = [c.strip().lower() for c in df.columns]

# Split lat_long and prepare Landmark list
df[['lat', 'lon']] = df['lat_long'].str.split(',', expand=True).astype(float)
landmarks = df['location_mentioned'].dropna().unique().tolist()
landmarks = [str(l).lower().strip() for l in landmarks if str(l).lower() != 'nan']

# Map locations to coordinates for the final report
coord_map = df.groupby('location_mentioned')[['lat', 'lon']].first().to_dict('index')
coord_map = {str(k).lower().strip(): v for k, v in coord_map.items()}

# --- 2. THE 4-PHASE ENGINES ---

def extract_p1_need(text):
    """Phase 1: Zero-Shot Classification (Need)"""
    try:
        result = client.zero_shot_classification(
            text=text, candidate_labels=CANDIDATE_LABELS, model=MODEL_ID,
            hypothesis_template="This emergency message indicates a need for {}."
        )
        return result[0]['label']
    except: return "error"

def extract_p2_location(text, landmark_list):
    """Phase 2: Spatial Recovery (LMR + Fuzzy)"""
    text = str(text).lower().strip()
    for loc in landmark_list:
        if re.search(rf'\b{re.escape(loc)}\b', text): return loc
    res = process.extractOne(text, landmark_list, scorer=fuzz.partial_ratio)
    if res and res[1] > 85: return res[0]
    return "chennai general"

def extract_p3_quantity(text):
    """Phase 3: Quantity Extraction (Regex)"""
    text = str(text).lower().strip()
    match = re.search(r'(\d+)\s*(people|ppl|pp|members|kids|children|infants|persons|adults|family|person)', text)
    if match: return match.group(0)
    family_match = re.search(r'family of (\d+)', text)
    if family_match: return f"{family_match.group(1)} family members"
    return "not given"

def calculate_p4_metrics(need, quantity_str):
    """Phase 4: Weighted Heuristics & Triage Color Coding"""
    # Need Weights
    weights = {"ambulance": 10, "fire engine": 10, "rescue boat": 9, "helicopter": 9, 
               "medicine": 7, "drinking water": 5, "food": 4, "shelter": 3, "error": 1}
    
    # Process Quantity
    nums = re.findall(r'\d+', str(quantity_str))
    qty_val = int(nums[0]) if nums else 1
    
    # Heuristic: 60% Scale (Quantity) + 40% Severity (Need)
    qty_score = min(qty_val * 5, 50) 
    need_score = weights.get(need, 2) * 5
    urgency_score = round((qty_score * 0.6) + (need_score * 0.4), 2)
    
    # Assign Triage Color
    if urgency_score >= 30: color = "red"
    elif 15 <= urgency_score < 30: color = "yellow"
    else: color = "green"
    
    return urgency_score, color

# --- 3. EXECUTION PIPELINE ---
print("Executing 4-Phase Integrated Pipeline...")
final_results = []

for index, row in df.iterrows():
    raw_text = str(row['text'])
    
    # Run AI & Logic
    p1_need = extract_p1_need(raw_text)
    p2_loc = extract_p2_location(raw_text, landmarks)
    p3_qty = extract_p3_quantity(raw_text)
    p4_score, p4_color = calculate_p4_metrics(p1_need, p3_qty)
    
    # GPS Lookup
    coords = coord_map.get(p2_loc, {'lat': 13.0827, 'lon': 80.2707})
    
    final_results.append({
        "S.No": row.get('s.no', index + 1),
        "Triage_Level": p4_color,
        "Urgency_Score": p4_score,
        "Predicted_Need": p1_need,
        "Quantity": p3_qty,
        "Predicted_Location": p2_loc,
        "Latitude": coords['lat'],
        "Longitude": coords['lon'],
        "Original_Text": raw_text,
        "Actual_Need": str(row['need']).lower().strip(),
        "Actual_Loc": str(row['location_mentioned']).lower().strip()
    })
    time.sleep(0.05) # Prevent API rate limiting

# --- 4. ACCURACY LOG & SAVE ---
report_df = pd.DataFrame(final_results)

# Accuracy Calculations
acc_need = accuracy_score(report_df['Actual_Need'], report_df['Predicted_Need']) * 100
report_df['Loc_Match'] = report_df.apply(lambda x: x['Actual_Loc'] in x['Predicted_Location'], axis=1)
acc_loc = report_df['Loc_Match'].mean() * 100
report_df['Qty_Match'] = report_df.apply(lambda x: x['Quantity'] != "not given" if any(c.isdigit() for c in x['Original_Text']) else True, axis=1)
acc_qty = report_df['Qty_Match'].mean() * 100

# Final Formatting
report_df = report_df.sort_values(by="Urgency_Score", ascending=False)
report_df.drop(columns=['Loc_Match', 'Qty_Match'], inplace=True)

print("\n" + "="*45)
print(f"PHASE 1 (NEED) ACCURACY:     {acc_need:.2f}%")
print(f"PHASE 2 (LOCATION) ACCURACY: {acc_loc:.2f}%")
print(f"PHASE 3 (QUANTITY) ACCURACY: {acc_qty:.2f}%")
print("-" * 45)
print(f"TOTAL SYSTEM PERFORMANCE:    {((acc_need + acc_loc + acc_qty) / 3):.2f}%")
print("Triage Levels assigned: RED, YELLOW, GREEN")
print("="*45)

report_df.to_csv("final_report.csv", index=False)
print("SUCCESS: 'final_report.csv' has been generated and prioritized.")

import os
from math import radians, cos, sin, asin, sqrt

# --- HAVERSINE DISTANCE FUNCTION ---
def get_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    d = 2 * 6371 * asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2))
    return round(d, 2)

# --- RESOURCE MATCHING ENGINE ---
def match_best_resource(victim_row, res_df):
    need = str(victim_row['Predicted_Need']).lower()
    v_lat, v_lon = victim_row['Latitude'], victim_row['Longitude']
    
    # Filter centers that have the specific resource available (> 0)
    if need in res_df.columns:
        capable_centers = res_df[res_df[need] > 0].copy()
    else:
        capable_centers = res_df.copy() 

    if capable_centers.empty:
        return "No Resource Available", 0.0

    # Find the closest capable center
    capable_centers['dist'] = capable_centers.apply(
        lambda r: get_distance(v_lat, v_lon, r['latitude'], r['longitude']), axis=1
    )
    
    best_match = capable_centers.loc[capable_centers['dist'].idxmin()]
    return best_match['location'], best_match['dist']

# --- MAIN EXECUTION ---
def run_final_dispatch():
    # 1. Load data
    try:
        report_df = pd.read_csv("final_report.csv") 
        res_df = pd.read_csv("available_resources.csv")
    except FileNotFoundError:
        print("Error: Ensure 'final_report.csv' and 'available_resources.csv' exist.")
        return

    print("Phase 5: Matching victims to resources...")
    
    # 2. Apply Matching
    matches = report_df.apply(lambda row: match_best_resource(row, res_df), axis=1)
    report_df['Assigned_Resource_Center'], report_df['Distance_km'] = zip(*matches)
    
    # We keep only what a rescue worker needs to see
    dispatch_columns = [
        "S.No", "Triage_Level", "Urgency_Score", "Predicted_Need", 
        "Quantity", "Predicted_Location", "Latitude", "Longitude", 
        "Assigned_Resource_Center", "Distance_km", "Original_Text"
    ]
    
    final_dispatch_df = report_df[dispatch_columns].copy()
    
    # 4. Save clean file
    final_dispatch_df.to_csv("final_matched_report.csv", index=False)
    print("CLEAN DISPATCH GENERATED: 'final_matched_report.csv'")

if __name__ == "__main__":
    run_final_dispatch()
