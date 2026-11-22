"""
URJA-SYNC Test Suite: Verification of End-to-End AI/ML Training Pipeline
Tests:
 1. generate_historical_dataset: Verifies 5-metro data generation engine (Weather, IEX, Logs)
 2. QuantileLoss: Verifies multi-quantile pinball loss formulation
 3. URJAGatedLSTM: Verifies forward pass, gating mechanism and quantile heads
 4. Training Artifacts: Checks saved weights (urja_sync_tft_model.pt), metrics JSON and exhibit PNG
"""

import pytest
import numpy as np
import torch
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai_ml_pipeline import (
    generate_historical_dataset,
    QuantileLoss,
    URJAGatedLSTM
)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class TestAIMLPipeline:

    def test_historical_dataset_generator(self):
        """Verifies synthetic dataset engine correctly populates 5 clusters and required features."""
        df = generate_historical_dataset(n_days=5)
        
        # Check cluster coverage
        clusters = set(df['cluster'].unique())
        expected_clusters = {'Delhi NCR', 'Mumbai MMR', 'Bengaluru', 'Hyderabad', 'Chennai'}
        assert clusters == expected_clusters
        
        # Check expected columns
        required_cols = [
            'timestamp', 'cluster', 'hour', 'day_of_week', 'temp_c',
            'solar_ghi', 'wind_speed', 'iex_dam_price', 're_gen_mw', 'demand_mw'
        ]
        for col in required_cols:
            assert col in df.columns, f"Missing column {col} in generated dataset"
            
        assert len(df) == 5 * 5 * 24 # 5 clusters * 5 days * 24 hours = 600
        assert np.all(df['demand_mw'] >= 0.0)
        assert np.all(df['iex_dam_price'] >= 2.0)
        assert np.all(df['re_gen_mw'] >= 0.0)

    def test_quantile_loss_pinball_math(self):
        """Verifies Pinball Quantile Loss for P10, P50, P90."""
        loss_fn = QuantileLoss(quantiles=[0.10, 0.50, 0.90])
        
        # Targets: [100.0, 100.0]
        target = torch.tensor([100.0, 100.0])
        # Perfect predictions: [100.0, 100.0, 100.0]
        preds_perfect = torch.tensor([[100.0, 100.0, 100.0], [100.0, 100.0, 100.0]])
        loss_zero = loss_fn(preds_perfect, target)
        assert np.isclose(loss_zero.item(), 0.0, atol=1e-5)
        
        # Biased predictions
        preds_low = torch.tensor([[90.0, 90.0, 90.0], [90.0, 90.0, 90.0]])
        loss_val = loss_fn(preds_low, target)
        assert loss_val.item() > 0.0

    def test_urja_gated_lstm_forward(self):
        """Verifies PyTorch Gated LSTM architecture forward pass."""
        model = URJAGatedLSTM(input_dim=8, hidden_dim=32, num_layers=1, num_quantiles=3)
        batch_size = 4
        seq_len = 12
        input_dim = 8
        
        dummy_input = torch.rand(batch_size, seq_len, input_dim)
        output = model(dummy_input)
        
        assert output.shape == (batch_size, 3)
        assert not torch.isnan(output).any()

    def test_pipeline_saved_artifacts_integrity(self):
        """Verifies trained model weights, evaluation metrics JSON, and training plots exist."""
        weights_path = os.path.join(BASE_DIR, 'urja_sync_tft_model.pt')
        metrics_path = os.path.join(BASE_DIR, 'ml_evaluation_metrics.json')
        plot_path = os.path.join(BASE_DIR, 'model_training_metrics.png')
        
        assert os.path.exists(weights_path), f"Missing model weights: {weights_path}"
        assert os.path.getsize(weights_path) > 10000, "Model weights file too small"
        
        assert os.path.exists(metrics_path), f"Missing metrics: {metrics_path}"
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
            
        assert metrics['test_r2_score'] >= 0.95, f"R^2 score should be high, got {metrics['test_r2_score']}"
        assert metrics['test_mae_mw'] < 15.0, f"MAE should be low, got {metrics['test_mae_mw']} MW"
        
        assert os.path.exists(plot_path), f"Missing training metrics plot: {plot_path}"
        assert os.path.getsize(plot_path) > 50000, "Plot file too small"
