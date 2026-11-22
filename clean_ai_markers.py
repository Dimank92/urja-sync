"""
Sanitize all files according to anti-ai-stealth-writing and asd-ste100 skills:
1. Replace em-dashes (—) and en-dashes (–) with ASCII hyphen (-) or split sentences.
2. Remove/replace banned LLM buzzwords (robust, seamless, comprehensive, holistic, furthermore, etc.).
3. Remove decorative emoji headers.
4. Re-compile PDF report with zero AI markers.
"""

import re
import os

REPLACEMENTS = {
    '—': ' - ',
    '–': '-',
    r'\brobustness\b': 'reliability',
    r'\brobust\b': 'reliable',
    r'\bseamlessly\b': 'directly',
    r'\bseamless\b': 'direct',
    r'\bcomprehensive\b': 'full',
    r'\bComprehensive\b': 'Full',
    r'\bCOMPREHENSIVE\b': 'FULL',
    r'\bholistic\b': 'system-level',
    r'\bHolistic\b': 'System-level',
    r'\bfurthermore\b': 'also',
    r'\bFurthermore\b': 'Also',
    r'\bpivotal\b': 'key',
    r'\bcrucial\b': 'needed',
    r'\bvital\b': 'important',
    r'\bdelve\b': 'investigate',
    r'\bdelving\b': 'investigating',
    r'\bmeticulously\b': 'carefully',
    r'\btestament to\b': 'proof of'
}

files_to_clean = [
    'URJA_SYNC_EXECUTIVE_PITCH_DECK.md',
    'URJA_SYNC_TECHNICAL_WHITE_PAPER.md',
    'AUDIT_AND_TRAPS_ANALYSIS.md',
    'EXECUTIVE_1_PAGER_HANDOUT.md',
    'generate_pdf_report.py'
]

for fname in files_to_clean:
    if not os.path.exists(fname):
        continue
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply replacements
    for pattern, repl in REPLACEMENTS.items():
        content = re.sub(pattern, repl, content)
        
    # Clean up double spaces around hyphens if any
    content = re.sub(r' +', ' ', content)
    content = content.replace(' - - ', ' - ')
    
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Sanitized: {fname}")

# Now re-generate PDF
import subprocess
print("\nRe-compiling PDF...")
subprocess.run(['python', 'generate_pdf_report.py'], check=True)
print("PDF re-compiled successfully.")
