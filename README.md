# Disaster Response AI: 4-Phase Integrated Pipeline

This system automates the triage of emergency messages during disasters (specifically modeled for Chennai disaster scenarios). It transforms messy text data into a prioritized, color-coded dispatch report.

---

## The 4-Phase Logic

### Phase 1: Need Classification (NLP)
- **Engine:** Zero-Shot Classification (`DeBERTa-v3-large`).
- **Goal:** Identifying **WHAT** is needed.

### Phase 2: Spatial Recovery (GIS)
- **Engine:** Fuzzy String Matching (`RapidFuzz`) + Landmark Database.
- **Goal:** Identifying **WHERE** the crisis is.

### Phase 3: Quantity Extraction (NER)
- **Engine:** Context-Aware Regex.
- **Goal:** Identifying **HOW MANY** lives are at stake.

### Phase 4: Urgency Scoring (Heuristics)
- **Engine:** Weighted Scoring Model ($60\% \text{ Quantity} + 40\% \text{ Need severity}$).
- **Triage Labels:**
    - 🔴 **Red (High):** Score 30+
    - 🟡 **Yellow (Medium):** Score 15-29
    - 🟢 **Green (Low):** Score <15

---

## Performance Metrics
| Metric | Accuracy |
| :--- | :--- |
| **Phase 1 (Need)** | 42.86% |
| **Phase 2 (Location)** | 69.39% |
| **Phase 3 (Quantity)** | 81.63% |
| **TOTAL SYSTEM SCORE** | **64.63%** |

---

## Deployment
The script outputs `final_report.csv`, which is pre-sorted by urgency.

---
*Developed for **crisis need to resource matching engine** under the **AI for Social Good Domain** for **KRUU Grasp Hackathon 2026**.*