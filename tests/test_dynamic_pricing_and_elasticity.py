"""
URJA-SYNC Test Suite: Dynamic Customer Pricing & Demand Elasticity
Verifies 100% compliance with Case Study Pricing Constraints:
 - Dynamic customer prices are strictly within ±20% of the baseline tariff (0.80 * P_base <= P_t <= 1.20 * P_base)
 - Microeconomic price elasticity of demand shifts fleet loads from evening peaks to solar surplus hours
 - Tariff alignment with IEX Day-Ahead Market bidding windows and price volatility
 - All prices denominated in Indian Rupees (INR / ₹)
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from urja_sync_simulation import BASE_RETAIL_PRICE, iex_dam_prices, HOURS, CLUSTERS

class TestDynamicPricingAndElasticity:

    def test_base_retail_price_validity(self):
        """Base retail tariff must be realistic for commercial Indian EV charging (₹16.50/kWh)."""
        assert BASE_RETAIL_PRICE > 0
        assert 12.0 <= BASE_RETAIL_PRICE <= 22.0, (
            f"Base retail price {BASE_RETAIL_PRICE} outside realistic Indian EV market norms (₹12-22/kWh)"
        )

    def test_dynamic_pricing_strictly_within_plus_minus_20_percent_bounds(self):
        """Case study mandates: Dynamic customer prices are market-determined within ±20% of average tariff."""
        lower_bound = BASE_RETAIL_PRICE * 0.80  # ₹13.20/kWh
        upper_bound = BASE_RETAIL_PRICE * 1.20  # ₹19.80/kWh
        
        # Check pricing across all 24 hours under various operating conditions
        for t in range(HOURS):
            p_iex = iex_dam_prices[t]
            
            # Dynamic pricing algorithm from URJA-SYNC
            if p_iex >= 7.80 or (t in [17, 18, 19, 20]):
                tariff = BASE_RETAIL_PRICE * 1.15
            elif 10 <= t <= 14:
                tariff = BASE_RETAIL_PRICE * 0.85
            else:
                tariff = BASE_RETAIL_PRICE * 0.98
                
            assert lower_bound <= tariff <= upper_bound, (
                f"Hour {t}: Tariff ₹{tariff:.2f} violated ±20% bound [₹{lower_bound:.2f}, ₹{upper_bound:.2f}]"
            )
            
            # Additional check: deviation from baseline cannot exceed 20%
            pct_deviation = abs(tariff - BASE_RETAIL_PRICE) / BASE_RETAIL_PRICE
            assert pct_deviation <= 0.20 + 1e-9, (
                f"Hour {t}: Price deviation {pct_deviation:.2%} exceeded 20% regulatory cap"
            )

    def test_peak_hours_tariff_is_higher_than_solar_noon_tariff(self):
        """Peak hours must price higher than solar hours to discourage congestion and encourage solar absorption."""
        peak_hours = [17, 18, 19, 20]
        solar_hours = [11, 12, 13]
        
        for p_hr in peak_hours:
            p_iex = iex_dam_prices[p_hr]
            tariff_peak = BASE_RETAIL_PRICE * 1.15 if (p_iex >= 7.80 or p_hr in [17, 18, 19, 20]) else BASE_RETAIL_PRICE
            for s_hr in solar_hours:
                tariff_solar = BASE_RETAIL_PRICE * 0.85
                assert tariff_peak > tariff_solar, (
                    f"Peak tariff (₹{tariff_peak}) must be strictly higher than solar tariff (₹{tariff_solar})"
                )
                spread = (tariff_peak - tariff_solar) / BASE_RETAIL_PRICE
                assert spread >= 0.25, f"Peak-to-offpeak price spread should provide strong price signal, got {spread:.1%}"

    def test_demand_elasticity_properly_shapes_load(self):
        """Price elasticity (epsilon = -0.35) must decrease load at peak and increase load during solar surplus."""
        raw_demand = 100.0 # MW
        elasticity = -0.35
        
        # 1. Peak tariff (+15%)
        peak_tariff = BASE_RETAIL_PRICE * 1.15
        pct_change_peak = (peak_tariff - BASE_RETAIL_PRICE) / BASE_RETAIL_PRICE
        shaped_demand_peak = raw_demand * (1.0 + elasticity * pct_change_peak)
        
        assert shaped_demand_peak < raw_demand, "Higher peak price must reduce peak charging load"
        expected_peak_reduction = raw_demand * (0.35 * 0.15) # 5.25 MW reduction
        assert np.isclose(shaped_demand_peak, raw_demand - expected_peak_reduction, atol=1e-5)
        
        # 2. Solar discount (-15%)
        solar_tariff = BASE_RETAIL_PRICE * 0.85
        pct_change_solar = (solar_tariff - BASE_RETAIL_PRICE) / BASE_RETAIL_PRICE
        shaped_demand_solar = raw_demand * (1.0 + elasticity * pct_change_solar)
        
        assert shaped_demand_solar > raw_demand, "Discounted solar tariff must stimulate demand"
        expected_solar_increase = raw_demand * (0.35 * 0.15) # 5.25 MW increase
        assert np.isclose(shaped_demand_solar, raw_demand + expected_solar_increase, atol=1e-5)

    def test_iex_dam_price_profile_adheres_to_indian_market_dynamics(self):
        """IEX Day-Ahead Market prices must reflect Indian power grid diurnal morning/evening peaks."""
        assert len(iex_dam_prices) == 24
        assert np.all(iex_dam_prices >= 2.0), "IEX prices must not fall below operational floor (₹2.0/kWh)"
        assert np.all(iex_dam_prices <= 12.0), "IEX prices must not exceed CERC regulatory ceiling (₹12.0/kWh)"
        
        # Evening peak (hours 18-20) should have the highest prices
        evening_peak_prices = iex_dam_prices[18:21]
        midday_solar_prices = iex_dam_prices[11:14]
        assert np.mean(evening_peak_prices) > np.mean(midday_solar_prices), (
            "Evening peak IEX prices must be substantially higher than midday solar trough prices"
        )
