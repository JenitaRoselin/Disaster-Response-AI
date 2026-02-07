import pandas as pd
import re
import time
import os
from math import radians, cos, sin, asin, sqrt
from rapidfuzz import process, fuzz
from huggingface_hub import InferenceClient
from sklearn.metrics import accuracy_score

# --- CONFIGURATION ---
HF_TOKEN = "add-your-HuggingFace-fine-grain-token-here"
MODEL_ID = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"
CANDIDATE_LABELS = ["food", "drinking water", "fire engine", "ambulance", "medicine", "rescue boat", "helicopter", "shelter"]

class DisasterAI:
    def __init__(self, token=HF_TOKEN):
        print("Initializing AI Engine and Knowledge Bases...")
        self.client = InferenceClient(token=token)
        self.landmarks = []
        self.coord_map = {}
        self.res_df = None
        self._load_knowledge()

    def _load_knowledge(self):
        """Loads landmarks and resource data for spatial recovery and haversine matching."""
        try:
            # Load landmarks from your test file
            df = pd.read_csv("test_need_loc.csv")
            df.columns = [c.strip().lower() for c in df.columns]
            df[['lat', 'lon']] = df['lat_long'].str.split(',', expand=True).astype(float)
            
            self.landmarks = df['location_mentioned'].dropna().unique().tolist()
            self.landmarks = [str(l).lower().strip() for l in self.landmarks if str(l).lower() != 'nan']
            
            # Map locations to coordinates
            self.coord_map = df.groupby('location_mentioned')[['lat', 'lon']].first().to_dict('index')
            self.coord_map = {str(k).lower().strip(): v for k, v in self.coord_map.items()}
            
            # Load available resources
            if os.path.exists("available_resources.csv"):
                self.res_df = pd.read_csv("available_resources.csv")
        except Exception as e:
            print(f"Warning: Knowledge base loading failed: {e}")

    # --- PHASE 1: NEED PREDICTION ---
    def extract_need(self, text):
        try:
            result = self.client.zero_shot_classification(
                text=text, candidate_labels=CANDIDATE_LABELS, model=MODEL_ID,
                hypothesis_template="This emergency message indicates a need for {}."
            )
            return result[0]['label']
        except: return "error"

    # --- PHASE 2: SPATIAL RECOVERY ---
    def extract_location(self, text):
        text = str(text).lower().strip()
        for loc in self.landmarks:
            if re.search(rf'\b{re.escape(loc)}\b', text): return loc
        res = process.extractOne(text, self.landmarks, scorer=fuzz.partial_ratio)
        if res and res[1] > 85: return res[0]
        return "chennai general"

    # --- PHASE 3: QUANTITY ---
    def extract_quantity(self, text):
        text = str(text).lower().strip()
        match = re.search(r'(\d+)\s*(people|ppl|pp|members|kids|children|infants|persons|adults|family|person)', text)
        if match: return match.group(0)
        family_match = re.search(r'family of (\d+)', text)
        if family_match: return f"{family_match.group(1)} family members"
        return "not given"

    # --- PHASE 4: TRIAGE SCORING ---
    def calculate_metrics(self, need, quantity_str):
        weights = {"ambulance": 10, "fire engine": 10, "rescue boat": 9, "helicopter": 9, 
                   "medicine": 7, "drinking water": 5, "food": 4, "shelter": 3, "error": 1}
        nums = re.findall(r'\d+', str(quantity_str))
        qty_val = int(nums[0]) if nums else 1
        qty_score = min(qty_val * 5, 50) 
        need_score = weights.get(need, 2) * 5
        urgency_score = round((qty_score * 0.6) + (need_score * 0.4), 2)
        
        if urgency_score >= 30: color = "red"
        elif 15 <= urgency_score < 30: color = "yellow"
        else: color = "green"
        return urgency_score, color

    # --- PHASE 5: HAVERSINE RESOURCE MATCHING ---
    def get_distance(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        d = 2 * 6371 * asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2))
        return round(d, 2)

    def match_resource(self, need, lat, lon):
        if self.res_df is None: return "No Resource DB", 0.0
        need = str(need).lower()
        capable_centers = self.res_df[self.res_df[need] > 0].copy() if need in self.res_df.columns else self.res_df.copy()
        
        if capable_centers.empty: return "No Resource Available", 0.0
        
        capable_centers['dist'] = capable_centers.apply(
            lambda r: self.get_distance(lat, lon, r['latitude'], r['longitude']), axis=1
        )
        best_match = capable_centers.loc[capable_centers['dist'].idxmin()]
        return best_match['location'], best_match['dist']

    # --- INTEGRATION PORT (For the Frontend) ---
    def process_single_ticket(self, raw_text):
        """Used by app.py to process a single user input from the UI."""
        need = self.extract_need(raw_text)
        loc = self.extract_location(raw_text)
        qty = self.extract_quantity(raw_text)
        score, color = self.calculate_metrics(need, qty)
        
        coords = self.coord_map.get(loc, {'lat': 13.0827, 'lon': 80.2707})
        res_name, dist = self.match_resource(need, coords['lat'], coords['lon'])
        
        return {
            "need": need,
            "location": loc,
            "quantity": qty,
            "urgency": score,
            "triage": color,
            "assigned_center": res_name,
            "distance_km": dist
        }

# --- BATCH PROCESSING (For the Accuracy Proof) ---
def run_batch_processing(engine, input_csv="test_need_loc.csv"):
    print(f"Executing Batch Pipeline on {input_csv}...")
    df = pd.read_csv(input_csv)
    df.columns = [c.strip().lower() for c in df.columns]
    
    results = []
    for _, row in df.iterrows():
        res = engine.process_single_ticket(row['text'])
        # Add actuals for accuracy checking
        res["Actual_Need"] = str(row['need']).lower().strip()
        res["Actual_Loc"] = str(row['location_mentioned']).lower().strip()
        res["Original_Text"] = row['text']
        results.append(res)
        time.sleep(0.02)
    
    report_df = pd.DataFrame(results)
    
    # Calculate Accuracy Metrics
    acc_need = accuracy_score(report_df['Actual_Need'], report_df['need']) * 100
    print(f"\nBATCH ACCURACY (NEED): {acc_need:.2f}%")
    
    report_df.to_csv("final_matched_report.csv", index=False)
    print("SUCCESS: 'final_matched_report.csv' generated.")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Initialize engine
    engine = DisasterAI()
    
    # Run the batch test for proof of accuracy
    run_batch_processing(engine)
