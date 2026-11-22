"""
URJA-SYNC Test Suite: Data Integrity, Export Artifacts & Simulation Reproducibility
Verifies that all generated reports, exhibits, and data artifacts are intact:
 - JSON simulation result files (calibrated_simulation_results.json, stress_test_results.json)
 - High-resolution visualization exhibits (exhibit 1 through 4 PNG files)
 - Executive PDF report (URJA_SYNC_COMPREHENSIVE_REPORT.pdf)
 - Technical white paper and pitch deck markdown documents
 - Numerical determinism and simulation idempotency under fixed seed
"""

import pytest
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from urja_sync_simulation import run_calibrated_simulation

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class TestDataAndReportArtifacts:

    def test_calibrated_simulation_json_artifact_integrity(self):
        """Verifies existence and complete schema of calibrated_simulation_results.json."""
        filepath = os.path.join(BASE_DIR, 'calibrated_simulation_results.json')
        assert os.path.exists(filepath), f"Missing {filepath}"
        
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        assert 'baseline' in data and 'urjasync' in data
        for mode in ['baseline', 'urjasync']:
            sub = data[mode]
            assert 'reliability_pct' in sub
            assert 'loss_pct' in sub
            assert 'ebitda_margin_pct' in sub
            assert 'daily_rev_cr' in sub
            assert 'daily_cost_cr' in sub
            assert 'daily_ebitda_cr' in sub
            assert 'annual_ebitda_cr' in sub
            assert 'cluster_margins' in sub
            assert len(sub['cluster_margins']) == 5

    def test_stress_test_json_artifact_integrity(self):
        """Verifies existence and schema of stress_test_results.json."""
        filepath = os.path.join(BASE_DIR, 'stress_test_results.json')
        assert os.path.exists(filepath), f"Missing {filepath}"
        
        with open(filepath, 'r') as f:
            scenarios = json.load(f)
            
        assert len(scenarios) == 5
        for sc in scenarios:
            assert 'scenario' in sc
            assert 'reliability_pct' in sc
            assert 'loss_pct' in sc
            assert 'ebitda_margin_pct' in sc
            assert 'cluster_margins' in sc
            assert sc['hurdle_12pct_met'] is True
            assert sc['reliability_target_met'] is True
            assert sc['loss_target_met'] is True

    def test_all_high_resolution_exhibits_exist_and_non_empty(self):
        """Verifies that all 4 presentation exhibits are generated as valid PNG files."""
        exhibits = [
            'exhibit1_kpi_scorecard.png',
            'exhibit2_cluster_margins.png',
            'exhibit3_24h_dispatch_delhi.png',
            'exhibit4_scenario_stress_testing.png'
        ]
        for exh in exhibits:
            filepath = os.path.join(BASE_DIR, exh)
            assert os.path.exists(filepath), f"Exhibit missing: {filepath}"
            file_size = os.path.getsize(filepath)
            # Valid PNG exhibits should be high-res (> 50,000 bytes)
            assert file_size > 50000, f"Exhibit {exh} file size too small ({file_size} bytes)"

    def test_pdf_report_exists_and_meets_size_standards(self):
        """Verifies that URJA_SYNC_COMPREHENSIVE_REPORT.pdf exists and is > 500 KB."""
        pdf_path = os.path.join(BASE_DIR, 'URJA_SYNC_COMPREHENSIVE_REPORT.pdf')
        assert os.path.exists(pdf_path), f"Missing PDF report: {pdf_path}"
        pdf_size = os.path.getsize(pdf_path)
        assert pdf_size > 500000, f"PDF report seems truncated ({pdf_size} bytes)"

    def test_documentation_markdown_files_exist(self):
        """Verifies that technical white paper and pitch deck are present and substantial."""
        docs = [
            'URJA_SYNC_TECHNICAL_WHITE_PAPER.md',
            'URJA_SYNC_EXECUTIVE_PITCH_DECK.md'
        ]
        for doc in docs:
            filepath = os.path.join(BASE_DIR, doc)
            assert os.path.exists(filepath), f"Missing documentation file: {filepath}"
            assert os.path.getsize(filepath) > 5000, f"Documentation file {doc} too short"

    def test_simulation_numerical_determinism(self):
        """Simulation must be 100% deterministic and reproducible under random seed 42."""
        import numpy as np
        np.random.seed(42)
        run_calibrated_simulation()
        
        path = os.path.join(BASE_DIR, 'calibrated_simulation_results.json')
        with open(path, 'r') as f:
            run1 = json.load(f)
            
        np.random.seed(42)
        run_calibrated_simulation()
        with open(path, 'r') as f:
            run2 = json.load(f)
            
        assert run1['urjasync']['reliability_pct'] == run2['urjasync']['reliability_pct']
        assert run1['urjasync']['loss_pct'] == run2['urjasync']['loss_pct']
        assert run1['urjasync']['ebitda_margin_pct'] == run2['urjasync']['ebitda_margin_pct']
        assert run1['urjasync']['annual_ebitda_cr'] == run2['urjasync']['annual_ebitda_cr']
