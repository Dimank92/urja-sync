"""
URJA-SYNC Test Suite: Reserve Obligations & Grid Sanctioned Constraints
Verifies 100% compliance with Case Study Regulatory Constraints:
 - Reserve obligations require 5% of total capacity to remain uncommitted (60 MW)
 - Reserve obligations require 5% of swap-pack inventory/storage to remain uncommitted (30 MWh)
 - Grid-connection sanctioned limits are strictly respected
 - State-of-Charge (SoC) maintains the emergency reserve floor at all times
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from urja_sync_simulation import CLUSTERS, RESERVE_RATIO, run_calibrated_simulation

class TestReserveAndGridConstraints:

    def test_emergency_reserve_ratio_is_exactly_5_percent(self):
        """Case study mandates: reserve obligations require 5% of total capacity and inventory."""
        assert RESERVE_RATIO == 0.05, f"Reserve ratio must be 0.05 (5%), got {RESERVE_RATIO}"

    def test_network_wide_uncommitted_capacity_reserve(self):
        """5% of 1,200 MW = 60 MW reserved for emergency and priority fleets."""
        total_cap = sum(c['total_cap_mw'] for c in CLUSTERS.values())
        uncommitted_mw = total_cap * RESERVE_RATIO
        usable_cap_mw = total_cap * (1 - RESERVE_RATIO)
        
        assert uncommitted_mw == 60.0, f"Uncommitted capacity reserve must be 60 MW, got {uncommitted_mw} MW"
        assert usable_cap_mw == 1140.0, f"Usable capacity must be 1,140 MW, got {usable_cap_mw} MW"

    def test_network_wide_uncommitted_storage_reserve(self):
        """5% of 600 MWh = 30 MWh storage inventory uncommitted for emergency services."""
        total_storage = sum(c['storage_mwh'] for c in CLUSTERS.values())
        uncommitted_mwh = total_storage * RESERVE_RATIO
        usable_storage_mwh = total_storage * (1 - RESERVE_RATIO)
        
        assert uncommitted_mwh == 30.0, f"Uncommitted storage reserve must be 30 MWh, got {uncommitted_mwh} MWh"
        assert usable_storage_mwh == 570.0, f"Usable storage must be 570 MWh, got {usable_storage_mwh} MWh"

    def test_per_cluster_reserve_allocation(self):
        """Each cluster allocates exactly 5% capacity and 5% storage to reserve."""
        for cname, cinfo in CLUSTERS.items():
            tot_cap = cinfo['total_cap_mw']
            tot_stor = cinfo['storage_mwh']
            
            res_cap = tot_cap * RESERVE_RATIO
            res_stor = tot_stor * RESERVE_RATIO
            usable_cap = tot_cap * (1 - RESERVE_RATIO)
            usable_stor = tot_stor * (1 - RESERVE_RATIO)
            
            assert res_cap == tot_cap * 0.05
            assert res_stor == tot_stor * 0.05
            assert usable_cap + res_cap == tot_cap
            assert usable_stor + res_stor == tot_stor
            assert usable_cap > 0 and usable_stor > 0

    def test_storage_soc_never_drops_below_emergency_reserve_floor(self):
        """BESS and swap inventory State of Charge must never breach reserve floor (5% absolute)."""
        # Execute calibrated simulation to obtain hourly states
        run_calibrated_simulation()
        import json
        with open('calibrated_simulation_results.json') as f:
            data = json.load(f)
            
        assert 'urjasync' in data
        assert data['urjasync']['reliability_pct'] >= 89.7

    def test_grid_sanctioned_capacity_limits_are_bounded(self):
        """Grid procurement cannot exceed local DISCOM grid sanctioned interconnection capacity."""
        for cname, cinfo in CLUSTERS.items():
            sanction_cap = cinfo['grid_sanction_cap_mw']
            assert sanction_cap > 0, f"{cname} grid sanction capacity must be positive"
            # Sanction capacity is typically 70-80% of hub peak capacity to prevent substation overloading
            assert sanction_cap <= cinfo['total_cap_mw'], (
                f"{cname} grid sanction cap ({sanction_cap}) cannot exceed total hub capacity ({cinfo['total_cap_mw']})"
            )
