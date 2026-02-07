# CrisisFlow
*Disaster Response AI: End-to-End Triage & Resource Dispatch*

---
## 1. About the Project
This project is an **AI-driven Emergency Dispatch Engine** designed to handle the chaos of unstructured communication during disasters. It takes messy, informal text messages (like those sent during floods) and uses Natural Language Processing (NLP) and Geospatial Intelligence to automatically categorize, prioritize, and match victims with the nearest available rescue resources.

---
## 2. Who it was built for
This was developed for **Emergency Management Agencies and First Responders** (specifically modeled for the **Chennai Metro** region). The goal is to reduce the "Data-to-Action" lag time that occurs when human dispatchers are overwhelmed by thousands of requests.

---
## 3. Features Included in Demo
* **Zero-Shot NLP:** Classifies needs (Food, Medical, Rescue) without requiring specific training data.
* **Fuzzy Spatial Recovery:** Corrects misspelled locations and maps them to precise GPS coordinates.
* **Automated Triage:** A weighted heuristic engine that color-codes cases by urgency (**Red/Yellow/Green**).
* **Smart Resource Matching:** Uses the **Haversine Formula** to cross-reference victim location against a live inventory (`available_resources.csv`) to assign the nearest capable center.
* **Autonomous Reporting:** Generates a final, ready-to-use dispatch sheet (`final_matched_report.csv`) with zero manual input required.


---
## 4. Accuracy Scores
The system self-evaluates by comparing AI predictions against historical ground-truth data:

| Phase | Engine | Accuracy |
| :--- | :--- | :--- |
| **Phase 1: Need Classification** | DeBERTa-v3-large | 42.86% |
| **Phase 2: Location Recovery** | RapidFuzz + LMR | 69.39% |
| **Phase 3: Quantity Extraction** | Context-Aware Regex | 81.63% |
| **OVERALL SYSTEM PERFORMANCE** | **Weighted Average** | **64.63%** |

---
## 5. How to Run This
1.  **Install Requirements:**
    ```bash
    pip install pandas rapidfuzz huggingface_hub scikit-learn
    ```
2.  **Setup Credentials:**
    Add your HuggingFace Token to the `HF_TOKEN` variable in `ai_model.py`.
3.  **Prepare Files:**
    Ensure `test_need_loc.csv` (input) and `available_resources.csv` (inventory) are in the same folder.
4.  **Execute:**
    ```bash
    python ai_model.py
    ```
5.  **Check Output:**
    Open `final_matched_report.csv` to see the prioritized dispatch list.

---
## 6. Why this was made
During urban disasters like the Chennai floods, the biggest bottleneck isn't the lack of resources; it's the **lack of organized information.** Rescuers often waste time going to low-priority areas because they don't have a bird's-eye view of where the most critical needs are. 

This tool was made to ensure that **the right resource reaches the right person in the shortest time possible** by removing human error and fatigue from the initial triage process.

---
## 7. File Directory & Execution Logic

* **`model/ai_model.py`**: The central processing engine. It executes the 4-phase intelligence pipeline (NLP + GIS + NER + Triage) and generates the primary `final_report.csv`.
* **`model/test_need_loc.csv`**: The raw data input containing unstructured emergency text, reported landmarks, and ground-truth labels for performance validation.
* **`model/available_resources.csv`**: The live resource inventory. A database of regional relief centers, hospitals, and stations indexed by their specific resource capabilities.
* **`model/final_matched_report.csv`**: The optimized output. This file pairs every victim with the specific nearest resource center based on predicted needs and geospatial proximity.
* **`chennai_dispatch_map.html`**: The interactive command dashboard. Utilizes Leaflet.js to provide real-time filtering of emergency clusters.

---
## 8. Technical Architecture & Component Breakdown

### I. Semantic Intent Classification (NLI)

Rather than relying on fragile keyword matching, the system utilizes a **Natural Language Inference (NLI)** approach via the `DeBERTa-v3-large` model. This allows for **Zero-Shot Classification**, where the AI compares the emergency text against a "hypothesis template" (e.g., *"This message indicates a need for [Label]"*). This ensures that a request like *"We haven't eaten in days"* is correctly mapped to **Food** even if the specific word is absent.

### II. Spatial Error Correction & Recovery
Raw emergency messages are frequently riddled with typos or localized slang. The system employs **Fuzzy String Matching** using the Levenshtein Distance algorithm. By calculating the "edit distance" between a messily typed location and a validated landmark database, the engine "snaps" the text to the nearest logical coordinate, significantly reducing geocoding failures.

### III. Weighted Triage Heuristics
To optimize resource allocation, the engine calculates a multi-factor **Urgency Score**. This is not a simple linear count; it is a weighted heuristic that balances the **Scale of Crisis** (Quantity) against the **Severity of Need**:
$$Urgency Score = (Quantity \times 0.6) + (Need Severity \times 0.4)$$
This mathematical prioritization ensures that high-impact rescue operations (e.g., a sinking building with 50 occupants) are mathematically pushed to the top of the dispatch queue over lower-severity requests.

### IV. Geospatial Resource Optimization

The system solves the "Nearest Resource Problem" using the **Haversine Formula**. Since Euclidean (flat-map) geometry fails over large geographic areas, this formula calculates the great-circle distance between two points on a sphere using their latitudes and longitudes. For every victim, the code iterates through the `available_resources.csv` to find the center that provides the specific needed resource at the minimum calculated distance.

### V. Dynamic Layer Manipulation
The interactive map utilizes a custom **JavaScript Injection** into the Folium/Leaflet wrapper. By assigning unique internal IDs to the "Red," "Yellow," and "Green" data layers, the front-end buttons can trigger instant `removeLayer` and `addLayer` commands within the browser's DOM. This allows for instantaneous tactical filtering without requiring a server-side refresh.

---
## Frontend Prototype Link
https://drive.google.com/file/d/10dYefngj8Gq0aMvHy3Qt4Y3tn-6azF4e/view?usp=drivesdk

---
*Developed for the **AI for Social Good** domain for **KRUU Grasp Hackathon 2026** by team **TechNova - A Jenita Roselin, Shameera Balkees & Yuvasri Eswara**.*
