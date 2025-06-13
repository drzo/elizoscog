#!/usr/bin/env python3
"""
Repository Discovery and Analysis System

This script discovers all repositories in the OpenCog and ElizaOS organizations,
analyzes their features, and generates comprehensive documentation and integration
checklists for the hybrid cognitive-financial system.
"""

import os
import json
import requests
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
import re

class RepositoryDiscovery:
    """Discovers and analyzes repositories from GitHub organizations"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.session = requests.Session()
        if self.github_token:
            self.session.headers.update({'Authorization': f'token {self.github_token}'})
        
        self.base_dir = Path('/home/runner/work/elizoscog/elizoscog')
        self.docs_dir = self.base_dir / 'docs' / 'integration'
        self.checklists_dir = self.docs_dir / 'checklists'
        self.bridges_dir = self.base_dir / 'src' / 'bridges'
        
        # Ensure directories exist
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.checklists_dir.mkdir(parents=True, exist_ok=True)
        self.bridges_dir.mkdir(parents=True, exist_ok=True)

    def discover_organization_repos(self, org_name: str) -> List[Dict]:
        """Discover all repositories in a GitHub organization"""
        repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f"https://api.github.com/orgs/{org_name}/repos"
            params = {
                'per_page': per_page,
                'page': page,
                'type': 'all',
                'sort': 'updated'
            }
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                page_repos = response.json()
                
                if not page_repos:
                    break
                    
                repos.extend(page_repos)
                page += 1
                
            except requests.RequestException as e:
                print(f"Error fetching repos for {org_name}: {e}")
                break
        
        return repos

    def analyze_repository_languages(self, repo: Dict) -> Dict[str, int]:
        """Analyze programming languages used in a repository"""
        try:
            url = f"https://api.github.com/repos/{repo['full_name']}/languages"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {}

    def analyze_repository_structure(self, repo: Dict) -> Dict:
        """Analyze repository structure and key files"""
        structure = {
            'has_readme': False,
            'has_license': False,
            'has_dockerfile': False,
            'has_setup': False,
            'has_package_json': False,
            'has_requirements': False,
            'has_cargo_toml': False,
            'has_cmake': False,
            'has_makefile': False,
            'has_ci': False,
            'key_files': []
        }
        
        try:
            url = f"https://api.github.com/repos/{repo['full_name']}/contents"
            response = self.session.get(url)
            response.raise_for_status()
            contents = response.json()
            
            for item in contents:
                name = item['name'].lower()
                structure['key_files'].append(item['name'])
                
                if name.startswith('readme'):
                    structure['has_readme'] = True
                elif name in ['license', 'license.txt', 'license.md']:
                    structure['has_license'] = True
                elif name == 'dockerfile':
                    structure['has_dockerfile'] = True
                elif name in ['setup.py', 'setup.cfg']:
                    structure['has_setup'] = True
                elif name == 'package.json':
                    structure['has_package_json'] = True
                elif name in ['requirements.txt', 'requirements.yml']:
                    structure['has_requirements'] = True
                elif name == 'cargo.toml':
                    structure['has_cargo_toml'] = True
                elif name in ['cmakelists.txt', 'cmake']:
                    structure['has_cmake'] = True
                elif name in ['makefile', 'makefile.am']:
                    structure['has_makefile'] = True
                elif name in ['.github', '.gitlab-ci.yml', '.travis.yml']:
                    structure['has_ci'] = True
                    
        except requests.RequestException:
            pass
            
        return structure

    def extract_repository_features(self, repo: Dict) -> Dict:
        """Extract comprehensive features from a repository"""
        features = {
            'basic_info': {
                'name': repo['name'],
                'full_name': repo['full_name'],
                'description': repo.get('description', ''),
                'url': repo['html_url'],
                'clone_url': repo['clone_url'],
                'created_at': repo['created_at'],
                'updated_at': repo['updated_at'],
                'stargazers_count': repo['stargazers_count'],
                'forks_count': repo['forks_count'],
                'size': repo['size'],
                'default_branch': repo['default_branch'],
                'topics': repo.get('topics', []),
                'archived': repo['archived'],
                'disabled': repo['disabled'],
                'private': repo['private']
            },
            'languages': self.analyze_repository_languages(repo),
            'structure': self.analyze_repository_structure(repo),
            'integration_potential': {
                'elizaos_compatibility': self._assess_elizaos_compatibility(repo),
                'opencog_compatibility': self._assess_opencog_compatibility(repo),
                'gnucash_compatibility': self._assess_gnucash_compatibility(repo)
            }
        }
        
        return features

    def _assess_elizaos_compatibility(self, repo: Dict) -> Dict:
        """Assess compatibility with ElizaOS ecosystem"""
        compatibility = {
            'score': 0,
            'reasons': [],
            'integration_type': 'unknown'
        }
        
        name = repo['name'].lower()
        description = (repo.get('description') or '').lower()
        topics = [t.lower() for t in repo.get('topics', [])]
        
        # High compatibility indicators
        if any(keyword in name for keyword in ['agent', 'plugin', 'client', 'action']):
            compatibility['score'] += 30
            compatibility['reasons'].append('Agent/plugin architecture')
            compatibility['integration_type'] = 'direct_plugin'
            
        if any(keyword in description for keyword in ['ai', 'agent', 'bot', 'llm', 'gpt']):
            compatibility['score'] += 20
            compatibility['reasons'].append('AI/agent related functionality')
            
        if any(topic in topics for topic in ['ai', 'agents', 'chatbot', 'llm', 'nodejs', 'typescript']):
            compatibility['score'] += 15
            compatibility['reasons'].append('Relevant topics/technologies')
            
        # Language compatibility
        languages = self.analyze_repository_languages(repo)
        if 'TypeScript' in languages or 'JavaScript' in languages:
            compatibility['score'] += 25
            compatibility['reasons'].append('JavaScript/TypeScript compatibility')
            compatibility['integration_type'] = 'direct_integration'
        elif 'Python' in languages:
            compatibility['score'] += 20
            compatibility['reasons'].append('Python compatibility via bridges')
            compatibility['integration_type'] = 'bridge_integration'
            
        return compatibility

    def _assess_opencog_compatibility(self, repo: Dict) -> Dict:
        """Assess compatibility with OpenCog ecosystem"""
        compatibility = {
            'score': 0,
            'reasons': [],
            'integration_type': 'unknown'
        }
        
        name = repo['name'].lower()
        description = (repo.get('description') or '').lower()
        topics = [t.lower() for t in repo.get('topics', [])]
        
        # High compatibility indicators
        if any(keyword in name for keyword in ['atomspace', 'atom', 'cognitive', 'reasoning', 'pln']):
            compatibility['score'] += 40
            compatibility['reasons'].append('Core cognitive architecture')
            compatibility['integration_type'] = 'core_component'
            
        if any(keyword in description for keyword in ['cognitive', 'reasoning', 'knowledge', 'atomspace']):
            compatibility['score'] += 25
            compatibility['reasons'].append('Cognitive/reasoning functionality')
            
        # Language compatibility
        languages = self.analyze_repository_languages(repo)
        if 'Scheme' in languages or 'C++' in languages:
            compatibility['score'] += 30
            compatibility['reasons'].append('Native Scheme/C++ compatibility')
            compatibility['integration_type'] = 'direct_integration'
        elif 'Python' in languages:
            compatibility['score'] += 20
            compatibility['reasons'].append('Python binding compatibility')
            compatibility['integration_type'] = 'binding_integration'
            
        return compatibility

    def _assess_gnucash_compatibility(self, repo: Dict) -> Dict:
        """Assess compatibility with GnuCash ecosystem"""
        compatibility = {
            'score': 0,
            'reasons': [],
            'integration_type': 'unknown'
        }
        
        name = repo['name'].lower()
        description = (repo.get('description') or '').lower()
        
        # Financial-related keywords
        financial_keywords = ['financial', 'accounting', 'money', 'transaction', 'budget', 'bank']
        if any(keyword in name or keyword in description for keyword in financial_keywords):
            compatibility['score'] += 25
            compatibility['reasons'].append('Financial domain relevance')
            compatibility['integration_type'] = 'domain_integration'
            
        return compatibility

    def generate_checklist_for_repo(self, repo_features: Dict) -> Dict:
        """Generate integration checklist for a repository"""
        basic = repo_features['basic_info']
        languages = repo_features['languages']
        structure = repo_features['structure']
        integration = repo_features['integration_potential']
        
        checklist = {
            'repository': basic['name'],
            'description': basic['description'],
            'priority': self._calculate_priority(repo_features),
            'elizaos_integration': {
                'assessment': integration['elizaos_compatibility'],
                'tasks': self._generate_elizaos_tasks(repo_features)
            },
            'opencog_integration': {
                'assessment': integration['opencog_compatibility'],
                'tasks': self._generate_opencog_tasks(repo_features)
            },
            'gnucash_integration': {
                'assessment': integration['gnucash_compatibility'],
                'tasks': self._generate_gnucash_tasks(repo_features)
            },
            'bridge_requirements': self._generate_bridge_requirements(repo_features)
        }
        
        return checklist

    def _calculate_priority(self, repo_features: Dict) -> str:
        """Calculate integration priority for a repository"""
        basic = repo_features['basic_info']
        integration = repo_features['integration_potential']
        
        total_score = (
            integration['elizaos_compatibility']['score'] +
            integration['opencog_compatibility']['score'] +
            integration['gnucash_compatibility']['score']
        )
        
        # Factor in repository activity
        if basic['stargazers_count'] > 100:
            total_score += 10
        if basic['forks_count'] > 50:
            total_score += 5
        if not basic['archived']:
            total_score += 15
            
        if total_score >= 80:
            return 'high'
        elif total_score >= 40:
            return 'medium'
        else:
            return 'low'

    def _generate_elizaos_tasks(self, repo_features: Dict) -> List[str]:
        """Generate ElizaOS integration tasks"""
        tasks = []
        basic = repo_features['basic_info']
        languages = repo_features['languages']
        compat = repo_features['integration_potential']['elizaos_compatibility']
        
        if compat['score'] > 30:
            if 'TypeScript' in languages or 'JavaScript' in languages:
                tasks.extend([
                    f"Create ElizaOS plugin wrapper for {basic['name']}",
                    "Implement agent action interfaces",
                    "Add TypeScript type definitions",
                    "Create integration tests"
                ])
            elif 'Python' in languages:
                tasks.extend([
                    f"Create Python-to-ElizaOS bridge for {basic['name']}",
                    "Implement agent subprocess communication",
                    "Add error handling and monitoring",
                    "Create bridge documentation"
                ])
            else:
                tasks.append(f"Assess feasibility of {basic['name']} integration")
                
        return tasks

    def _generate_opencog_tasks(self, repo_features: Dict) -> List[str]:
        """Generate OpenCog integration tasks"""
        tasks = []
        basic = repo_features['basic_info']
        languages = repo_features['languages']
        compat = repo_features['integration_potential']['opencog_compatibility']
        
        if compat['score'] > 30:
            if 'Scheme' in languages or 'C++' in languages:
                tasks.extend([
                    f"Create AtomSpace bindings for {basic['name']}",
                    "Implement hypergraph representation",
                    "Add PLN reasoning support",
                    "Create CogServer integration"
                ])
            elif 'Python' in languages:
                tasks.extend([
                    f"Create Python-AtomSpace bridge for {basic['name']}",
                    "Implement Atomese query interface",
                    "Add pattern matching support",
                    "Create cognitive documentation"
                ])
                
        return tasks

    def _generate_gnucash_tasks(self, repo_features: Dict) -> List[str]:
        """Generate GnuCash integration tasks"""
        tasks = []
        basic = repo_features['basic_info']
        compat = repo_features['integration_potential']['gnucash_compatibility']
        
        if compat['score'] > 15:
            tasks.extend([
                f"Create financial data adapter for {basic['name']}",
                "Implement account structure mapping",
                "Add transaction processing support",
                "Create financial intelligence layer"
            ])
            
        return tasks

    def _generate_bridge_requirements(self, repo_features: Dict) -> Dict:
        """Generate bridge implementation requirements"""
        requirements = {
            'data_formats': [],
            'communication_protocols': [],
            'api_interfaces': [],
            'integration_patterns': []
        }
        
        languages = repo_features['languages']
        structure = repo_features['structure']
        
        # Determine data formats
        if 'JSON' in str(structure) or structure['has_package_json']:
            requirements['data_formats'].append('JSON')
        if 'Python' in languages:
            requirements['data_formats'].append('Python objects')
        if 'Scheme' in languages:
            requirements['data_formats'].append('S-expressions')
            
        # Communication protocols
        if structure['has_dockerfile']:
            requirements['communication_protocols'].append('HTTP/REST')
        if 'C++' in languages:
            requirements['communication_protocols'].append('Native bindings')
        if 'Python' in languages:
            requirements['communication_protocols'].append('Python subprocess')
            
        return requirements

    def generate_ecosystem_analysis(self, org_name: str) -> Dict:
        """Generate comprehensive analysis of an organization's ecosystem"""
        print(f"Discovering repositories for {org_name}...")
        repos = self.discover_organization_repos(org_name)
        
        analysis = {
            'organization': org_name,
            'total_repositories': len(repos),
            'generated_at': datetime.now().isoformat(),
            'repositories': {},
            'summary': {
                'by_language': {},
                'by_priority': {'high': 0, 'medium': 0, 'low': 0},
                'integration_candidates': {
                    'elizaos': [],
                    'opencog': [],
                    'gnucash': []
                }
            }
        }
        
        for repo in repos:
            print(f"Analyzing {repo['name']}...")
            features = self.extract_repository_features(repo)
            checklist = self.generate_checklist_for_repo(features)
            
            repo_name = repo['name']
            analysis['repositories'][repo_name] = {
                'features': features,
                'checklist': checklist
            }
            
            # Update summary statistics
            for lang in features['languages']:
                if lang not in analysis['summary']['by_language']:
                    analysis['summary']['by_language'][lang] = 0
                analysis['summary']['by_language'][lang] += 1
                
            priority = checklist['priority']
            analysis['summary']['by_priority'][priority] += 1
            
            # Track integration candidates
            if checklist['elizaos_integration']['assessment']['score'] > 30:
                analysis['summary']['integration_candidates']['elizaos'].append(repo_name)
            if checklist['opencog_integration']['assessment']['score'] > 30:
                analysis['summary']['integration_candidates']['opencog'].append(repo_name)
            if checklist['gnucash_integration']['assessment']['score'] > 15:
                analysis['summary']['integration_candidates']['gnucash'].append(repo_name)
        
        return analysis

    def save_analysis(self, analysis: Dict, filename: str):
        """Save analysis to JSON file"""
        filepath = self.docs_dir / f"{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"Analysis saved to {filepath}")

    def generate_markdown_documentation(self, analysis: Dict) -> str:
        """Generate markdown documentation from analysis"""
        org_name = analysis['organization']
        summary = analysis['summary']
        
        md = f"""# {org_name} Repository Analysis

Generated on: {analysis['generated_at']}

## Summary Statistics

- **Total Repositories**: {analysis['total_repositories']}
- **High Priority**: {summary['by_priority']['high']} repositories
- **Medium Priority**: {summary['by_priority']['medium']} repositories  
- **Low Priority**: {summary['by_priority']['low']} repositories

### Language Distribution
"""
        
        for lang, count in sorted(summary['by_language'].items(), key=lambda x: x[1], reverse=True):
            md += f"- **{lang}**: {count} repositories\n"
            
        md += f"""

### Integration Candidates

#### ElizaOS Compatible ({len(summary['integration_candidates']['elizaos'])} repositories)
"""
        for repo in summary['integration_candidates']['elizaos']:
            md += f"- [{repo}](#{repo.lower().replace('-', '')})\n"
            
        md += f"""

#### OpenCog Compatible ({len(summary['integration_candidates']['opencog'])} repositories)
"""
        for repo in summary['integration_candidates']['opencog']:
            md += f"- [{repo}](#{repo.lower().replace('-', '')})\n"
            
        md += f"""

#### GnuCash Compatible ({len(summary['integration_candidates']['gnucash'])} repositories)
"""
        for repo in summary['integration_candidates']['gnucash']:
            md += f"- [{repo}](#{repo.lower().replace('-', '')})\n"
            
        md += "\n## Repository Details\n\n"
        
        # Add detailed repository information
        for repo_name, repo_data in analysis['repositories'].items():
            features = repo_data['features']
            checklist = repo_data['checklist']
            basic = features['basic_info']
            
            md += f"""### {repo_name}

**Description**: {basic['description']}  
**URL**: {basic['url']}  
**Priority**: {checklist['priority'].title()}  
**Stars**: {basic['stargazers_count']} | **Forks**: {basic['forks_count']}

#### Languages
"""
            for lang, bytes_count in features['languages'].items():
                md += f"- {lang}\n"
                
            md += "\n#### Integration Assessment\n\n"
            
            # ElizaOS integration
            elizaos = checklist['elizaos_integration']['assessment']
            if elizaos['score'] > 0:
                md += f"**ElizaOS Compatibility**: {elizaos['score']}/100\n"
                for reason in elizaos['reasons']:
                    md += f"- {reason}\n"
                    
            # OpenCog integration  
            opencog = checklist['opencog_integration']['assessment']
            if opencog['score'] > 0:
                md += f"\n**OpenCog Compatibility**: {opencog['score']}/100\n"
                for reason in opencog['reasons']:
                    md += f"- {reason}\n"
                    
            # GnuCash integration
            gnucash = checklist['gnucash_integration']['assessment']
            if gnucash['score'] > 0:
                md += f"\n**GnuCash Compatibility**: {gnucash['score']}/100\n"
                for reason in gnucash['reasons']:
                    md += f"- {reason}\n"
                    
            md += "\n#### Integration Tasks\n\n"
            
            all_tasks = (
                checklist['elizaos_integration']['tasks'] +
                checklist['opencog_integration']['tasks'] +
                checklist['gnucash_integration']['tasks']
            )
            
            for task in all_tasks:
                md += f"- [ ] {task}\n"
                
            md += "\n---\n\n"
            
        return md

def main():
    """Main execution function"""
    discovery = RepositoryDiscovery()
    
    # Analyze OpenCog organization
    print("=== Analyzing OpenCog Organization ===")
    opencog_analysis = discovery.generate_ecosystem_analysis('opencog')
    discovery.save_analysis(opencog_analysis, 'opencog_analysis')
    
    # Generate OpenCog documentation
    opencog_md = discovery.generate_markdown_documentation(opencog_analysis)
    with open(discovery.docs_dir / 'opencog_repositories.md', 'w') as f:
        f.write(opencog_md)
    
    # Analyze ElizaOS organization
    print("\n=== Analyzing ElizaOS Organization ===")
    elizaos_analysis = discovery.generate_ecosystem_analysis('elizaOS')
    discovery.save_analysis(elizaos_analysis, 'elizaos_analysis')
    
    # Generate ElizaOS documentation
    elizaos_md = discovery.generate_markdown_documentation(elizaos_analysis)
    with open(discovery.docs_dir / 'elizaos_repositories.md', 'w') as f:
        f.write(elizaos_md)
    
    print("\n=== Analysis Complete ===")
    print(f"OpenCog: {opencog_analysis['total_repositories']} repositories")
    print(f"ElizaOS: {elizaos_analysis['total_repositories']} repositories")
    print(f"Documentation saved to: {discovery.docs_dir}")

if __name__ == "__main__":
    main()