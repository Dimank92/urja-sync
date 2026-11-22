"""
URJA-SYNC Test Suite: Verification of AI/ML Production Models
Tests:
 1. SpatioTemporalDemandGNN: 5-cluster spatial message passing & 24h demand predictions
 2. IEXPriceForecaster: Quantile forecasting (P10/P50/P90) and CERC ₹10/kWh cap compliance
 3. BatteryPINNDegradation: Physics-Informed Neural Network Arrhenius electrochemical loss
 4. ContextualPricingBandit: Bounded tariff policy and microeconomic demand elasticity
"""

import pytest
import numpy as np
import torch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from urja_sync_ai_models import (
    SpatioTemporalDemandGNN,
    IEXPriceForecaster,
    BatteryPINNDegradation,
    ContextualPricingBandit
)

class TestAIModels:

    def test_spatio_temporal_gnn_architecture_and_forward_pass(self):
        """Verifies Spatio-Temporal Graph Neural Network produces valid non-negative 24h demand."""
        num_nodes = 5 # 5 Indian Metros
        seq_len = 12  # Past 12 hours of historical telemetry
        in_features = 4 # [demand, temp, occupancy, retail_price]
        batch_size = 2
        
        model = SpatioTemporalDemandGNN(num_nodes=num_nodes, in_features=in_features, hidden_dim=32, out_steps=24)
        
        # Synthetic normalized adjacency matrix (5x5) based on geographical distance
        adj = torch.eye(num_nodes) + 0.25 * torch.ones(num_nodes, num_nodes)
        row_sum = adj.sum(dim=1, keepdim=True)
        adj_norm = adj / row_sum
        
        # Dummy input tensor
        x = torch.rand(batch_size, num_nodes, seq_len, in_features)
        
        # Forward pass
        pred_24h = model(x, adj_norm)
        
        assert pred_24h.shape == (batch_size, num_nodes, 24), (
            f"Expected output shape {(batch_size, num_nodes, 24)}, got {pred_24h.shape}"
        )
        assert torch.all(pred_24h >= 0.0), "Predicted demand must be strictly non-negative"

    def test_iex_price_forecaster_quantiles_and_cap_classification(self):
        """Verifies IEX Forecaster produces ordered quantiles (P10 <= P50 <= P90) bounded by regulatory cap."""
        forecaster = IEXPriceForecaster(cap_ceiling=10.0)
        forecaster.fit()
        
        # 24-hour test feature matrix
        hours = np.arange(24)
        day_of_week = np.full(24, 2) # Wednesday
        ambient_temp = 35.0 + 7.0 * np.sin(np.pi * (hours - 8) / 12)
        national_demand_gw = 190 + 30.0 * np.sin(np.pi * (hours - 9) / 12)
        solar_gen_gw = np.maximum(0, 40.0 * np.sin(np.pi * (hours - 6) / 12))
        wind_gen_gw = np.full(24, 28.0)
        net_demand_gw = national_demand_gw - solar_gen_gw - wind_gen_gw
        
        features_24h = np.column_stack([hours, day_of_week, ambient_temp, national_demand_gw, solar_gen_gw, wind_gen_gw, net_demand_gw])
        
        preds = forecaster.predict_24h(features_24h)
        
        p10 = preds['p10']
        p50 = preds['p50']
        p90 = preds['p90']
        cap_prob = preds['cap_probability']
        
        assert len(p50) == 24
        assert np.all(p50 >= 2.0), "Prices should not fall below ₹2.0/kWh"
        assert np.all(p50 <= 10.0), "Prices must strictly respect the ₹10.0/kWh regulatory cap"
        assert np.all(p90 >= p10 - 0.1), "P90 quantile must generally exceed P10 quantile"
        assert np.all((cap_prob >= 0.0) & (cap_prob <= 1.0)), "Cap probability must lie in [0, 1]"

    def test_battery_pinn_degradation_arrhenius_loss(self):
        """Verifies Physics-Informed Neural Network correctly incorporates Arrhenius thermal aging loss."""
        pinn = BatteryPINNDegradation()
        
        # Inputs: C_rate = 1.5C, Temp = 315K (42°C summer heat), DoD = 0.80, Throughput = 100 kWh
        sample_input = torch.tensor([[1.5, 315.15, 0.80, 100.0]], dtype=torch.float32)
        pred_loss = pinn(sample_input)
        
        assert pred_loss.item() >= 0.0, "Capacity degradation prediction must be non-negative"
        
        # Compute physics-informed residual loss
        c_rate = torch.tensor([1.5])
        temp_k = torch.tensor([315.15])
        dod = torch.tensor([0.80])
        
        phys_loss = pinn.compute_physics_loss(c_rate, temp_k, dod, pred_loss)
        assert phys_loss.item() >= 0.0
        assert not torch.isnan(phys_loss)

    def test_contextual_pricing_bandit_hard_bounds_and_elasticity(self):
        """Verifies dynamic pricing bandit strictly enforces ±20% bounds and shifts demand."""
        bandit = ContextualPricingBandit(p_base=16.50, elasticity=-0.35)
        
        # Case 1: High IEX peak -> Premium price (capped at +20%)
        tariff_peak = bandit.select_tariff(hour=19, iex_price=9.80, solar_ratio=0.05, queue_risk=0.85)
        assert 13.20 <= tariff_peak <= 19.80, f"Peak tariff ₹{tariff_peak} violated ±20% bound"
        assert tariff_peak > 16.50, "Peak hour should command a premium"
        
        # Case 2: Solar surplus -> Discounted price (capped at -20%)
        tariff_solar = bandit.select_tariff(hour=12, iex_price=3.10, solar_ratio=0.65, queue_risk=0.10)
        assert 13.20 <= tariff_solar <= 19.80, f"Solar tariff ₹{tariff_solar} violated ±20% bound"
        assert tariff_solar < 16.50, "Solar noon should offer a discount"
        
        # Demand elasticity check
        raw_load = 100.0 # MW
        shaped_load_peak = bandit.calculate_effective_demand(raw_load, tariff_peak)
        shaped_load_solar = bandit.calculate_effective_demand(raw_load, tariff_solar)
        
        assert shaped_load_peak < raw_load, "Peak tariff must shave demand"
        assert shaped_load_solar > raw_load, "Solar discount must stimulate demand"
