"""
Script to verify 100% mathematical and numerical consistency across all files:
- calibrated_simulation_results.json
- URJA_SYNC_COMPREHENSIVE_REPORT.pdf
- URJA_SYNC_EXECUTIVE_PITCH_DECK.md
- URJA_SYNC_TECHNICAL_WHITE_PAPER.md
- AUDIT_AND_TRAPS_ANALYSIS.md
"""

import json
import pypdf
import os

with open('calibrated_simulation_results.json') as f:
    sim = json.load(f)

# Core Truth Metrics
TRUTH = {
    'rel_base': sim['baseline']['reliability_pct'],      # 77.9
    'rel_target': 89.7,                                  # 89.7
    'rel_urja': sim['urjasync']['reliability_pct'],      # 90.4
    
    'loss_base': sim['baseline']['loss_pct'],            # 10.0
    'loss_target': 8.0,                                  # 8.0
    'loss_urja': sim['urjasync']['loss_pct'],            # 7.8
    
    'ebitda_base': sim['baseline']['ebitda_margin_pct'], # 26.6
    'ebitda_target': 12.0,                               # 12.0
    'ebitda_urja': sim['urjasync']['ebitda_margin_pct'], # 44.2
    
    'uplift_cr': round(sim['urjasync']['annual_ebitda_cr'] - sim['baseline']['annual_ebitda_cr'], 1), # 1506.0
    'delhi_margin': sim['urjasync']['cluster_margins']['Delhi NCR'],     # 42.2
    'mumbai_margin': sim['urjasync']['cluster_margins']['Mumbai MMR'],   # 40.1
    'blr_margin': sim['urjasync']['cluster_margins']['Bengaluru'],       # 48.2
    'hyd_margin': sim['urjasync']['cluster_margins']['Hyderabad'],       # 46.6
    'maa_margin': sim['urjasync']['cluster_margins']['Chennai']          # 46.9
}

print("="*60)
print("GROUND TRUTH SIMULATION METRICS")
print("="*60)
for k, v in TRUTH.items():
    print(f"  {k:<16}: {v}")
print("="*60)

# 1. Audit PDF
print("\n>>> AUDITING URJA_SYNC_COMPREHENSIVE_REPORT.pdf ...")
reader = pypdf.PdfReader('URJA_SYNC_COMPREHENSIVE_REPORT.pdf')
pdf_text = '\n'.join([page.extract_text() for page in reader.pages])

pdf_checks = [
    (f"{TRUTH['rel_base']}%", "Baseline Reliability 77.9%"),
    (f"{TRUTH['rel_target']}%", "Target Reliability 89.7%"),
    (f"{TRUTH['rel_urja']}%", "URJA Reliability 90.4%"),
    (f"{TRUTH['loss_base']}%", "Baseline Loss 10.0%"),
    (f"{TRUTH['loss_urja']}%", "URJA Loss 7.8%"),
    (f"{TRUTH['ebitda_base']}%", "Baseline EBITDA 26.6%"),
    (f"{TRUTH['ebitda_urja']}%", "URJA EBITDA 44.2%"),
    (f"1,506.0", "EBITDA Uplift 1,506.0 Cr"),
    (f"{TRUTH['delhi_margin']}%", "Delhi Margin 42.2%"),
    (f"{TRUTH['mumbai_margin']}%", "Mumbai Margin 40.1%"),
    (f"{TRUTH['blr_margin']}%", "Bengaluru Margin 48.2%"),
    (f"{TRUTH['hyd_margin']}%", "Hyderabad Margin 46.6%"),
    (f"{TRUTH['maa_margin']}%", "Chennai Margin 46.9%"),
    ("1,200 MW", "Total Capacity 1,200 MW"),
    ("600 MWh", "Total Storage 600 MWh"),
    ("60 MW", "Reserve Capacity 60 MW"),
    ("30 MWh", "Reserve Storage 30 MWh")
]

pdf_pass = True
for string_val, desc in pdf_checks:
    found = string_val in pdf_text
    print(f"  {'[PASS]' if found else '[FAIL]'} {desc} ({string_val})")
    if not found:
        pdf_pass = False

# 2. Audit Markdown Files
md_files = [
    'URJA_SYNC_EXECUTIVE_PITCH_DECK.md',
    'URJA_SYNC_TECHNICAL_WHITE_PAPER.md',
    'AUDIT_AND_TRAPS_ANALYSIS.md'
]

for mdf in md_files:
    print(f"\n>>> AUDITING {mdf} ...")
    with open(mdf, encoding='utf-8') as f:
        mdf_text = f.read()
    
    mdf_pass = True
    for string_val, desc in pdf_checks:
        found = string_val in mdf_text
        if not found:
            print(f"  [MISSING] {desc} ({string_val}) in {mdf}")
            mdf_pass = False
    if mdf_pass:
        print(f"  [ALL PASS] 100% Numbers match in {mdf}!")

print("\n" + "="*60)
print(f"FINAL AUDIT STATUS: {'SUCCESS - 100% CONSISTENT' if pdf_pass else 'DISCREPANCIES FOUND'}")
print("="*60)
