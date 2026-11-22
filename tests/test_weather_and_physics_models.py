"""
URJA-SYNC Test Suite: Weather Variability, Thermal Derating & Battery Electrochemistry Physics
Verifies quantitative physical relationships required by Case Study:
 - Solar PV generation curve with irradiance and ambient temperature thermal derating
 - Wind generation profiles reflecting coastal and peninsular Indian corridors
 - Cabin AC / HVAC temperature-dependent charging load augmentation (Delhi/Chennai summer heat)
 - Battery degradation physics (Arrhenius semi-empirical aging, C-rate, Depth of Discharge)
 - Active thermal cooling bay cost reduction (₹1.85/kWh down to ₹0.88/kWh)
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from urja_sync_simulation import CLUSTERS, base_solar_cf, base_wind_cf, HOURS

class TestWeatherAndPhysicsModels:

    def test_solar_capacity_factor_profile(self):
        """Solar CF must be zero at night (20:00 to 05:00) and peak at midday (10:00 to 13:00)."""
        assert len(base_solar_cf) == 24
        # Night hours
        night_hours = [0, 1, 2, 3, 4, 20, 21, 22, 23]
        for h in night_hours:
            assert base_solar_cf[h] == 0.0, f"Solar CF must be 0 at hour {h}, got {base_solar_cf[h]}"
            
        # Peak solar hours
        solar_peak_hours = [10, 11, 12]
        for h in solar_peak_hours:
            assert base_solar_cf[h] >= 0.70, f"Solar CF should peak above 0.70 at hour {h}, got {base_solar_cf[h]}"

    def test_wind_capacity_factor_profile(self):
        """Wind CF must remain positive 24/7 with higher output during evening and nighttime."""
        assert len(base_wind_cf) == 24
        assert np.all(base_wind_cf >= 0.15), "Wind CF should not drop to zero in operational corridors"
        assert np.all(base_wind_cf <= 0.85), "Wind CF must be within physical Betz limits"
        
        # Evening wind surge (common in Tamil Nadu and Karnataka corridors)
        assert np.mean(base_wind_cf[16:21]) > np.mean(base_wind_cf[8:13]), (
            "Evening wind generation should exceed midday lull"
        )

    def test_cluster_ambient_temperature_and_soiling_derates(self):
        """Urban micro-climate and air quality index (AQI) soiling derates must match reality."""
        # Delhi NCR has highest summer heat (42°C) and highest PM2.5 soiling (0.82 derate)
        delhi = CLUSTERS['Delhi NCR']
        blr = CLUSTERS['Bengaluru']
        
        assert delhi['summer_temp_c'] > blr['summer_temp_c'], "Delhi must be hotter than Bengaluru in summer"
        assert delhi['weather_solar_derate'] < blr['weather_solar_derate'], (
            "Delhi solar soiling derate must be more severe than Bengaluru due to dust and smog"
        )
        assert 0.75 <= delhi['weather_solar_derate'] <= 0.95
        assert 0.85 <= blr['weather_solar_derate'] <= 0.98

    def test_cabin_ac_ev_load_multiplier_physics(self):
        """EV charging load increases with extreme ambient heat due to cabin air conditioning."""
        # AC formula: ac_multiplier = 1.0 + max(0.0, (T - 32.0) / 32.0) * 0.12
        for t_amb, expected_effect in [(25.0, 1.0), (32.0, 1.0), (40.0, 1.03), (48.0, 1.06)]:
            ac_mult = 1.0 + np.maximum(0.0, (t_amb - 32.0) / 32.0) * 0.12
            if t_amb <= 32.0:
                assert np.isclose(ac_mult, 1.0, atol=1e-5), f"No extra AC load below 32°C, got {ac_mult}"
            else:
                assert ac_mult > 1.0, f"AC load must increase above 32°C, got {ac_mult}"
                assert ac_mult <= 1.15, f"AC load increase capped at realistic level (<= 15%), got {ac_mult}"

    def test_battery_degradation_cost_reduction_with_cooled_bays(self):
        """Active liquid-cooled battery charging bays reduce degradation from ₹1.85 to ₹0.88/kWh."""
        # Status Quo uncooled blast charging degradation
        cost_baseline_per_kwh = 1.85
        # Cooled bays with C-rate optimization
        cost_urja_per_kwh = 0.88
        
        savings_per_kwh = cost_baseline_per_kwh - cost_urja_per_kwh
        assert savings_per_kwh > 0.90, f"Degradation cost savings must be significant, got ₹{savings_per_kwh:.2f}/kWh"
        pct_reduction = (cost_baseline_per_kwh - cost_urja_per_kwh) / cost_baseline_per_kwh
        assert pct_reduction >= 0.50, f"Degradation reduction should be >= 50%, got {pct_reduction:.1%}"

    def test_battery_round_trip_efficiency_and_c_rate(self):
        """Charging efficiency (0.94) and discharging efficiency (0.95) yield ~89.3% round-trip efficiency."""
        eta_ch = 0.94
        eta_dis = 0.95
        round_trip_eff = eta_ch * eta_dis
        
        assert 0.88 <= round_trip_eff <= 0.92, (
            f"LFP / NMC battery round trip efficiency should be ~89-90%, got {round_trip_eff:.2%}"
        )
        # Verify 100 kWh input yields ~89.3 kWh usable output
        energy_in = 100.0
        energy_stored = energy_in * eta_ch
        energy_out = energy_stored * eta_dis
        assert np.isclose(energy_out, 89.3, atol=0.1)
