#!/usr/bin/env python3
"""
Repository Discovery Script for OpenCog and ElizaOS organizations
Fetches repository information and generates structured data for integration
"""

import json
import os
import sys
import time
from datetime import datetime
from github import Github
from typing import Dict, List, Any

def discover_organization_repos(org_name: str, github_token: str) -> List[Dict[str, Any]]:
    """Discover all repositories for a given organization"""
    g = Github(github_token)
    
    try:
        org = g.get_organization(org_name)
        repos = []
        
        print(f"Discovering repositories for {org_name}...")
        
        for repo in org.get_repos():
            try:
                # Get additional repository information with error handling
                try:
                    languages = repo.get_languages() or {}
                except Exception as e:
                    print(f"    Warning: Could not get languages for {repo.name}: {e}")
                    languages = {}
                
                try:
                    topics = repo.get_topics() or []
                except Exception as e:
                    print(f"    Warning: Could not get topics for {repo.name}: {e}")
                    topics = []
                
                # Get recent activity with comprehensive error handling
                recent_activity = []
                try:
                    commits = list(repo.get_commits()[:5])  # Last 5 commits
                    for commit in commits:
                        try:
                            # Safely access nested commit properties with null checks
                            commit_data = commit.commit if commit.commit else None
                            author_data = commit_data.author if commit_data and commit_data.author else None
                            
                            recent_activity.append({
                                'sha': commit.sha if commit.sha else 'unknown',
                                'message': commit_data.message if commit_data and commit_data.message else 'No message',
                                'date': author_data.date.isoformat() if author_data and author_data.date else datetime.now().isoformat(),
                                'author': author_data.name if author_data and author_data.name else 'Unknown'
                            })
                        except (AttributeError, TypeError) as e:
                            # Skip commits with incomplete data but log the issue
                            print(f"    Warning: Skipping commit with incomplete data: {e}")
                            continue
                except Exception as e:
                    print(f"    Warning: Could not get commits for {repo.name}: {e}")
                    recent_activity = []
                
                repo_info = {
                    'name': repo.name or 'Unknown',
                    'full_name': repo.full_name or 'Unknown',
                    'description': repo.description,
                    'html_url': repo.html_url or '',
                    'clone_url': repo.clone_url or '',
                    'ssh_url': repo.ssh_url or '',
                    'languages': languages,
                    'topics': topics,
                    'stargazers_count': repo.stargazers_count or 0,
                    'forks_count': repo.forks_count or 0,
                    'open_issues_count': repo.open_issues_count or 0,
                    'size': repo.size or 0,
                    'default_branch': repo.default_branch or 'main',
                    'created_at': repo.created_at.isoformat() if repo.created_at else datetime.now().isoformat(),
                    'updated_at': repo.updated_at.isoformat() if repo.updated_at else datetime.now().isoformat(),
                    'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
                    'archived': repo.archived or False,
                    'disabled': repo.disabled or False,
                    'fork': repo.fork or False,
                    'license': repo.license.name if repo.license else None,
                    'recent_activity': recent_activity,
                    'readme_url': f"{repo.html_url}/blob/{repo.default_branch}/README.md" if repo.html_url and repo.default_branch else ''
                }
                
                repos.append(repo_info)
                print(f"  ✓ {repo.name} - {repo.description[:50]}...")
                
                # Rate limiting courtesy
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  ✗ Error processing {repo.name}: {e}")
                continue
                
    except Exception as e:
        print(f"Error accessing organization {org_name}: {e}")
        return []
    
    return repos

def categorize_repos(repos: List[Dict[str, Any]], org_name: str) -> Dict[str, List[Dict[str, Any]]]:
    """Categorize repositories based on their characteristics"""
    if org_name.lower() == 'opencog':
        categories = {
            'atomspace': [],
            'research': [], 
            'fossils': [],
            'hyperon': [],
            'incubator': []
        }
        
        for repo in repos:
            name_lower = repo['name'].lower()
            desc_lower = (repo['description'] or '').lower()
            topics = [t.lower() for t in repo['topics']]
            
            # Categorization logic for OpenCog
            if any(keyword in name_lower for keyword in ['atomspace', 'atom-space']):
                categories['atomspace'].append(repo)
            elif 'hyperon' in name_lower or 'hyperon' in desc_lower or 'hyperon' in topics:
                categories['hyperon'].append(repo)
            elif repo['archived'] or any(keyword in desc_lower for keyword in ['obsolete', 'deprecated', 'abandoned']):
                categories['fossils'].append(repo)
            elif any(keyword in topics for keyword in ['research', 'experimental']):
                categories['research'].append(repo)
            else:
                categories['incubator'].append(repo)
                
    elif org_name.lower() == 'elizaos':
        categories = {
            'core': [],
            'plugins': [],
            'clients': [],
            'tools': [],
            'documentation': []
        }
        
        for repo in repos:
            name_lower = repo['name'].lower()
            desc_lower = (repo['description'] or '').lower()
            topics = [t.lower() for t in repo['topics']]
            
            # Categorization logic for ElizaOS
            if any(keyword in name_lower for keyword in ['core', 'engine', 'framework']):
                categories['core'].append(repo)
            elif any(keyword in name_lower for keyword in ['plugin', 'adapter', 'connector']):
                categories['plugins'].append(repo)
            elif any(keyword in name_lower for keyword in ['client', 'ui', 'interface']):
                categories['clients'].append(repo)
            elif any(keyword in name_lower for keyword in ['tool', 'cli', 'util']):
                categories['tools'].append(repo)
            elif any(keyword in name_lower for keyword in ['doc', 'guide', 'example']):
                categories['documentation'].append(repo)
            else:
                categories['core'].append(repo)  # Default to core
    
    else:
        categories = {'uncategorized': repos}
    
    return categories

def save_repository_data(org_name: str, categorized_repos: Dict[str, List[Dict[str, Any]]]):
    """Save repository data to JSON files"""
    os.makedirs('data/repositories', exist_ok=True)
    
    # Save full data
    filename = f'data/repositories/{org_name.lower()}_repos.json'
    with open(filename, 'w') as f:
        json.dump({
            'organization': org_name,
            'discovered_at': datetime.now().isoformat(),
            'categories': categorized_repos,
            'total_repos': sum(len(repos) for repos in categorized_repos.values())
        }, f, indent=2)
    
    print(f"Saved repository data to {filename}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python discover_repos.py <organization_name>")
        sys.exit(1)
    
    org_name = sys.argv[1]
    github_token = os.environ.get('GITHUB_TOKEN')
    
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    print(f"Starting repository discovery for {org_name}...")
    
    repos = discover_organization_repos(org_name, github_token)
    if not repos:
        print(f"No repositories found for {org_name}")
        sys.exit(1)
    
    categorized_repos = categorize_repos(repos, org_name)
    save_repository_data(org_name, categorized_repos)
    
    print(f"\nDiscovery complete for {org_name}:")
    for category, repo_list in categorized_repos.items():
        print(f"  {category}: {len(repo_list)} repositories")

if __name__ == '__main__':
    main()