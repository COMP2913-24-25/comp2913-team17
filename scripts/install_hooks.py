#!/usr/bin/env python3
"""
Install Git hooks to automatically run security scanning before commits.
"""

import os
import stat

def install_pre_commit_hook():
    """Install the pre-commit hook that runs security scans."""
    
    # Project root directory
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Git hooks directory
    hooks_dir = os.path.join(root_dir, '.git', 'hooks')
    
    # Create the pre-commit hook file
    pre_commit_path = os.path.join(hooks_dir, 'pre-commit')
    with open(pre_commit_path, 'w') as f:
        f.write('''#!/bin/bash
# Pre-commit hook to run security scans

# Store the current directory
CURRENT_DIR=$(pwd)

# Get the project root directory
PROJECT_ROOT=$(git rev-parse --show-toplevel)

# Change to the project root directory
cd "$PROJECT_ROOT"

# Run the security scan script
python scripts/security_scan.py

# Get the result
RESULT=$?

# Restore the current directory
cd "$CURRENT_DIR"

# If the script returned an error, prevent the commit
if [ $RESULT -ne 0 ]; then
    echo "Security scan failed. Commit aborted."
    exit 1
fi

# Otherwise allow the commit
exit 0
''')
    
    # Make the hook executable
    os.chmod(pre_commit_path, os.stat(pre_commit_path).st_mode | stat.S_IEXEC)
    
    print(f"Pre-commit hook installed at: {pre_commit_path}")
    print("Security scanning will now run automatically before each commit.")

if __name__ == "__main__":
    install_pre_commit_hook()
