# URJA-SYNC: Submission Package File Inventory

### Package Archive
- **URJA_SYNC_HACKATHON_PACKAGE.zip** (2.3 MB)
  Complete offline submission bundle containing all source code, trained neural network weights, reports, interactive dashboard, and 300-DPI charts.

---

### Core Submission Files and Explanations

1. **run_all_ml.py**
   - **Role:** Unified master AI/ML execution runner.
   - **Description:** Single quick-launch command (`python run_all_ml.py`) that runs both the empirical deep learning training pipeline and the domain physics neural architecture suite.

2. **ai_ml_pipeline.py**
   - **Role:** Empirical AI/ML training and inference pipeline.
   - **Description:** Implements a PyTorch Gated Bidirectional LSTM neural network for multi-quantile demand forecasting (P10, P50, P90) alongside a Scikit-Learn Gradient Boosting benchmark (R^2 = 0.9962, MAE = 5.02 MW).

3. **urja_sync_ai_models.py**
   - **Role:** Domain-informed neural architecture engine.
   - **Description:** Implements SpatioTemporalDemandGNN for inter-metro fleet migration, IEXPriceForecaster with CERC regulatory price cap detection, BatteryPINNDegradation with Arrhenius electro-thermal physics loss, and ContextualPricingBandit for dynamic tariffs within +-20% corridors.

4. **urja_sync_tft_model.pt**
   - **Role:** Serialized PyTorch model weights.
   - **Description:** Pre-trained network checkpoint ready for instant 12-millisecond real-time market inference without retraining.

5. **urja_sync_simulation.py**
   - **Role:** 24-hour physical and financial dispatch engine.
   - **Description:** Simulates the 1,200 MW EV network and 600 MWh BESS across 5 metro clusters under IEX DAM/RTM pricing, battery degradation constraints, and DISCOM quotas.

6. **urja_sync_stress_scenarios.py**
   - **Role:** Black-swan resilience stress testing.
   - **Description:** Validates network stability across 5 extreme conditions: 47°C Northern heatwave, monsoon wind lulls, IEX price cap spikes, DISCOM load shedding, and compound shocks.

7. **URJA_SYNC_COMPREHENSIVE_REPORT.pdf**
   - **Role:** Official 7-page technical report and executive briefing.
   - **Description:** Formatted with ReportLab to institutional standards. Contains complete mathematical formulations, dispatch tables, EBITDA breakdown, 4 high-resolution exhibits, and live repository links in the footer with zero competitor/team identifiers.

8. **URJA_SYNC_INTERACTIVE_DASHBOARD.html**
   - **Role:** Interactive browser-based operations simulator.
   - **Description:** Standalone web application with Chart.js visualization and dynamic sliders to inspect cluster dispatch, battery State of Charge, and EBITDA margins in real time.

9. **URJA_SYNC_EXECUTIVE_PITCH_DECK.md**
   - **Role:** 10-slide competitive pitch deck.
   - **Description:** Slide-by-slide script covering problem statement, AI architecture, financial metrics, and pilot implementation roadmap.

10. **ENGLISH_DEFENSE_SCRIPTS.md**
    - **Role:** Jury Q&A defense script.
    - **Description:** Time-coded English responses explaining data sources, terminal output metrics, both ML engines, and architectural trade-offs.

11. **README.md**
    - **Role:** GitHub repository homepage and user guide.
    - **Description:** Complete open-source documentation with architecture diagrams, quick-start setup commands, benchmark tables, and mathematical formulas.

12. **requirements.txt & .gitignore**
    - **Role:** Environment configuration and build rules.
    - **Description:** Lists pinned Python dependencies (torch, numpy, pandas, scikit-learn, matplotlib, reportlab) and repository exclusion rules.

---

### High-Resolution Exhibits (300 DPI)

- **exhibit1_hourly_dispatch.png:** 24-hour network-wide energy dispatch stacked by source (Solar, Wind, DISCOM, BESS, IEX).
- **exhibit2_cluster_kpis.png:** Five-metro performance comparison across reliability, losses, and EBITDA margin.
- **exhibit3_waterfall.png:** Financial waterfall chart showing annual EBITDA improvement of +INR 1,506 Crores.
- **exhibit4_soc_profiles.png:** 24-hour battery State-of-Charge trajectories maintaining 20% to 90% health limits.
- **model_training_metrics.png:** PyTorch training convergence, multi-quantile forecast ribbons, and top feature importance weights.
