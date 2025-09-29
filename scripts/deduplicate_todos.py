#!/usr/bin/env python3
"""
TODO Files Deduplication Script

Removes duplicate sections from TODO-ES.md and TODO-OC.md while preserving
unique content and proper structure.
"""

import re
from pathlib import Path
from typing import List, Tuple, Set
from datetime import datetime

class TODODeduplicator:
    """Removes duplicate content from TODO files"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path('.')
        self.todo_es_path = self.base_dir / 'TODO-ES.md'
        self.todo_oc_path = self.base_dir / 'TODO-OC.md'
    
    def analyze_duplicates(self, content: str) -> dict:
        """Analyze duplicate patterns in content"""
        # Find all sections starting with ##
        sections = re.findall(r'^## (.+?)(?=\n## |\n#(?!#)|\Z)', content, re.MULTILINE | re.DOTALL)
        
        section_counts = {}
        for section in sections:
            section_title = section.split('\n')[0].strip()
            section_counts[section_title] = section_counts.get(section_title, 0) + 1
        
        return section_counts
    
    def extract_unique_sections(self, content: str) -> str:
        """Extract unique sections, removing duplicates"""
        lines = content.split('\n')
        result_lines = []
        seen_sections = set()
        current_section = None
        section_lines = []
        in_section = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a section header
            if line.startswith('## '):
                # Save previous section if it was unique
                if current_section and current_section not in seen_sections:
                    result_lines.extend(section_lines)
                    seen_sections.add(current_section)
                elif current_section:
                    print(f"  Skipping duplicate section: {current_section}")
                
                # Start new section
                current_section = line[3:].strip()
                section_lines = [line]
                in_section = True
            elif line.startswith('# ') and not line.startswith('## '):
                # Main header - always include
                if current_section and current_section not in seen_sections:
                    result_lines.extend(section_lines)
                    seen_sections.add(current_section)
                
                result_lines.append(line)
                current_section = None
                section_lines = []
                in_section = False
            elif in_section:
                section_lines.append(line)
            else:
                result_lines.append(line)
            
            i += 1
        
        # Don't forget the last section
        if current_section and current_section not in seen_sections:
            result_lines.extend(section_lines)
        
        return '\n'.join(result_lines)
    
    def preserve_unique_content(self, content: str) -> str:
        """Preserve only the first occurrence of each section, maintaining structure"""
        # Split content into major sections
        sections = re.split(r'\n(?=## )', content)
        unique_sections = []
        seen_titles = set()
        
        for section in sections:
            if not section.strip():
                continue
                
            # Get section title
            lines = section.split('\n')
            if lines and lines[0].startswith('## '):
                title = lines[0][3:].strip()
                
                # Skip certain sections that are clearly duplicated
                if title in seen_titles:
                    print(f"  Removing duplicate section: {title}")
                    continue
                
                seen_titles.add(title)
            
            unique_sections.append(section)
        
        return '\n'.join(unique_sections)
    
    def clean_todo_es(self) -> str:
        """Clean TODO-ES.md by removing massive duplication"""
        print("Cleaning TODO-ES.md...")
        
        with open(self.todo_es_path, 'r') as f:
            content = f.read()
        
        print(f"  Original length: {len(content.split())} lines")
        
        # Analyze duplicates first
        section_counts = self.analyze_duplicates(content)
        duplicates = {k: v for k, v in section_counts.items() if v > 1}
        
        if duplicates:
            print("  Found duplicate sections:")
            for section, count in duplicates.items():
                print(f"    '{section}': {count} occurrences")
        
        # Remove duplicates while preserving structure
        cleaned_content = self.preserve_unique_content(content)
        
        print(f"  Cleaned length: {len(cleaned_content.split())} lines")
        print(f"  Reduction: {len(content) - len(cleaned_content)} characters")
        
        return cleaned_content
    
    def clean_todo_oc(self) -> str:
        """Clean TODO-OC.md if needed"""
        print("Checking TODO-OC.md...")
        
        with open(self.todo_oc_path, 'r') as f:
            content = f.read()
        
        print(f"  Current length: {len(content.split())} lines")
        
        # Analyze for duplicates
        section_counts = self.analyze_duplicates(content)
        duplicates = {k: v for k, v in section_counts.items() if v > 1}
        
        if duplicates:
            print("  Found duplicate sections:")
            for section, count in duplicates.items():
                print(f"    '{section}': {count} occurrences")
            content = self.preserve_unique_content(content)
            print("  Cleaned TODO-OC.md")
        else:
            print("  No duplicates found in TODO-OC.md")
        
        return content
    
    def backup_files(self):
        """Create backups of original files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.todo_es_path.exists():
            backup_es = self.base_dir / f'TODO-ES.md.backup_{timestamp}'
            backup_es.write_text(self.todo_es_path.read_text())
            print(f"Created backup: {backup_es}")
        
        if self.todo_oc_path.exists():
            backup_oc = self.base_dir / f'TODO-OC.md.backup_{timestamp}'
            backup_oc.write_text(self.todo_oc_path.read_text())
            print(f"Created backup: {backup_oc}")
    
    def deduplicate_files(self):
        """Main deduplication process"""
        print("Starting TODO files deduplication...")
        
        # Create backups
        self.backup_files()
        
        # Clean TODO-ES.md (the main culprit)
        if self.todo_es_path.exists():
            cleaned_es = self.clean_todo_es()
            self.todo_es_path.write_text(cleaned_es)
            print("✅ TODO-ES.md deduplicated")
        
        # Clean TODO-OC.md if needed
        if self.todo_oc_path.exists():
            cleaned_oc = self.clean_todo_oc()
            self.todo_oc_path.write_text(cleaned_oc)
            print("✅ TODO-OC.md checked and cleaned if needed")
        
        print("\n🎉 Deduplication complete!")
        print(f"  - Backups created with timestamp suffix")
        print(f"  - TODO-ES.md: Massive duplication removed")
        print(f"  - TODO-OC.md: Checked and cleaned")

def main():
    """Main function"""
    base_dir = Path('.')
    deduplicator = TODODeduplicator(base_dir)
    
    try:
        deduplicator.deduplicate_files()
    except Exception as e:
        print(f"Error during deduplication: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())