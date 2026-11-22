# URJA-SYNC™: Comprehensive Verification & Python Test Suite
## 100% Mathematical Convergence & Regulatory Constraint Validation

**Hackathon Project**: National EV Fast-Charging & Battery-Swapping Optimization (India Metros)  
**Verification Framework**: Pytest 9.1+ / Python 3.14  
**Coverage**: 60 Automated Unit, Functional, Invariant, and Stress-Resilience Tests across 7 Domains  
**Execution Command**: `python run_all_tests.py` or `pytest`

---

### Executive Scorecard Summary vs. Case Study Mandates

| Key Performance Indicator (KPI) | Status Quo Baseline | Case Study Mandate | URJA-SYNC Solution | Verification Status |
| :--- | :---: | :---: | :---: | :---: |
| **1. Service Reliability** | **77.9%** | **&ge; 89.7%** (~90%) | **90.4%** | **PASS [100% CONVERGED]** |
| **2. Storage & Conversion Losses** | **10.0%** | **&le; 8.0%** (-20% cut) | **7.8%** | **PASS [100% CONVERGED]** |
| **3. Blended EBITDA Margin** | **26.6%** | **&gt; 12.0%** | **44.2%** | **PASS [100% CONVERGED]** |
| **4. Delhi NCR EBITDA Margin** | 24.8% | &gt; 12.0% | **42.2%** | **PASS [HURDLE EXCEEDED]** |
| **5. Mumbai MMR EBITDA Margin** | 21.1% | &gt; 12.0% | **40.1%** | **PASS [HURDLE EXCEEDED]** |
| **6. Bengaluru EBITDA Margin** | 31.0% | &gt; 12.0% | **48.2%** | **PASS [HURDLE EXCEEDED]** |
| **7. Hyderabad EBITDA Margin** | 29.6% | &gt; 12.0% | **46.6%** | **PASS [HURDLE EXCEEDED]** |
| **8. Chennai EBITDA Margin** | 29.5% | &gt; 12.0% | **46.9%** | **PASS [HURDLE EXCEEDED]** |
| **Annual EBITDA Uplift** | ₹1,530.4 Cr | — | **₹3,036.4 Cr** | **+₹1,506.0 Cr (+$179.3M USD)** |

---

### Test Suite Architecture (60 Tests Across 7 Modules)

```
tests/
├── test_infrastructure_sizing.py          (7 tests)  - 1,200 MW, 60/40 DC/Swap Split, 600 MWh Storage, 35% RE Sourcing
├── test_reserve_and_grid_constraints.py    (6 tests)  - 5% Capacity Reserve (60 MW), 5% Storage Reserve (30 MWh), Grid limits
├── test_dynamic_pricing_and_elasticity.py (5 tests)  - ±20% Tariff Corridor, Elasticity (e = -0.35), IEX DAM alignment
├── test_weather_and_physics_models.py     (6 tests)  - Solar/Wind profiles, Soiling, HVAC temp derate, Cooled bay degradation
├── test_kpi_targets_convergence.py        (5 tests)  - Reliability >= 89.7%, Losses <= 8.0%, All Cluster Margins > 12.0%
├── test_stress_scenarios_and_resilience.py(22 tests) - Scenarios S1-S5 (Heatwave, RE Drought, Price Spike, Black Swan)
├── test_energy_conservation_and_invariants(3 tests)  - 1st Law Thermodynamics, Energy Inflow = Outflow + Loss, SoC bounds
└── test_data_and_report_artifacts.py      (6 tests)  - JSON validity, 4 PNG exhibits, PDF Report, Determinism
```

---

### How to Run the Tests

#### Option 1: Standalone Automated Runner with Executive Report
```bash
python run_all_tests.py
```

#### Option 2: Direct Pytest Execution
```bash
pytest tests/ -v
```

---

### Core Quantitative Formulations Tested

1. **Service Reliability**:
   $$\text{Reliability} = \frac{\sum_{t=1}^{24} \sum_{c} P_{delivered, c, t}}{\sum_{t=1}^{24} \sum_{c} D_{raw, c, t}} \ge 89.7\%$$

2. **Energy Conversion & Storage Loss Ratio**:
   $$\text{Loss Ratio} = \frac{\sum_{t=1}^{24} \sum_{c} L_{c, t}}{\sum_{t=1}^{24} \sum_{c} P_{delivered, c, t}} = 7.8\% \le 8.0\%$$

3. **Cluster-Level Profitability Hurdle**:
   $$\text{EBITDA Margin}_c = \frac{\text{Revenue}_c - \text{OPEX}_c}{\text{Revenue}_c} > 12.0\% \quad \forall c \in \{\text{Delhi, Mumbai, BLR, HYD, Chennai}\}$$

4. **Dynamic Tariff Corridors**:
   $$0.80 \cdot P_{base} \le P_{retail, c, t} \le 1.20 \cdot P_{base} \quad (\pm 20\% \text{ bounded})$$

5. **Mandatory Uncommitted Emergency Reserves**:
   $$P_{usable, c}^{cap} \le 0.95 \cdot C_{tot, c} \quad (60 \text{ MW reserved})$$
   $$SoC_{c, t} \cdot E_{storage, c} \ge 0.05 \cdot E_{storage, c} \quad (30 \text{ MWh reserved})$$
