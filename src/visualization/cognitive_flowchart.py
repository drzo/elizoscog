#!/usr/bin/env python3
"""
Cognitive Flowchart Generator

Generates interactive flowcharts for cognitive reasoning processes,
integration workflows, and multi-agent coordination patterns.
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum


class FlowchartNodeType(Enum):
    """Types of nodes in cognitive flowcharts"""
    START = "start"
    END = "end"
    PROCESS = "process"
    DECISION = "decision"
    DATA = "data"
    AGENT = "agent"
    REASONING = "reasoning"
    INTEGRATION = "integration"


class CognitiveFlowchartGenerator:
    """Generate interactive cognitive reasoning flowcharts"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize flowchart generator with configuration"""
        self.config = config or {
            'layout': 'hierarchical',
            'enable_animation': True,
            'show_metrics': True,
            'interactive': True
        }
        self.nodes = []
        self.edges = []
        self.flowchart_data = {}
        
    def create_integration_flowchart(self) -> Dict:
        """Create flowchart for OpenCog-ElizaOS-GnuCash integration"""
        # Define integration workflow nodes
        nodes = [
            {
                "id": "start",
                "type": FlowchartNodeType.START.value,
                "label": "Integration Request",
                "position": {"x": 400, "y": 50},
                "description": "User initiates integration workflow"
            },
            {
                "id": "analyze_request",
                "type": FlowchartNodeType.REASONING.value,
                "label": "Analyze Request",
                "position": {"x": 400, "y": 150},
                "description": "OpenCog PLN analyzes integration requirements"
            },
            {
                "id": "check_compatibility",
                "type": FlowchartNodeType.DECISION.value,
                "label": "Compatible?",
                "position": {"x": 400, "y": 250},
                "description": "Check component compatibility"
            },
            {
                "id": "elizaos_agent",
                "type": FlowchartNodeType.AGENT.value,
                "label": "ElizaOS Agent",
                "position": {"x": 200, "y": 350},
                "description": "Create ElizaOS bridge agent"
            },
            {
                "id": "opencog_subsystem",
                "type": FlowchartNodeType.INTEGRATION.value,
                "label": "OpenCog Subsystem",
                "position": {"x": 400, "y": 350},
                "description": "Initialize OpenCog subsystem"
            },
            {
                "id": "gnucash_bridge",
                "type": FlowchartNodeType.DATA.value,
                "label": "GnuCash Bridge",
                "position": {"x": 600, "y": 350},
                "description": "Connect to GnuCash financial data"
            },
            {
                "id": "cognitive_coordination",
                "type": FlowchartNodeType.REASONING.value,
                "label": "Cognitive Coordination",
                "position": {"x": 400, "y": 450},
                "description": "Multi-agent cognitive coordination"
            },
            {
                "id": "validate_integration",
                "type": FlowchartNodeType.PROCESS.value,
                "label": "Validate Integration",
                "position": {"x": 400, "y": 550},
                "description": "Test integrated system functionality"
            },
            {
                "id": "success",
                "type": FlowchartNodeType.END.value,
                "label": "Integration Complete",
                "position": {"x": 300, "y": 650},
                "description": "Successful integration achieved"
            },
            {
                "id": "failure",
                "type": FlowchartNodeType.END.value,
                "label": "Integration Failed",
                "position": {"x": 500, "y": 650},
                "description": "Integration unsuccessful"
            }
        ]
        
        # Define workflow edges
        edges = [
            {"source": "start", "target": "analyze_request", "label": "Initialize"},
            {"source": "analyze_request", "target": "check_compatibility", "label": "Analysis Complete"},
            {"source": "check_compatibility", "target": "elizaos_agent", "label": "Yes - ElizaOS"},
            {"source": "check_compatibility", "target": "opencog_subsystem", "label": "Yes - OpenCog"},
            {"source": "check_compatibility", "target": "gnucash_bridge", "label": "Yes - GnuCash"},
            {"source": "check_compatibility", "target": "failure", "label": "No - Incompatible"},
            {"source": "elizaos_agent", "target": "cognitive_coordination", "label": "Agent Ready"},
            {"source": "opencog_subsystem", "target": "cognitive_coordination", "label": "Subsystem Ready"},
            {"source": "gnucash_bridge", "target": "cognitive_coordination", "label": "Bridge Ready"},
            {"source": "cognitive_coordination", "target": "validate_integration", "label": "Coordinate"},
            {"source": "validate_integration", "target": "success", "label": "Valid"},
            {"source": "validate_integration", "target": "failure", "label": "Invalid"}
        ]
        
        self.nodes = nodes
        self.edges = edges
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "title": "OpenCog-ElizaOS-GnuCash Integration Workflow",
                "description": "Cognitive integration flowchart for hybrid financial intelligence",
                "created_at": datetime.now().isoformat(),
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
        }
    
    def create_financial_reasoning_flowchart(self) -> Dict:
        """Create flowchart for financial reasoning processes"""
        nodes = [
            {
                "id": "financial_data",
                "type": FlowchartNodeType.DATA.value,
                "label": "GnuCash Data",
                "position": {"x": 400, "y": 50},
                "description": "Financial transaction data input"
            },
            {
                "id": "data_preprocessing",
                "type": FlowchartNodeType.PROCESS.value,
                "label": "Data Preprocessing",
                "position": {"x": 400, "y": 150},
                "description": "Clean and normalize financial data"
            },
            {
                "id": "pattern_recognition",
                "type": FlowchartNodeType.REASONING.value,
                "label": "Pattern Recognition",
                "position": {"x": 200, "y": 250},
                "description": "OpenCog pattern mining"
            },
            {
                "id": "trend_analysis",
                "type": FlowchartNodeType.REASONING.value,
                "label": "Trend Analysis",
                "position": {"x": 400, "y": 250},
                "description": "PLN-based trend inference"
            },
            {
                "id": "anomaly_detection",
                "type": FlowchartNodeType.REASONING.value,
                "label": "Anomaly Detection",
                "position": {"x": 600, "y": 250},
                "description": "Identify unusual patterns"
            },
            {
                "id": "risk_assessment",
                "type": FlowchartNodeType.DECISION.value,
                "label": "Risk Level?",
                "position": {"x": 400, "y": 350},
                "description": "Assess financial risk level"
            },
            {
                "id": "low_risk_action",
                "type": FlowchartNodeType.AGENT.value,
                "label": "Conservative Action",
                "position": {"x": 200, "y": 450},
                "description": "ElizaOS conservative agent"
            },
            {
                "id": "high_risk_action",
                "type": FlowchartNodeType.AGENT.value,
                "label": "Alert & Review",
                "position": {"x": 600, "y": 450},
                "description": "ElizaOS alert agent"
            },
            {
                "id": "generate_insights",
                "type": FlowchartNodeType.PROCESS.value,
                "label": "Generate Insights",
                "position": {"x": 400, "y": 550},
                "description": "Create actionable financial insights"
            },
            {
                "id": "user_interface",
                "type": FlowchartNodeType.END.value,
                "label": "Present to User",
                "position": {"x": 400, "y": 650},
                "description": "Display insights via ElizaOS interface"
            }
        ]
        
        edges = [
            {"source": "financial_data", "target": "data_preprocessing", "label": "Raw Data"},
            {"source": "data_preprocessing", "target": "pattern_recognition", "label": "Patterns"},
            {"source": "data_preprocessing", "target": "trend_analysis", "label": "Trends"},
            {"source": "data_preprocessing", "target": "anomaly_detection", "label": "Anomalies"},
            {"source": "pattern_recognition", "target": "risk_assessment", "label": "Pattern Results"},
            {"source": "trend_analysis", "target": "risk_assessment", "label": "Trend Results"},
            {"source": "anomaly_detection", "target": "risk_assessment", "label": "Anomaly Results"},
            {"source": "risk_assessment", "target": "low_risk_action", "label": "Low Risk"},
            {"source": "risk_assessment", "target": "high_risk_action", "label": "High Risk"},
            {"source": "low_risk_action", "target": "generate_insights", "label": "Conservative"},
            {"source": "high_risk_action", "target": "generate_insights", "label": "Alert"},
            {"source": "generate_insights", "target": "user_interface", "label": "Insights"}
        ]
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "title": "Cognitive Financial Reasoning Flow",
                "description": "AI-driven financial analysis and decision-making process",
                "created_at": datetime.now().isoformat(),
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
        }
    
    def generate_html_flowchart(self, flowchart_data: Dict) -> str:
        """Generate interactive HTML flowchart visualization"""
        
        html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0a0a; color: white; }}
        #flowchart {{ width: 100vw; height: 100vh; }}
        .info-panel {{ position: absolute; top: 20px; left: 20px; background: rgba(0,0,0,0.9); padding: 20px; border-radius: 10px; border: 1px solid #333; }}
        .node {{ cursor: pointer; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3)); }}
        .node-start {{ fill: #4CAF50; }}
        .node-end {{ fill: #F44336; }}
        .node-process {{ fill: #2196F3; }}
        .node-decision {{ fill: #FF9800; }}
        .node-data {{ fill: #9C27B0; }}
        .node-agent {{ fill: #00BCD4; }}
        .node-reasoning {{ fill: #3F51B5; }}
        .node-integration {{ fill: #607D8B; }}
        .edge {{ stroke: #666; stroke-width: 2px; fill: none; marker-end: url(#arrowhead); }}
        .edge-label {{ fill: white; font-size: 12px; text-anchor: middle; }}
        .node-label {{ fill: white; font-size: 14px; font-weight: bold; text-anchor: middle; }}
        .tooltip {{ position: absolute; background: rgba(0,0,0,0.9); color: white; padding: 15px; border-radius: 8px; pointer-events: none; border: 1px solid #333; }}
    </style>
</head>
<body>
    <div id="flowchart"></div>
    <div class="info-panel">
        <h3>{title}</h3>
        <p>{description}</p>
        <p>Nodes: <span id="node-count">{node_count}</span></p>
        <p>Edges: <span id="edge-count">{edge_count}</span></p>
        <p>Generated: {timestamp}</p>
    </div>
    
    <script>
        const data = {flowchart_json};
        
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select("#flowchart")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        // Define arrow marker
        svg.append("defs").append("marker")
            .attr("id", "arrowhead")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 8)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#666");
        
        // Create edges
        const edges = svg.append("g")
            .selectAll("path")
            .data(data.edges)
            .enter().append("path")
            .attr("class", "edge")
            .attr("d", d => {{
                const sourceNode = data.nodes.find(n => n.id === d.source);
                const targetNode = data.nodes.find(n => n.id === d.target);
                return `M${{sourceNode.position.x}},${{sourceNode.position.y}} L${{targetNode.position.x}},${{targetNode.position.y}}`;
            }});
        
        // Create edge labels
        const edgeLabels = svg.append("g")
            .selectAll("text")
            .data(data.edges)
            .enter().append("text")
            .attr("class", "edge-label")
            .attr("x", d => {{
                const sourceNode = data.nodes.find(n => n.id === d.source);
                const targetNode = data.nodes.find(n => n.id === d.target);
                return (sourceNode.position.x + targetNode.position.x) / 2;
            }})
            .attr("y", d => {{
                const sourceNode = data.nodes.find(n => n.id === d.source);
                const targetNode = data.nodes.find(n => n.id === d.target);
                return (sourceNode.position.y + targetNode.position.y) / 2 - 5;
            }})
            .text(d => d.label);
        
        // Create nodes
        const nodes = svg.append("g")
            .selectAll("g")
            .data(data.nodes)
            .enter().append("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${{d.position.x}},${{d.position.y}})`);
        
        // Add node shapes based on type
        nodes.each(function(d) {{
            const nodeGroup = d3.select(this);
            
            switch(d.type) {{
                case 'start':
                case 'end':
                    nodeGroup.append("circle")
                        .attr("r", 30)
                        .attr("class", `node-${{d.type}}`);
                    break;
                case 'decision':
                    nodeGroup.append("polygon")
                        .attr("points", "0,-30 40,0 0,30 -40,0")
                        .attr("class", `node-${{d.type}}`);
                    break;
                default:
                    nodeGroup.append("rect")
                        .attr("x", -50)
                        .attr("y", -20)
                        .attr("width", 100)
                        .attr("height", 40)
                        .attr("rx", 8)
                        .attr("class", `node-${{d.type}}`);
            }}
        }});
        
        // Add node labels
        nodes.append("text")
            .attr("class", "node-label")
            .attr("dy", "0.35em")
            .text(d => d.label)
            .each(function(d) {{
                const text = d3.select(this);
                const words = d.label.split(' ');
                if (words.length > 2) {{
                    text.text('');
                    text.append('tspan').attr('x', 0).attr('dy', '-0.2em').text(words.slice(0, 2).join(' '));
                    text.append('tspan').attr('x', 0).attr('dy', '1.2em').text(words.slice(2).join(' '));
                }}
            }});
        
        // Add tooltips
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);
        
        nodes.on("mouseover", function(event, d) {{
            tooltip.transition().duration(200).style("opacity", .9);
            tooltip.html(`
                <strong>${{d.label}}</strong><br/>
                Type: ${{d.type}}<br/>
                ${{d.description}}
            `)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 28) + "px");
        }})
        .on("mouseout", function(d) {{
            tooltip.transition().duration(500).style("opacity", 0);
        }});
        
        // Add click interactions
        nodes.on("click", function(event, d) {{
            console.log("Node clicked:", d);
            // Add custom interaction logic here
        }});
        
        // Add zoom and pan
        const zoom = d3.zoom()
            .scaleExtent([0.1, 3])
            .on("zoom", function(event) {{
                svg.selectAll("g").attr("transform", event.transform);
            }});
        
        svg.call(zoom);
    </script>
</body>
</html>'''.format(
            title=flowchart_data['metadata']['title'],
            description=flowchart_data['metadata']['description'],
            node_count=flowchart_data['metadata']['node_count'],
            edge_count=flowchart_data['metadata']['edge_count'],
            timestamp=flowchart_data['metadata']['created_at'],
            flowchart_json=json.dumps(flowchart_data)
        )
        
        return html_template
    
    def save_flowchart(self, flowchart_data: Dict, filename: str) -> bool:
        """Save flowchart visualization to HTML file"""
        try:
            html_content = self.generate_html_flowchart(flowchart_data)
            with open(filename, 'w') as f:
                f.write(html_content)
            print(f"Cognitive flowchart saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving flowchart: {e}")
            return False
    
    def generate_all_flowcharts(self, output_dir: str = ".") -> List[str]:
        """Generate all available flowcharts"""
        flowcharts = [
            ("integration_flowchart.html", self.create_integration_flowchart()),
            ("financial_reasoning_flowchart.html", self.create_financial_reasoning_flowchart())
        ]
        
        saved_files = []
        for filename, flowchart_data in flowcharts:
            filepath = f"{output_dir}/{filename}"
            if self.save_flowchart(flowchart_data, filepath):
                saved_files.append(filepath)
        
        return saved_files


def main():
    """Demo cognitive flowchart generator"""
    print("🧠 Cognitive Flowchart Generator Demo")
    
    generator = CognitiveFlowchartGenerator({
        'layout': 'hierarchical',
        'enable_animation': True,
        'interactive': True
    })
    
    # Generate integration flowchart
    print("🔄 Generating integration flowchart...")
    integration_flow = generator.create_integration_flowchart()
    generator.save_flowchart(integration_flow, "demo_integration_flowchart.html")
    
    # Generate financial reasoning flowchart
    print("💰 Generating financial reasoning flowchart...")
    financial_flow = generator.create_financial_reasoning_flowchart()
    generator.save_flowchart(financial_flow, "demo_financial_flowchart.html")
    
    # Generate all flowcharts
    print("📊 Generating all flowcharts...")
    saved_files = generator.generate_all_flowcharts("./flowcharts")
    
    print(f"✅ Generated {len(saved_files)} flowcharts:")
    for file in saved_files:
        print(f"  - {file}")
    
    print("🎉 Cognitive flowchart generation completed!")


if __name__ == "__main__":
    main()