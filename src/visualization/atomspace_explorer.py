#!/usr/bin/env python3
"""
AtomSpace Explorer - Interactive Hypergraph Visualization

Provides web-based visualization of OpenCog AtomSpace hypergraph structures
with real-time updates and cognitive reasoning flow visualization.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class AtomSpaceExplorer:
    """Interactive AtomSpace hypergraph explorer and visualizer"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize AtomSpace Explorer with configuration"""
        self.config = config or {
            'max_nodes': 1000,
            'layout_algorithm': 'force_directed',
            'update_interval': 100,
            'enable_3d': True
        }
        self.atoms = {}
        self.links = []
        self.visualization_data = {}
        
    def load_atomspace_data(self, atomspace_path: str) -> bool:
        """Load AtomSpace data from file or database"""
        try:
            # Simulate loading AtomSpace data
            self.atoms = {
                f"atom_{i}": {
                    "type": "ConceptNode" if i % 2 == 0 else "PredicateNode",
                    "name": f"concept_{i}",
                    "truth_value": {"strength": 0.8, "confidence": 0.9},
                    "attention_value": {"sti": 100, "lti": 50},
                    "position": {"x": i * 10, "y": (i * 10) % 500, "z": 0}
                }
                for i in range(min(50, self.config['max_nodes']))
            }
            
            # Generate some sample links
            self.links = [
                {
                    "type": "EvaluationLink",
                    "source": f"atom_{i}",
                    "target": f"atom_{(i+1) % len(self.atoms)}",
                    "strength": 0.7
                }
                for i in range(0, len(self.atoms)-1, 2)
            ]
            
            return True
        except Exception as e:
            print(f"Error loading AtomSpace data: {e}")
            return False
    
    def generate_visualization_json(self) -> Dict:
        """Generate JSON data for web visualization"""
        nodes = []
        edges = []
        
        # Convert atoms to visualization nodes
        for atom_id, atom_data in self.atoms.items():
            nodes.append({
                "id": atom_id,
                "label": atom_data["name"],
                "type": atom_data["type"],
                "size": atom_data["attention_value"]["sti"] / 10,
                "color": self._get_node_color(atom_data["type"]),
                "x": atom_data["position"]["x"],
                "y": atom_data["position"]["y"],
                "z": atom_data["position"]["z"] if self.config['enable_3d'] else None,
                "truth_value": atom_data["truth_value"]
            })
        
        # Convert links to visualization edges
        for link in self.links:
            edges.append({
                "source": link["source"],
                "target": link["target"],
                "type": link["type"],
                "weight": link["strength"],
                "color": self._get_edge_color(link["type"])
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_atoms": len(self.atoms),
                "total_links": len(self.links),
                "generated_at": datetime.now().isoformat(),
                "config": self.config
            }
        }
    
    def _get_node_color(self, node_type: str) -> str:
        """Get visualization color for node type"""
        color_map = {
            "ConceptNode": "#4CAF50",
            "PredicateNode": "#2196F3", 
            "NumberNode": "#FF9800",
            "VariableNode": "#9C27B0",
            "SchemaNode": "#F44336"
        }
        return color_map.get(node_type, "#757575")
    
    def _get_edge_color(self, edge_type: str) -> str:
        """Get visualization color for edge type"""
        color_map = {
            "EvaluationLink": "#666666",
            "InheritanceLink": "#4CAF50",
            "SimilarityLink": "#2196F3",
            "MemberLink": "#FF9800"
        }
        return color_map.get(edge_type, "#999999")
    
    def generate_html_visualization(self) -> str:
        """Generate complete HTML visualization page"""
        viz_data = self.generate_visualization_json()
        
        html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AtomSpace Explorer</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ margin: 0; font-family: Arial, sans-serif; background: #1a1a1a; color: white; }}
        #visualization {{ width: 100vw; height: 100vh; }}
        .info-panel {{ position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.8); padding: 15px; border-radius: 5px; }}
        .node {{ cursor: pointer; }}
        .link {{ stroke: #666; stroke-width: 2px; }}
        .tooltip {{ position: absolute; background: rgba(0,0,0,0.9); color: white; padding: 10px; border-radius: 5px; pointer-events: none; }}
    </style>
</head>
<body>
    <div id="visualization"></div>
    <div class="info-panel">
        <h3>AtomSpace Explorer</h3>
        <p>Nodes: <span id="node-count">{node_count}</span></p>
        <p>Links: <span id="link-count">{link_count}</span></p>
        <p>Generated: {timestamp}</p>
    </div>
    
    <script>
        const data = {viz_data_json};
        
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select("#visualization")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.edges).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        const link = svg.append("g")
            .selectAll("line")
            .data(data.edges)
            .enter().append("line")
            .attr("class", "link")
            .attr("stroke", d => d.color)
            .attr("stroke-width", d => d.weight * 3);
        
        const node = svg.append("g")
            .selectAll("circle")
            .data(data.nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", d => d.size)
            .attr("fill", d => d.color)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);
        
        node.on("mouseover", function(event, d) {{
            tooltip.transition().duration(200).style("opacity", .9);
            tooltip.html(`
                <strong>${{d.label}}</strong><br/>
                Type: ${{d.type}}<br/>
                Truth Value: ${{d.truth_value.strength.toFixed(2)}} / ${{d.truth_value.confidence.toFixed(2)}}
            `)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 28) + "px");
        }})
        .on("mouseout", function(d) {{
            tooltip.transition().duration(500).style("opacity", 0);
        }});
        
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>'''.format(
            viz_data_json=json.dumps(viz_data),
            node_count=len(viz_data['nodes']),
            link_count=len(viz_data['edges']),
            timestamp=viz_data['metadata']['generated_at']
        )
        
        return html_template
    
    def save_visualization(self, filename: str = "atomspace_visualization.html") -> bool:
        """Save HTML visualization to file"""
        try:
            html_content = self.generate_html_visualization()
            with open(filename, 'w') as f:
                f.write(html_content)
            print(f"AtomSpace visualization saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving visualization: {e}")
            return False
    
    def get_cognitive_insights(self) -> Dict:
        """Analyze AtomSpace for cognitive insights"""
        insights = {
            "node_type_distribution": {},
            "attention_patterns": [],
            "truth_value_analysis": {},
            "connectivity_metrics": {}
        }
        
        # Analyze node type distribution
        for atom in self.atoms.values():
            node_type = atom["type"]
            insights["node_type_distribution"][node_type] = \
                insights["node_type_distribution"].get(node_type, 0) + 1
        
        # Analyze attention patterns
        high_attention_atoms = [
            atom for atom in self.atoms.values()
            if atom["attention_value"]["sti"] > 150
        ]
        insights["attention_patterns"] = [
            {
                "name": atom["name"],
                "sti": atom["attention_value"]["sti"],
                "type": atom["type"]
            }
            for atom in high_attention_atoms
        ]
        
        # Truth value analysis
        avg_strength = sum(atom["truth_value"]["strength"] for atom in self.atoms.values()) / len(self.atoms)
        avg_confidence = sum(atom["truth_value"]["confidence"] for atom in self.atoms.values()) / len(self.atoms)
        
        insights["truth_value_analysis"] = {
            "average_strength": avg_strength,
            "average_confidence": avg_confidence,
            "high_confidence_count": len([
                atom for atom in self.atoms.values()
                if atom["truth_value"]["confidence"] > 0.8
            ])
        }
        
        # Connectivity metrics
        node_connections = {}
        for link in self.links:
            source = link["source"]
            target = link["target"]
            node_connections[source] = node_connections.get(source, 0) + 1
            node_connections[target] = node_connections.get(target, 0) + 1
        
        insights["connectivity_metrics"] = {
            "total_connections": len(self.links),
            "average_connections": sum(node_connections.values()) / len(node_connections) if node_connections else 0,
            "most_connected_nodes": sorted(
                [(node, count) for node, count in node_connections.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
        
        return insights


def main():
    """Demo AtomSpace Explorer functionality"""
    print("🧠 AtomSpace Explorer Demo")
    
    explorer = AtomSpaceExplorer({
        'max_nodes': 50,
        'enable_3d': True,
        'layout_algorithm': 'force_directed'
    })
    
    # Load sample data
    print("📊 Loading AtomSpace data...")
    explorer.load_atomspace_data("sample_atomspace.scm")
    
    # Generate visualization
    print("🎨 Generating visualization...")
    explorer.save_visualization("demo_atomspace_explorer.html")
    
    # Get cognitive insights
    print("🧠 Analyzing cognitive patterns...")
    insights = explorer.get_cognitive_insights()
    
    print(f"📈 Analysis Results:")
    print(f"  Node Types: {list(insights['node_type_distribution'].keys())}")
    print(f"  High Attention Atoms: {len(insights['attention_patterns'])}")
    print(f"  Average Truth Value: {insights['truth_value_analysis']['average_strength']:.2f}")
    print(f"  Total Connections: {insights['connectivity_metrics']['total_connections']}")
    
    print("✅ AtomSpace Explorer demo completed!")


if __name__ == "__main__":
    main()