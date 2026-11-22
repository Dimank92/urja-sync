# URJA-SYNC: AI-Powered Regional Energy Allocation & Storage Optimization Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch 2.0+](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg)](https://scikit-learn.org/)
[![CERC Compliant](https://img.shields.io/badge/Market-CERC%20%2F%20IEX%20Aligned-0D9488.svg)](https://cercind.gov.in)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Real-time energy allocation, battery storage dispatch, and dynamic pricing framework for 1,200 MW installed capacity (60% DC Fast Charging, 40% Battery Swapping) backed by 600 MWh battery storage across 5 Indian metros: Delhi NCR, Mumbai MMR, Bengaluru, Hyderabad, and Chennai.

---

## 1. Executive Performance Benchmark

| Case Study Target | Baseline (Current) | Target Mandate | URJA-SYNC AI Engine | Verification Status |
| :--- | :---: | :---: | :---: | :---: |
| **Service Reliability** | **77.9%** | **>= 89.7% (~90%)** | **90.4%** | **PASSED (+0.7% headroom)** |
| **Storage & Conversion Losses** | **10.0%** | **<= 8.0%** | **7.8%** | **PASSED (22.0% relative cut)** |
| **Blended EBITDA Margin** | **26.6%** | **> 12.0%** | **44.2%** | **PASSED (+32.2% margin)** |
| **Annual Network EBITDA** | INR 1,530.4 Cr | - | **INR 3,036.4 Cr** | **+INR 1,506.0 Cr ($179.3M USD)** |

All 5 individual metro clusters exceed the 12.0% EBITDA hurdle:
- Delhi NCR (320 MW / 160 MWh): **42.2%** (Baseline: 24.8%)
- Mumbai MMR (280 MW / 140 MWh): **40.1%** (Baseline: 21.1%)
- Bengaluru (240 MW / 120 MWh): **48.2%** (Baseline: 31.0%)
- Hyderabad (180 MW / 90 MWh): **46.6%** (Baseline: 29.6%)
- Chennai (180 MW / 90 MWh): **46.9%** (Baseline: 29.5%)

---

## 2. Machine Learning Architecture & Benchmark Results

URJA-SYNC deploys a 3-tier AI system:
1. **Tier 1 (Multi-Horizon Probabilistic Forecaster)**: PyTorch Gated Bidirectional LSTM with Multi-Quantile Head predicting P10, P50, and P90 demand curves.
2. **Tier 2 (Stochastic MPC Dispatcher)**: Rolling 24h Mixed-Integer Linear Program (MILP) coordinating IEX Day-Ahead (DAM) and Real-Time (RTM) market bids with a hard 5% emergency reserve constraint (60 MW / 30 MWh).
3. **Tier 3 (Dynamic Pricing & Degradation Engine)**: Price elasticity model shifting flexible fleet charging into solar hours while controlling cell temperature (<30°C) via active liquid cooling.

### Trained Model Performance (`ai_ml_pipeline.py`)

```
=================================================================
MODEL BENCHMARK PERFORMANCE ON OUT-OF-SAMPLE TEST SET
=================================================================
PyTorch Gated LSTM Forecaster (P50 Median Forecast):
  - Mean Absolute Error (MAE):           5.02 MW
  - Root Mean Squared Error (RMSE):      6.50 MW
  - Coefficient of Determination (R^2):  0.9962  (High Accuracy)
  - Pinball Quantile Loss:               1.8638

Scikit-Learn Gradient Boosting Benchmark:
  - Mean Absolute Error (MAE):           4.22 MW
  - R^2 Score:                           0.9974
=================================================================
```

---

## 3. Project File Structure

```
├── ai_ml_pipeline.py                 # PyTorch & Scikit-Learn training and evaluation pipeline
├── urja_sync_simulation.py           # 24-hour national energy dispatch simulation (5 metros)
├── urja_sync_stress_scenarios.py     # Multi-scenario stress tests (Heatwave, Monsoon, Price spikes)
├── generate_pdf_report.py            # ReportLab script generating the official 7-page PDF report
├── verify_all_numbers.py             # Automated consistency testing across all files
│
├── URJA_SYNC_COMPREHENSIVE_REPORT.pdf# Official 7-page PDF report for jury submission
├── URJA_SYNC_EXECUTIVE_PITCH_DECK.md # 10-slide ready-to-present pitch deck with speaker notes
├── URJA_SYNC_INTERACTIVE_DASHBOARD.html # Standalone interactive browser dashboard with Chart.js
├── AUDIT_AND_TRAPS_ANALYSIS.md       # Forensic analysis of 10 case study traps and jury defense
├── EXECUTIVE_1_PAGER_HANDOUT.md      # 1-page executive summary for jury review
│
├── urja_sync_tft_model.pt            # Serialized PyTorch model weights
├── ml_evaluation_metrics.json        # Out-of-sample ML validation metrics
├── calibrated_simulation_results.json# Detailed cluster simulation records
├── stress_test_results.json          # Multi-scenario stress test results
│
├── exhibit1_kpi_scorecard.png        # Exhibit 1: Target vs Actual KPI Scorecard
├── exhibit2_cluster_margins.png      # Exhibit 2: Cluster-Wise EBITDA Margin Audit
├── exhibit3_24h_dispatch_delhi.png   # Exhibit 3: Delhi NCR 24h Dispatch & Dynamic Pricing
├── exhibit4_scenario_stress_testing.png # Exhibit 4: Black Swan Resilience Matrix
└── model_training_metrics.png        # ML Forecast Intervals and Feature Importance
```

---

## 4. Quickstart: Installation & Execution

### Prerequisites
Install Python 3.10+ and required dependencies:
```bash
pip install -r requirements.txt
```

### 1. Run Unified Dual AI/ML Suite (Recommended)
Executes both empirical deep learning training and domain physics architecture validation:
```bash
python run_all_ml.py
```

### 2. Run Individual ML Engines
- **Empirical Training Pipeline (BiLSTM-GLU & Quantile Regression):**
  ```bash
  python ai_ml_pipeline.py
  ```
- **Domain-Informed Structural Architecture (GNN, IEX Cap, Battery PINN, Bandit):**
  ```bash
  python urja_sync_ai_models.py
  ```

### 3. Run Physical & Financial Dispatch Simulation
```bash
python urja_sync_simulation.py
```

### 4. Run Black-Swan Stress Scenarios
```bash
python urja_sync_stress_scenarios.py
```

### 2. Run the 24-Hour Network Simulation
```bash
python urja_sync_simulation.py
```
Simulates hourly dispatch across Delhi, Mumbai, Bengaluru, Hyderabad, and Chennai, validating the 90.4% reliability, 7.8% losses, and 44.2% EBITDA margin.

### 3. Run Scenario Stress Tests
```bash
python urja_sync_stress_scenarios.py
```
Tests 5 black swan scenarios (47°C summer heatwave, monsoon wind lull, IEX price cap spike, compound shock).

### 4. Build the Official PDF Report
```bash
python generate_pdf_report.py
```
Compiles `URJA_SYNC_COMPREHENSIVE_REPORT.pdf` with all 4 embedded 300-DPI exhibits and dynamic page numbering.

### 5. Launch the Interactive Dashboard
Open `URJA_SYNC_INTERACTIVE_DASHBOARD.html` in any web browser to adjust ambient temperature, solar cloud cover, and market prices in real time.

---

## 5. Regulatory Alignment

- **CERC Green Energy Open Access Rules 2022**: Utilizes the 100 kW threshold for direct solar and wind contracting.
- **IEX Market Structure**: Integrates 24-hour baseline Day-Ahead Market (DAM) bidding (10:00-12:00 window) with 48 half-hour Real-Time Market (RTM) balancing sessions.
- **CERC Deviation Settlement Mechanism (DSM)**: Stationary BESS provides 20-millisecond ramp-rate buffering to eliminate grid frequency deviation penalties.
- **Battery Degradation Physics**: Models electro-thermal degradation using the Wang et al. (Ford / Journal of Power Sources) Arrhenius formulation with active liquid cooling (<30°C).

---

## 6. License
This project is licensed under the MIT License.
