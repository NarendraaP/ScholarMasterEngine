#!/usr/bin/env python3
"""
File Audit Script
Identifies potentially unused files by comparing against a golden list of essential files.
Does NOT delete anything - only reports for manual review.
"""

import os
import pathlib
from pathlib import Path

# Golden List of Essential Files and Patterns
ESSENTIAL_FILES = {
    # Main Application Files
    "admin_panel.py",
    "multi_stream_simulation.py",
    "test_live.py",
    "requirements.txt",
    ".gitignore",
    "README.md",
    
    # Model Files
    "models/yolov8n-pose.pt",
}

ESSENTIAL_DIRECTORIES = {
    "modules",
    "utils",
    "data",
    "tests",
    "scripts",
    "benchmarks",
    ".git",
    ".venv",
    "models",
    "__pycache__",
    ".pytest_cache",
}

ESSENTIAL_EXTENSIONS = {
    ".py",   # Python source files
    ".md",   # Documentation
    ".json", # Config files
    ".csv",  # Data files
    ".txt",  # Text files
}

# Files to explicitly ignore (known temporary/generated)
KNOWN_TEMP_PATTERNS = {
    "__pycache__",
    ".pyc",
    ".DS_Store",
    ".pytest_cache",
    "*.tmp",
    ".coverage",
}

def read_gitignore(project_root):
    """Read .gitignore patterns."""
    gitignore_path = project_root / ".gitignore"
    patterns = set()
    
    if gitignore_path.exists():
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        patterns.add(line)
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            try:
                with open(gitignore_path, 'r', encoding='latin-1') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.add(line)
            except Exception as e:
                print(f"⚠️  Could not read .gitignore: {e}")
    
    return patterns

def is_ignored_by_gitignore(file_path, gitignore_patterns):
    """Simple check if file matches any gitignore pattern."""
    file_name = file_path.name
    file_str = str(file_path)
    
    for pattern in gitignore_patterns:
        # Simple pattern matching (not full git pattern support)
        if pattern.endswith('/'):
            # Directory pattern
            if pattern[:-1] in file_str:
                return True
        elif pattern.startswith('*.'):
            # Extension pattern
            if file_name.endswith(pattern[1:]):
                return True
        elif pattern in file_str:
            # Substring match
            return True
    
    return False

def is_essential(file_path, project_root):
    """Check if a file is essential based on golden list."""
    relative_path = file_path.relative_to(project_root)
    
    # Check if in essential files
    if file_path.name in ESSENTIAL_FILES:
        return True
    
    # Check if in essential directory
    parts = relative_path.parts
    if parts and parts[0] in ESSENTIAL_DIRECTORIES:
        return True
    
    # Check if has essential extension
    if file_path.suffix in ESSENTIAL_EXTENSIONS:
        return True
    
    return False

def audit_files(project_root="."):
    """
    Audit all files in the project.
    """
    project_root = Path(project_root).resolve()
    
    print("=" * 70)
    print("🔍 File Audit Report")
    print("=" * 70)
    print(f"\n📂 Project Root: {project_root}\n")
    
    # Read gitignore
    gitignore_patterns = read_gitignore(project_root)
    print(f"📋 Loaded {len(gitignore_patterns)} .gitignore patterns\n")
    
    # Scan all files
    all_files = []
    unknown_files = []
    essential_count = 0
    ignored_count = 0
    
    for file_path in project_root.rglob("*"):
        if file_path.is_file():
            all_files.append(file_path)
            
            # Check if ignored by gitignore
            if is_ignored_by_gitignore(file_path, gitignore_patterns):
                ignored_count += 1
                continue
            
            # Check if essential
            if is_essential(file_path, project_root):
                essential_count += 1
                continue
            
            # If not essential and not ignored, mark as unknown
            unknown_files.append(file_path)
    
    # Print summary
    print(f"📊 Summary:")
    print(f"   Total files scanned: {len(all_files)}")
    print(f"   Essential files: {essential_count}")
    print(f"   Ignored files (.gitignore): {ignored_count}")
    print(f"   Unknown files: {len(unknown_files)}")
    
    # Print unknown files
    if unknown_files:
        print("\n" + "=" * 70)
        print("⚠️  Unknown Files (Review for Deletion)")
        print("=" * 70)
        
        for file_path in sorted(unknown_files):
            relative_path = file_path.relative_to(project_root)
            file_size = file_path.stat().st_size
            size_kb = file_size / 1024
            
            if size_kb > 1024:
                size_str = f"{size_kb/1024:.2f} MB"
            else:
                size_str = f"{size_kb:.2f} KB"
            
            print(f"   📄 {relative_path} ({size_str})")
        
        print("\n💡 Recommendation:")
        print("   Review the files above. Delete if they are:")
        print("   - Temporary files")
        print("   - Old documentation")
        print("   - Duplicate files")
        print("   - Generated files that should be in .gitignore")
    else:
        print("\n✅ No unknown files found! Project is clean.")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    audit_files()
