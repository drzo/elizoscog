#!/usr/bin/env python3
"""
Generate detailed functional feature checklists for discovered repositories
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

def analyze_repo_features(repo: Dict[str, Any]) -> List[str]:
    """Analyze repository to extract features and capabilities"""
    features = []
    
    name = repo['name'].lower()
    description = (repo['description'] or '').lower()
    languages = repo.get('languages', {})
    topics = repo.get('topics', [])
    
    # Language-based features
    if 'Python' in languages:
        features.append("Python implementation")
    if 'C++' in languages:
        features.append("C++ implementation")
    if 'JavaScript' in languages or 'TypeScript' in languages:
        features.append("JavaScript/TypeScript implementation")
    if 'Scheme' in languages:
        features.append("Scheme implementation")
    if 'C' in languages:
        features.append("C implementation")
    if 'Java' in languages:
        features.append("Java implementation")
    
    # Common feature patterns
    feature_patterns = {
        'api': "API interface",
        'cli': "Command-line interface",
        'web': "Web interface",
        'gui': "Graphical user interface",
        'database': "Database integration",
        'network': "Network communication",
        'nlp': "Natural language processing",
        'ml': "Machine learning",
        'ai': "Artificial intelligence",
        'bot': "Bot/Agent functionality",
        'chat': "Chat functionality",
        'connector': "External system connector",
        'plugin': "Plugin architecture",
        'test': "Testing framework",
        'doc': "Documentation system",
        'parser': "Parsing capabilities",
        'server': "Server functionality",
        'client': "Client functionality",
        'storage': "Data storage",
        'visualization': "Data visualization",
        'analysis': "Data analysis",
        'processing': "Data processing"
    }
    
    for pattern, feature in feature_patterns.items():
        if pattern in name or pattern in description or pattern in ' '.join(topics):
            features.append(feature)
    
    # Topic-based features
    for topic in topics:
        if topic not in ['opensource', 'github', 'mit', 'license']:
            features.append(f"Topic: {topic}")
    
    # Repository characteristics
    if repo.get('stargazers_count', 0) > 100:
        features.append("Popular project (100+ stars)")
    if repo.get('forks_count', 0) > 20:
        features.append("Active community (20+ forks)")
    if not repo.get('archived', False):
        features.append("Active development")
    if repo.get('license'):
        features.append(f"Licensed under {repo['license']}")
    
    return features

def generate_integration_checklist(repo: Dict[str, Any], target_ecosystem: str) -> List[str]:
    """Generate integration checklist for cross-ecosystem compatibility"""
    checklist = []
    
    if target_ecosystem == 'opencog':
        # Integration into OpenCog ecosystem
        checklist.extend([
            "[ ] Analyze AtomSpace compatibility",
            "[ ] Identify Scheme binding opportunities", 
            "[ ] Map data structures to Atoms/Links",
            "[ ] Evaluate CogServer integration potential",
            "[ ] Design distributed processing interface",
            "[ ] Plan hypergraph representation",
            "[ ] Consider PLN reasoning integration"
        ])
    elif target_ecosystem == 'elizaos':
        # Integration into ElizaOS ecosystem
        checklist.extend([
            "[ ] Design agent plugin interface",
            "[ ] Map to ElizaOS action framework",
            "[ ] Implement client connector pattern",
            "[ ] Design multi-agent coordination",
            "[ ] Plan memory system integration", 
            "[ ] Consider real-time communication needs",
            "[ ] Evaluate UI/dashboard integration"
        ])
    
    # Common integration tasks
    checklist.extend([
        "[ ] Create API compatibility layer",
        "[ ] Design configuration management",
        "[ ] Implement error handling",
        "[ ] Add logging and monitoring",
        "[ ] Create integration tests",
        "[ ] Write integration documentation",
        "[ ] Plan deployment strategy",
        "[ ] Consider security implications"
    ])
    
    return checklist

def generate_feature_checklist(categorized_repos: Dict[str, List[Dict[str, Any]]], org_name: str) -> str:
    """Generate markdown feature checklist for all repositories"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    content = f"""# {org_name} Repository Feature Checklist

*Generated on: {timestamp}*

This document provides a comprehensive feature analysis and integration checklist for all {org_name} repositories.

"""
    
    for category, repos in categorized_repos.items():
        if not repos:
            continue
            
        content += f"## {category.title()} Repositories\n\n"
        
        for repo in repos:
            content += f"### [{repo['name']}]({repo['html_url']})\n"
            content += f"**Description:** {repo['description'] or 'No description available'}\n\n"
            
            # Repository stats
            content += f"**Stats:** ⭐ {repo['stargazers_count']} | 🍴 {repo['forks_count']} | 🐛 {repo['open_issues_count']} issues\n"
            content += f"**Last Updated:** {repo['updated_at'][:10]}\n"
            if repo.get('license'):
                content += f"**License:** {repo['license']}\n"
            content += "\n"
            
            # Languages
            if repo.get('languages'):
                lang_str = ", ".join(repo['languages'].keys())
                content += f"**Languages:** {lang_str}\n\n"
            
            # Features
            features = analyze_repo_features(repo)
            if features:
                content += "**Features:**\n"
                for feature in features:
                    content += f"- {feature}\n"
                content += "\n"
            
            # Integration checklists
            if org_name.lower() == 'opencog':
                target = 'elizaos'
            else:
                target = 'opencog'
                
            integration_tasks = generate_integration_checklist(repo, target)
            content += f"**Integration with {target.title()}:**\n"
            for task in integration_tasks:
                content += f"{task}\n"
            content += "\n"
            
            # Recent activity
            if repo.get('recent_activity'):
                content += "**Recent Activity:**\n"
                for activity in repo['recent_activity'][:3]:
                    content += f"- {activity['date'][:10]}: {activity['message'][:60]}...\n"
                content += "\n"
            
            content += "---\n\n"
    
    return content

def main():
    """Generate feature checklists for all discovered repositories"""
    
    data_dir = 'data/repositories'
    docs_dir = 'docs/integration'
    
    os.makedirs(docs_dir, exist_ok=True)
    
    # Process each organization's data
    for org_file in ['opencog_repos.json', 'elizaos_repos.json']:
        filepath = os.path.join(data_dir, org_file)
        
        if not os.path.exists(filepath):
            print(f"Repository data not found: {filepath}")
            continue
            
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        org_name = data['organization']
        categorized_repos = data['categories']
        
        # Generate feature checklist
        checklist_content = generate_feature_checklist(categorized_repos, org_name)
        
        # Save to docs
        output_file = os.path.join(docs_dir, f'{org_name.lower()}_features.md')
        with open(output_file, 'w') as f:
            f.write(checklist_content)
        
        print(f"Generated feature checklist: {output_file}")
        
        # Generate summary stats
        total_repos = sum(len(repos) for repos in categorized_repos.values())
        print(f"  {org_name}: {total_repos} repositories processed")

if __name__ == '__main__':
    main()