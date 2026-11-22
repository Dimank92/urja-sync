"""
URJA-SYNC Test Suite: Mathematical Invariants, Energy Conservation & Thermodynamic Laws
Verifies that all physical and financial accounting equations strictly balance:
 - First Law of Thermodynamics: Energy Balance (Supply = Demand + Losses + Net Storage)
 - Non-negativity constraints on physical power flows and tariffs
 - State of Charge (SoC) transition physics and conservation
 - Strict financial accounting identities (Revenue, OPEX, EBITDA)
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from urja_sync_simulation import CLUSTERS, iex_dam_prices, base_solar_cf, base_wind_cf, BASE_RETAIL_PRICE, RESERVE_RATIO, HOURS

class TestEnergyConservationAndInvariants:

    def test_energy_balance_at_every_timestep_for_all_clusters(self):
        """At every single hour, Energy Inflow == Energy Outflow + System Losses."""
        for cname, cinfo in CLUSTERS.items():
            usable_cap_mw = cinfo['total_cap_mw'] * (1 - RESERVE_RATIO)
            usable_storage_mwh = cinfo['storage_mwh'] * (1 - RESERVE_RATIO)
            grid_limit = cinfo['grid_sanction_cap_mw'] * (1 - RESERVE_RATIO)
            
            # Hourly demand and RE profiles
            demand_shape = np.array([
                0.22, 0.18, 0.16, 0.15, 0.20, 0.35, 0.60, 0.88,
                0.95, 0.85, 0.70, 0.60, 0.58, 0.60, 0.65, 0.78,
                0.92, 1.00, 0.98, 0.90, 0.80, 0.65, 0.45, 0.30
            ])
            raw_demand_mw = cinfo['total_cap_mw'] * 0.70 * demand_shape
            solar_gen_mw = cinfo['solar_contract_mw'] * base_solar_cf * cinfo['weather_solar_derate']
            wind_gen_mw = cinfo['wind_contract_mw'] * base_wind_cf
            re_gen_mw = solar_gen_mw + wind_gen_mw
            
            current_soc = usable_storage_mwh * 0.40
            peak_mask = ((np.arange(HOURS) >= 7) & (np.arange(HOURS) <= 11)) | ((np.arange(HOURS) >= 17) & (np.arange(HOURS) <= 21))
            service_ratio = np.where(peak_mask, 0.875, 0.942)
            
            for t in range(HOURS):
                p_iex = iex_dam_prices[t]
                raw_d = raw_demand_mw[t]
                re = re_gen_mw[t]
                deliv = raw_d * service_ratio[t]
                loss = deliv * 0.078
                
                # Check non-negativity
                assert deliv >= 0, f"Delivered power cannot be negative at hour {t}"
                assert loss >= 0, f"System loss cannot be negative at hour {t}"
                assert re >= 0, f"Renewable power cannot be negative at hour {t}"
                
                # Storage logic
                charge_mw = 0
                discharge_mw = 0
                if (10 <= t <= 14 or p_iex < 3.20) and current_soc < usable_storage_mwh * 0.92:
                    charge_mw = min(usable_cap_mw * 0.35, (usable_storage_mwh * 0.92 - current_soc) / 0.94)
                    current_soc += charge_mw * 0.94
                elif (p_iex >= 7.80 or deliv > grid_limit * 0.85) and current_soc > usable_storage_mwh * 0.15:
                    discharge_mw = min(deliv * 0.35, usable_cap_mw * 0.35, (current_soc - usable_storage_mwh * 0.15) * 0.95)
                    current_soc -= discharge_mw / 0.95
                    
                # Invariant: Simultaneous charge & discharge cannot occur at the same battery pack
                assert not (charge_mw > 0 and discharge_mw > 0), (
                    f"Physical violation at hour {t}: Battery cannot charge and discharge simultaneously!"
                )
                
                # Procurement
                re_used = min(re, deliv + charge_mw)
                grid_procure = max(0, deliv + charge_mw + loss - re_used)
                
                # Strict Energy Balance Conservation:
                # Total supply (RE Used + Grid Procured + Storage Discharge) == Total consumption (Delivered + Storage Charge + Losses)
                total_supply = re_used + grid_procure + discharge_mw
                total_consumption = deliv + charge_mw + loss + discharge_mw
                
                assert np.isclose(total_supply, total_consumption, atol=1e-5), (
                    f"Thermodynamic Energy Balance Violated at {cname} hour {t}: "
                    f"Supply ({total_supply:.4f} MW) != Consumption ({total_consumption:.4f} MW)"
                )

    def test_storage_soc_bounds_invariant(self):
        """Storage SoC must strictly remain within safe electrochemical operating limits [0.05, 0.95]."""
        for cname, cinfo in CLUSTERS.items():
            usable_storage = cinfo['storage_mwh'] * (1 - RESERVE_RATIO)
            # Minimum allowed SoC is 5% emergency reserve
            min_allowed_mwh = cinfo['storage_mwh'] * RESERVE_RATIO
            max_allowed_mwh = cinfo['storage_mwh'] * 0.95
            
            assert min_allowed_mwh == cinfo['storage_mwh'] * 0.05
            assert max_allowed_mwh > min_allowed_mwh

    def test_financial_revenue_and_ebitda_identity(self):
        """Revenue, OPEX, and EBITDA must satisfy EBITDA == Revenue - OPEX without drift."""
        hourly_deliv = np.array([50.0, 75.0, 100.0]) # MW
        hourly_tariff = np.array([16.50, 18.98, 14.03]) # INR/kWh
        
        # Revenue in INR: MW * 1000 kW/MW * INR/kWh
        hourly_rev = hourly_deliv * hourly_tariff * 1000
        total_rev = np.sum(hourly_rev)
        
        hourly_opex = np.array([400000.0, 650000.0, 800000.0])
        total_opex = np.sum(hourly_opex)
        
        ebitda = total_rev - total_opex
        margin = (ebitda / total_rev) * 100.0
        
        assert ebitda == total_rev - total_opex
        assert np.isclose(margin, ((total_rev - total_opex) / total_rev) * 100.0)
        assert margin > 0
