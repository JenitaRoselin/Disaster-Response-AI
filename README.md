# Disaster Response AI: End-to-End Triage & Resource Dispatch

## 1. About the Project
This project is an **AI-driven Emergency Dispatch Engine** designed to handle the chaos of unstructured communication during disasters. It takes messy, informal text messages (like those sent during floods) and uses Natural Language Processing (NLP) and Geospatial Intelligence to automatically categorize, prioritize, and match victims with the nearest available rescue resources.

## 2. Who it was built for
This was developed for **Emergency Management Agencies and First Responders** (specifically modeled for the **Chennai Metro** region). The goal is to reduce the "Data-to-Action" lag time that occurs when human dispatchers are overwhelmed by thousands of requests.

## 3. Features Included in Demo
* **Zero-Shot NLP:** Classifies needs (Food, Medical, Rescue) without requiring specific training data.
* **Fuzzy Spatial Recovery:** Corrects misspelled locations and maps them to precise GPS coordinates.
* **Automated Triage:** A weighted heuristic engine that color-codes cases by urgency (**Red/Yellow/Green**).
* **Smart Resource Matching:** Uses the **Haversine Formula** to cross-reference victim location against a live inventory (`available_resources.csv`) to assign the nearest capable center.
* **Autonomous Reporting:** Generates a final, ready-to-use dispatch sheet (`final_matched_report.csv`) with zero manual input required.



## 4. Accuracy Scores
The system self-evaluates by comparing AI predictions against historical ground-truth data:

| Phase | Engine | Accuracy |
| :--- | :--- | :--- |
| **Phase 1: Need Classification** | DeBERTa-v3-large | 42.86% |
| **Phase 2: Location Recovery** | RapidFuzz + LMR | 69.39% |
| **Phase 3: Quantity Extraction** | Context-Aware Regex | 81.63% |
| **OVERALL SYSTEM PERFORMANCE** | **Weighted Average** | **64.63%** |

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

## 6. Why this was made
During urban disasters like the Chennai floods, the biggest bottleneck isn't the lack of resources; it's the **lack of organized information.** Rescuers often waste time going to low-priority areas because they don't have a bird's-eye view of where the most critical needs are. 

This tool was made to ensure that **the right resource reaches the right person in the shortest time possible** by removing human error and fatigue from the initial triage process.

---
*Developed for the **AI for Social Good** domain for **KRUU Grasp Hackathon 2026** by team **TechNova - A Jenita Roselin, Shameera Balkees, Yuvasri Eswara**.*
