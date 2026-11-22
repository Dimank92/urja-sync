"""
URJA-SYNC Test Suite: Core Case Study KPI Targets & Convergence Verification
Validates 100% convergence against all three Technical Mandates:
 - Target 1: Service Reliability from 78.0% to >= 89.7% (~90.0%)
 - Target 2: Storage & Conversion Losses reduced by 20% (10.0% down to <= 8.0%)
 - Target 3: EBITDA Margins strictly sustained > 12.0% across ALL 5 metro clusters
 - Financials denominated in INR (₹) and Crores (Cr)
"""

import pytest
import numpy as np
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from urja_sync_simulation import run_calibrated_simulation, CLUSTERS

@pytest.fixture(scope="module")
def sim_results():
    """Runs the simulation once for the test module and returns calibrated results dict."""
    run_calibrated_simulation()
    res_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'calibrated_simulation_results.json'))
    with open(res_path, 'r') as f:
        data = json.load(f)
    return data

class TestKpiTargetsConvergence:

    def test_target_1_service_reliability_improvement(self, sim_results):
        """Case study Target 1: Increase reliability from 78% to about 90% (89.7%)."""
        base_rel = sim_results['baseline']['reliability_pct']
        urja_rel = sim_results['urjasync']['reliability_pct']
        
        # Verify baseline calibration
        assert 77.0 <= base_rel <= 78.5, f"Baseline reliability should calibrate to ~78%, got {base_rel}%"
        
        # Verify target achievement
        TARGET_RELIABILITY = 89.7
        assert urja_rel >= TARGET_RELIABILITY, (
            f"URJA-SYNC failed Target 1! Expected >= {TARGET_RELIABILITY}%, got {urja_rel}%"
        )
        assert urja_rel > base_rel, "URJA-SYNC reliability must exceed baseline"
        
        # Verify 15% relative improvement
        rel_improvement = (urja_rel - base_rel) / base_rel
        assert rel_improvement >= 0.145, (
            f"Target 1 requires ~15% relative improvement, got {rel_improvement:.2%}"
        )

    def test_target_2_loss_reduction(self, sim_results):
        """Case study Target 2: 20% reduction in energy storage & conversion losses (10.0% down to <= 8.0%)."""
        base_loss = sim_results['baseline']['loss_pct']
        urja_loss = sim_results['urjasync']['loss_pct']
        
        # Verify baseline losses
        assert np.isclose(base_loss, 10.0, atol=0.2), f"Baseline losses must average 10.0%, got {base_loss}%"
        
        # Verify target achievement
        TARGET_LOSS = 8.0
        assert urja_loss <= TARGET_LOSS, (
            f"URJA-SYNC failed Target 2! Expected <= {TARGET_LOSS}%, got {urja_loss}%"
        )
        assert urja_loss < base_loss, "URJA-SYNC losses must be lower than baseline"
        
        # Verify 20% relative reduction
        loss_reduction = (base_loss - urja_loss) / base_loss
        assert loss_reduction >= 0.20, (
            f"Target 2 requires at least 20% relative reduction in losses, got {loss_reduction:.2%}"
        )

    def test_target_3_ebitda_margins_strictly_above_12_percent_all_clusters(self, sim_results):
        """Case study Target 3: Maintain EBITDA margins strictly above 12% across ALL clusters."""
        MANDATORY_HURDLE = 12.0
        
        # Check overall network blended margin
        overall_margin = sim_results['urjasync']['ebitda_margin_pct']
        assert overall_margin > MANDATORY_HURDLE, (
            f"Blended EBITDA margin ({overall_margin}%) must exceed 12% hurdle"
        )
        
        # Check cluster-by-cluster audit (No cluster left behind)
        cluster_margins = sim_results['urjasync']['cluster_margins']
        assert len(cluster_margins) == 5, f"Must have margins for all 5 clusters, got {len(cluster_margins)}"
        
        for cname in CLUSTERS.keys():
            assert cname in cluster_margins, f"Missing margin for cluster {cname}"
            m = cluster_margins[cname]
            assert m > MANDATORY_HURDLE, (
                f"Cluster {cname} failed 12% EBITDA hurdle! Got {m}%, required > {MANDATORY_HURDLE}%"
            )
            # Ensure healthy margin cushion
            assert m >= 35.0, f"Cluster {cname} margin ({m}%) demonstrates robust operational profitability"

    def test_financial_denominations_and_positive_ebitda_uplift(self, sim_results):
        """Financial metrics must be denominated in INR Crores and produce massive positive uplift."""
        base_annual_cr = sim_results['baseline']['annual_ebitda_cr']
        urja_annual_cr = sim_results['urjasync']['annual_ebitda_cr']
        
        assert base_annual_cr > 0, "Baseline EBITDA must be positive"
        assert urja_annual_cr > base_annual_cr, "URJA-SYNC EBITDA must exceed baseline"
        
        uplift_cr = urja_annual_cr - base_annual_cr
        assert uplift_cr > 1000.0, f"Annual EBITDA uplift must exceed ₹1,000 Crores, got ₹{uplift_cr:.1f} Cr"
        assert np.isclose(uplift_cr, 1506.0, atol=2.0), (
            f"Calibrated annual EBITDA uplift should be ~₹1,506 Cr ($179.3M USD), got ₹{uplift_cr:.1f} Cr"
        )

    def test_daily_ebitda_and_revenue_cost_math(self, sim_results):
        """Verifies daily revenue, cost, and EBITDA accounting identity: EBITDA = Rev - Cost."""
        for mode in ['baseline', 'urjasync']:
            data = sim_results[mode]
            rev = data['daily_rev_cr']
            cost = data['daily_cost_cr']
            ebitda = data['daily_ebitda_cr']
            
            calculated_ebitda = round(rev - cost, 2)
            assert np.isclose(ebitda, calculated_ebitda, atol=0.02), (
                f"Accounting mismatch in {mode}: rev ({rev}) - cost ({cost}) != ebitda ({ebitda})"
            )
            
            # Check margin formula: (ebitda / rev) * 100
            expected_margin = round((ebitda / rev) * 100, 1)
            actual_margin = data['ebitda_margin_pct']
            assert np.isclose(actual_margin, expected_margin, atol=0.2), (
                f"Margin formula mismatch in {mode}: got {actual_margin}%, expected {expected_margin}%"
            )
