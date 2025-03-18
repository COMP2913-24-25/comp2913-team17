#!/usr/bin/env python3
"""
Security scanning script that runs Bandit with comprehensive options.
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def run_bandit_scan():
    """Run Bandit security scan with the configuration file"""
    print("Starting Bandit security scan...")
    
    # Project root directory
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Config file path
    config_file = os.path.join(root_dir, 'bandit.yaml')
    
    # Report paths
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_report = os.path.join(root_dir, f'security-report_{timestamp}.json')
    html_report = os.path.join(root_dir, f'security-report_{timestamp}.html')
    
    try:
        # Run bandit with JSON output
        subprocess.run([
            'bandit',
            '-r',                  # Recursive scan
            os.path.join(root_dir, 'main'),  # Target directory
            '-c', config_file,     # Config file
            '-f', 'json',          # Output format
            '-o', json_report      # Output file
        ], check=True)
        
        # Generate HTML report
        subprocess.run([
            'bandit',
            '-r',
            os.path.join(root_dir, 'main'),
            '-c', config_file,
            '-f', 'html',
            '-o', html_report
        ], check=True)
        
        # Load and analyze the JSON report
        with open(json_report, 'r') as f:
            results = json.load(f)
        
        # Count issues by severity
        issues_by_severity = {
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0
        }
        
        for result in results.get('results', []):
            severity = result.get('issue_severity', 'LOW')
            issues_by_severity[severity] += 1
        
        total_issues = sum(issues_by_severity.values())
        
        print("\n=== Security Scan Results ===")
        print(f"Total issues found: {total_issues}")
        print(f"HIGH severity issues: {issues_by_severity['HIGH']}")
        print(f"MEDIUM severity issues: {issues_by_severity['MEDIUM']}")
        print(f"LOW severity issues: {issues_by_severity['LOW']}")
        print(f"\nDetailed reports saved to:")
        print(f"- JSON: {json_report}")
        print(f"- HTML: {html_report}")
        
        # Exit with error code if high-severity issues found
        if issues_by_severity['HIGH'] > 0:
            print("\n⚠️  HIGH SEVERITY ISSUES FOUND! Please review and fix before committing. ⚠️")
            return 1
            
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"Error running Bandit: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_bandit_scan())
