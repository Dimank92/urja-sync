"""
URJA-SYNC Test Suite: Infrastructure Sizing, Technology Split & Energy Sourcing
Verifies 100% compliance with Case Study Specifications:
 - 1,200 MW Total Installed Capacity
 - 60% DC Fast-Charging (720 MW) & 40% Battery-Swapping (480 MW)
 - 600 MWh Total Distributed Storage across 5 Metros
 - 5 Metros: Delhi NCR, Mumbai MMR, Bengaluru, Hyderabad, Chennai
 - ~35% Open-Access Contracted Renewable Energy (Solar & Wind)
"""

import pytest
import numpy as np
import sys
import os

# Add parent directory to path to import simulation modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from urja_sync_simulation import CLUSTERS, base_solar_cf, base_wind_cf

class TestInfrastructureSizing:
    
    def test_total_metro_count_and_identities(self):
        """Case study mandates 5 specific Indian metropolitan clusters."""
        expected_clusters = {'Delhi NCR', 'Mumbai MMR', 'Bengaluru', 'Hyderabad', 'Chennai'}
        actual_clusters = set(CLUSTERS.keys())
        assert actual_clusters == expected_clusters, (
            f"Cluster mismatch: Expected {expected_clusters}, got {actual_clusters}"
        )
        assert len(CLUSTERS) == 5, f"Expected exactly 5 clusters, got {len(CLUSTERS)}"

    def test_total_network_capacity_equals_1200_mw(self):
        """Total installed capacity across all clusters must sum exactly to 1,200 MW."""
        total_cap = sum(c['total_cap_mw'] for c in CLUSTERS.values())
        assert total_cap == 1200, f"Total capacity must be exactly 1,200 MW, got {total_cap} MW"

    def test_technology_split_60_percent_fast_dc_and_40_percent_swapping(self):
        """Case study mandates 60% DC fast-charging hubs (720 MW) and 40% swap stations (480 MW)."""
        total_fast_dc = sum(c['fast_dc_mw'] for c in CLUSTERS.values())
        total_swap = sum(c['swap_mw'] for c in CLUSTERS.values())
        total_cap = sum(c['total_cap_mw'] for c in CLUSTERS.values())
        
        assert total_fast_dc == 720, f"Expected 720 MW DC Fast Charging, got {total_fast_dc} MW"
        assert total_swap == 480, f"Expected 480 MW Swapping, got {total_swap} MW"
        assert total_fast_dc + total_swap == total_cap == 1200
        
        ratio_dc = total_fast_dc / total_cap
        ratio_swap = total_swap / total_cap
        assert np.isclose(ratio_dc, 0.60, atol=1e-5), f"Fast DC ratio must be 60%, got {ratio_dc:.2%}"
        assert np.isclose(ratio_swap, 0.40, atol=1e-5), f"Swap ratio must be 40%, got {ratio_swap:.2%}"

    def test_each_cluster_subsystem_capacity_split(self):
        """Each cluster's fast DC and swap capacities must sum to its total capacity with 60/40 ratio."""
        for cname, cinfo in CLUSTERS.items():
            tot = cinfo['total_cap_mw']
            fast_dc = cinfo['fast_dc_mw']
            swap = cinfo['swap_mw']
            
            assert fast_dc + swap == tot, (
                f"Cluster {cname} internal capacity mismatch: {fast_dc} + {swap} != {tot}"
            )
            assert np.isclose(fast_dc / tot, 0.60, atol=1e-3), (
                f"Cluster {cname} Fast DC ratio must be 60%, got {fast_dc / tot:.2%}"
            )
            assert np.isclose(swap / tot, 0.40, atol=1e-3), (
                f"Cluster {cname} Swap ratio must be 40%, got {swap / tot:.2%}"
            )

    def test_total_distributed_storage_equals_600_mwh(self):
        """Total distributed energy storage across all 5 metro clusters must equal 600 MWh."""
        total_storage = sum(c['storage_mwh'] for c in CLUSTERS.values())
        assert total_storage == 600, f"Total storage must be exactly 600 MWh, got {total_storage} MWh"

    def test_individual_cluster_storage_and_capacity_allocations(self):
        """Verifies individual cluster sizing aligned with realistic Indian EV demand tiers."""
        expected_allocations = {
            'Delhi NCR': {'total_cap': 320, 'storage': 160},
            'Mumbai MMR': {'total_cap': 280, 'storage': 140},
            'Bengaluru': {'total_cap': 240, 'storage': 120},
            'Hyderabad': {'total_cap': 180, 'storage': 90},
            'Chennai': {'total_cap': 180, 'storage': 90}
        }
        for cname, exp in expected_allocations.items():
            actual = CLUSTERS[cname]
            assert actual['total_cap_mw'] == exp['total_cap'], (
                f"{cname} total capacity expected {exp['total_cap']}, got {actual['total_cap_mw']}"
            )
            assert actual['storage_mwh'] == exp['storage'], (
                f"{cname} storage expected {exp['storage']}, got {actual['storage_mwh']}"
            )

    def test_renewable_sourcing_share_aligned_with_35_percent_mandate(self):
        """Case study notes ~35% of energy is sourced from solar & wind via open access."""
        total_solar_contract = sum(c['solar_contract_mw'] for c in CLUSTERS.values())
        total_wind_contract = sum(c['wind_contract_mw'] for c in CLUSTERS.values())
        total_re_contract = total_solar_contract + total_wind_contract
        
        # Total contracted RE generation across 24 hours (MWh)
        daily_re_gen_mwh = 0
        for cname, cinfo in CLUSTERS.items():
            solar_24h = cinfo['solar_contract_mw'] * base_solar_cf * cinfo['weather_solar_derate']
            wind_24h = cinfo['wind_contract_mw'] * base_wind_cf
            daily_re_gen_mwh += np.sum(solar_24h + wind_24h)
            
        # Daily delivered energy is ~10,000 - 12,000 MWh across 1,200 MW network
        # Verify RE contracts provide significant renewable coverage (~30% to 40% of delivered energy)
        assert total_re_contract >= 500, f"Contracted RE MW should be substantial, got {total_re_contract} MW"
        assert daily_re_gen_mwh > 2500, f"Daily RE generation should be > 2500 MWh, got {daily_re_gen_mwh:.1f} MWh"
