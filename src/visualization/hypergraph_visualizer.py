#!/usr/bin/env python3
"""
Hypergraph Visualizer for OpenCog AtomSpace

Advanced 3D visualization of hypergraph structures with cognitive
reasoning patterns and multi-dimensional relationship mapping.
"""

import json
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class HyperedgeNode:
    """Node in a hypergraph structure"""
    id: str
    label: str
    node_type: str
    position: Tuple[float, float, float]
    properties: Dict[str, Any]


@dataclass
class Hyperedge:
    """Hyperedge connecting multiple nodes"""
    id: str
    nodes: List[str]
    edge_type: str
    strength: float
    properties: Dict[str, Any]


class HypergraphVisualizer:
    """3D hypergraph visualization for OpenCog AtomSpace"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize hypergraph visualizer with configuration"""
        self.config = config or {
            'dimensions': 3,
            'layout_algorithm': 'force_directed_3d',
            'enable_physics': True,
            'clustering': True,
            'interactive': True
        }
        self.nodes = []
        self.hyperedges = []
        self.clusters = {}
        
    def create_atomspace_hypergraph(self) -> Dict:
        """Create hypergraph representation of AtomSpace structure"""
        
        # Create sample AtomSpace nodes
        atomspace_nodes = [
            HyperedgeNode(
                id="concept_animal",
                label="Animal",
                node_type="ConceptNode",
                position=(0, 0, 0),
                properties={"truth_value": {"strength": 0.9, "confidence": 0.8}}
            ),
            HyperedgeNode(
                id="concept_dog",
                label="Dog", 
                node_type="ConceptNode",
                position=(100, 0, 0),
                properties={"truth_value": {"strength": 0.95, "confidence": 0.9}}
            ),
            HyperedgeNode(
                id="concept_cat",
                label="Cat",
                node_type="ConceptNode", 
                position=(50, 100, 0),
                properties={"truth_value": {"strength": 0.92, "confidence": 0.85}}
            ),
            HyperedgeNode(
                id="predicate_breathes",
                label="Breathes",
                node_type="PredicateNode",
                position=(0, 50, 100),
                properties={"truth_value": {"strength": 0.99, "confidence": 0.95}}
            ),
            HyperedgeNode(
                id="predicate_walks",
                label="Walks",
                node_type="PredicateNode",
                position=(100, 50, 100),
                properties={"truth_value": {"strength": 0.88, "confidence": 0.80}}
            ),
            HyperedgeNode(
                id="schema_movement",
                label="MovementSchema",
                node_type="SchemaNode",
                position=(50, 0, 150),
                properties={"truth_value": {"strength": 0.75, "confidence": 0.70}}
            )
        ]
        
        # Create hyperedges representing complex relationships
        hyperedges = [
            Hyperedge(
                id="inheritance_1",
                nodes=["concept_dog", "concept_animal"],
                edge_type="InheritanceLink",
                strength=0.9,
                properties={"relationship": "is_a"}
            ),
            Hyperedge(
                id="inheritance_2", 
                nodes=["concept_cat", "concept_animal"],
                edge_type="InheritanceLink",
                strength=0.85,
                properties={"relationship": "is_a"}
            ),
            Hyperedge(
                id="evaluation_1",
                nodes=["predicate_breathes", "concept_animal"],
                edge_type="EvaluationLink",
                strength=0.95,
                properties={"relationship": "capability"}
            ),
            Hyperedge(
                id="complex_relation_1",
                nodes=["concept_dog", "predicate_walks", "schema_movement"],
                edge_type="ExecutionLink",
                strength=0.88,
                properties={"relationship": "behavioral_pattern", "complexity": "high"}
            ),
            Hyperedge(
                id="similarity_1",
                nodes=["concept_dog", "concept_cat"],
                edge_type="SimilarityLink",
                strength=0.75,
                properties={"relationship": "semantic_similarity"}
            ),
            Hyperedge(
                id="implication_1",
                nodes=["concept_animal", "predicate_breathes", "predicate_walks"],
                edge_type="ImplicationLink",
                strength=0.70,
                properties={"relationship": "logical_implication", "complexity": "high"}
            )
        ]
        
        self.nodes = atomspace_nodes
        self.hyperedges = hyperedges
        
        return {
            "nodes": [self._node_to_dict(node) for node in atomspace_nodes],
            "hyperedges": [self._hyperedge_to_dict(edge) for edge in hyperedges],
            "metadata": {
                "total_nodes": len(atomspace_nodes),
                "total_hyperedges": len(hyperedges),
                "dimensions": self.config['dimensions'],
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def create_cognitive_reasoning_hypergraph(self) -> Dict:
        """Create hypergraph showing cognitive reasoning flow"""
        
        reasoning_nodes = [
            HyperedgeNode(
                id="input_observation",
                label="Observation",
                node_type="InputNode",
                position=(0, 0, 0),
                properties={"cognitive_function": "perception", "certainty": 0.8}
            ),
            HyperedgeNode(
                id="pattern_recognition",
                label="Pattern Recognition",
                node_type="ProcessNode",
                position=(150, 0, 50),
                properties={"cognitive_function": "recognition", "accuracy": 0.85}
            ),
            HyperedgeNode(
                id="memory_retrieval",
                label="Memory Retrieval",
                node_type="ProcessNode",
                position=(0, 150, 50),
                properties={"cognitive_function": "memory", "speed": 0.9}
            ),
            HyperedgeNode(
                id="inference_engine",
                label="PLN Inference",
                node_type="ReasoningNode",
                position=(150, 150, 100),
                properties={"cognitive_function": "reasoning", "logic_strength": 0.92}
            ),
            HyperedgeNode(
                id="decision_maker",
                label="Decision Making",
                node_type="DecisionNode",
                position=(75, 75, 150),
                properties={"cognitive_function": "decision", "confidence": 0.78}
            ),
            HyperedgeNode(
                id="action_output",
                label="Action Output",
                node_type="OutputNode",
                position=(75, 0, 200),
                properties={"cognitive_function": "action", "effectiveness": 0.82}
            )
        ]
        
        reasoning_edges = [
            Hyperedge(
                id="perception_to_pattern",
                nodes=["input_observation", "pattern_recognition"],
                edge_type="FlowLink",
                strength=0.9,
                properties={"flow_type": "information", "latency": 0.1}
            ),
            Hyperedge(
                id="perception_to_memory",
                nodes=["input_observation", "memory_retrieval"],
                edge_type="FlowLink",
                strength=0.85,
                properties={"flow_type": "query", "latency": 0.15}
            ),
            Hyperedge(
                id="cognitive_fusion",
                nodes=["pattern_recognition", "memory_retrieval", "inference_engine"],
                edge_type="FusionLink",
                strength=0.88,
                properties={"fusion_type": "cognitive_integration", "complexity": "high"}
            ),
            Hyperedge(
                id="reasoning_to_decision",
                nodes=["inference_engine", "decision_maker"],
                edge_type="FlowLink",
                strength=0.92,
                properties={"flow_type": "reasoning_result", "confidence": 0.87}
            ),
            Hyperedge(
                id="decision_to_action",
                nodes=["decision_maker", "action_output"],
                edge_type="FlowLink",
                strength=0.80,
                properties={"flow_type": "command", "urgency": 0.75}
            ),
            Hyperedge(
                id="feedback_loop",
                nodes=["action_output", "input_observation"],
                edge_type="FeedbackLink",
                strength=0.65,
                properties={"feedback_type": "outcome", "delay": 0.5}
            )
        ]
        
        return {
            "nodes": [self._node_to_dict(node) for node in reasoning_nodes],
            "hyperedges": [self._hyperedge_to_dict(edge) for edge in reasoning_edges],
            "metadata": {
                "total_nodes": len(reasoning_nodes),
                "total_hyperedges": len(reasoning_edges),
                "reasoning_type": "cognitive_flow",
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def apply_force_directed_layout(self, iterations: int = 100) -> None:
        """Apply 3D force-directed layout algorithm"""
        if not self.nodes:
            return
            
        # Physics simulation parameters
        k = 100  # Spring constant
        repulsion = 5000  # Node repulsion strength
        damping = 0.9  # Velocity damping
        
        # Initialize velocities
        velocities = {node.id: [0.0, 0.0, 0.0] for node in self.nodes}
        
        for iteration in range(iterations):
            forces = {node.id: [0.0, 0.0, 0.0] for node in self.nodes}
            
            # Calculate repulsive forces between all nodes
            for i, node1 in enumerate(self.nodes):
                for j, node2 in enumerate(self.nodes[i+1:], i+1):
                    dx = node1.position[0] - node2.position[0]
                    dy = node1.position[1] - node2.position[1]
                    dz = node1.position[2] - node2.position[2]
                    
                    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                    if distance < 1:
                        distance = 1  # Avoid division by zero
                    
                    force_magnitude = repulsion / (distance * distance)
                    
                    fx = (dx / distance) * force_magnitude
                    fy = (dy / distance) * force_magnitude
                    fz = (dz / distance) * force_magnitude
                    
                    forces[node1.id][0] += fx
                    forces[node1.id][1] += fy
                    forces[node1.id][2] += fz
                    
                    forces[node2.id][0] -= fx
                    forces[node2.id][1] -= fy
                    forces[node2.id][2] -= fz
            
            # Calculate attractive forces from hyperedges
            for hyperedge in self.hyperedges:
                if len(hyperedge.nodes) < 2:
                    continue
                    
                # Calculate centroid of connected nodes
                centroid = [0.0, 0.0, 0.0]
                valid_nodes = []
                
                for node_id in hyperedge.nodes:
                    node = next((n for n in self.nodes if n.id == node_id), None)
                    if node:
                        centroid[0] += node.position[0]
                        centroid[1] += node.position[1]
                        centroid[2] += node.position[2]
                        valid_nodes.append(node)
                
                if len(valid_nodes) < 2:
                    continue
                    
                centroid[0] /= len(valid_nodes)
                centroid[1] /= len(valid_nodes)
                centroid[2] /= len(valid_nodes)
                
                # Apply attractive force toward centroid
                for node in valid_nodes:
                    dx = centroid[0] - node.position[0]
                    dy = centroid[1] - node.position[1]
                    dz = centroid[2] - node.position[2]
                    
                    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                    if distance > 0:
                        force_magnitude = k * hyperedge.strength * distance
                        
                        forces[node.id][0] += (dx / distance) * force_magnitude
                        forces[node.id][1] += (dy / distance) * force_magnitude
                        forces[node.id][2] += (dz / distance) * force_magnitude
            
            # Update velocities and positions
            for node in self.nodes:
                velocities[node.id][0] = (velocities[node.id][0] + forces[node.id][0]) * damping
                velocities[node.id][1] = (velocities[node.id][1] + forces[node.id][1]) * damping
                velocities[node.id][2] = (velocities[node.id][2] + forces[node.id][2]) * damping
                
                new_x = node.position[0] + velocities[node.id][0]
                new_y = node.position[1] + velocities[node.id][1]
                new_z = node.position[2] + velocities[node.id][2]
                
                node.position = (new_x, new_y, new_z)
    
    def generate_3d_visualization_html(self, hypergraph_data: Dict) -> str:
        """Generate 3D HTML visualization using Three.js"""
        
        html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Hypergraph Visualization</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/dat-gui/0.7.9/dat.gui.min.js"></script>
    <style>
        body {{ margin: 0; padding: 0; background: #000; color: white; font-family: Arial, sans-serif; overflow: hidden; }}
        #container {{ width: 100vw; height: 100vh; }}
        #info {{ position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.8); padding: 15px; border-radius: 5px; z-index: 100; }}
        #controls {{ position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.8); padding: 15px; border-radius: 5px; z-index: 100; }}
        .node-label {{ color: white; font-size: 12px; }}
        button {{ background: #4CAF50; color: white; border: none; padding: 10px 15px; margin: 5px; border-radius: 5px; cursor: pointer; }}
        button:hover {{ background: #45a049; }}
    </style>
</head>
<body>
    <div id="container"></div>
    <div id="info">
        <h3>🧠 3D Hypergraph Explorer</h3>
        <p>Nodes: <span id="node-count">{node_count}</span></p>
        <p>Hyperedges: <span id="edge-count">{edge_count}</span></p>
        <p>Click nodes for details</p>
    </div>
    <div id="controls">
        <button onclick="resetCamera()">Reset View</button><br>
        <button onclick="togglePhysics()">Toggle Physics</button><br>
        <button onclick="changeLayout()">Change Layout</button><br>
        <button onclick="exportView()">Export View</button>
    </div>
    
    <script>
        const hypergraphData = {hypergraph_json};
        
        // Scene setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setClearColor(0x000011);
        document.getElementById('container').appendChild(renderer.domElement);
        
        // Camera controls (basic mouse interaction)
        let mouseX = 0, mouseY = 0;
        let cameraRadius = 500;
        let cameraTheta = 0;
        let cameraPhi = Math.PI / 2;
        
        // Node and edge storage
        const nodeObjects = {{}};
        const edgeObjects = [];
        const nodeLabels = [];
        
        // Materials
        const materials = {{
            ConceptNode: new THREE.MeshPhongMaterial({{ color: 0x4CAF50 }}),
            PredicateNode: new THREE.MeshPhongMaterial({{ color: 0x2196F3 }}),
            SchemaNode: new THREE.MeshPhongMaterial({{ color: 0xFF9800 }}),
            InputNode: new THREE.MeshPhongMaterial({{ color: 0x9C27B0 }}),
            OutputNode: new THREE.MeshPhongMaterial({{ color: 0xF44336 }}),
            ProcessNode: new THREE.MeshPhongMaterial({{ color: 0x00BCD4 }}),
            ReasoningNode: new THREE.MeshPhongMaterial({{ color: 0x3F51B5 }}),
            DecisionNode: new THREE.MeshPhongMaterial({{ color: 0xFF5722 }}),
            default: new THREE.MeshPhongMaterial({{ color: 0x607D8B }})
        }};
        
        // Create nodes
        hypergraphData.nodes.forEach(nodeData => {{
            const geometry = new THREE.SphereGeometry(10, 16, 16);
            const material = materials[nodeData.node_type] || materials.default;
            const sphere = new THREE.Mesh(geometry, material);
            
            sphere.position.set(nodeData.position[0], nodeData.position[1], nodeData.position[2]);
            sphere.userData = nodeData;
            
            scene.add(sphere);
            nodeObjects[nodeData.id] = sphere;
            
            // Add text label
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = 256;
            canvas.height = 64;
            context.fillStyle = 'white';
            context.font = '24px Arial';
            context.textAlign = 'center';
            context.fillText(nodeData.label, 128, 40);
            
            const texture = new THREE.CanvasTexture(canvas);
            const spriteMaterial = new THREE.SpriteMaterial({{ map: texture }});
            const sprite = new THREE.Sprite(spriteMaterial);
            sprite.position.copy(sphere.position);
            sprite.position.y += 20;
            sprite.scale.set(50, 12.5, 1);
            
            scene.add(sprite);
            nodeLabels.push(sprite);
        }});
        
        // Create hyperedges
        hypergraphData.hyperedges.forEach(edgeData => {{
            if (edgeData.nodes.length === 2) {{
                // Simple edge between two nodes
                const node1 = nodeObjects[edgeData.nodes[0]];
                const node2 = nodeObjects[edgeData.nodes[1]];
                
                if (node1 && node2) {{
                    const geometry = new THREE.BufferGeometry().setFromPoints([
                        node1.position, node2.position
                    ]);
                    const material = new THREE.LineBasicMaterial({{ 
                        color: 0x666666, 
                        opacity: edgeData.strength,
                        transparent: true
                    }});
                    const line = new THREE.Line(geometry, material);
                    scene.add(line);
                    edgeObjects.push(line);
                }}
            }} else if (edgeData.nodes.length > 2) {{
                // Hyperedge - create hub and spokes
                const centerPos = new THREE.Vector3();
                const validNodes = [];
                
                edgeData.nodes.forEach(nodeId => {{
                    const node = nodeObjects[nodeId];
                    if (node) {{
                        centerPos.add(node.position);
                        validNodes.push(node);
                    }}
                }});
                
                if (validNodes.length > 1) {{
                    centerPos.divideScalar(validNodes.length);
                    
                    // Create hub
                    const hubGeometry = new THREE.OctahedronGeometry(5);
                    const hubMaterial = new THREE.MeshPhongMaterial({{ 
                        color: 0xFF6600,
                        opacity: 0.7,
                        transparent: true
                    }});
                    const hub = new THREE.Mesh(hubGeometry, hubMaterial);
                    hub.position.copy(centerPos);
                    scene.add(hub);
                    
                    // Create spokes to each node
                    validNodes.forEach(node => {{
                        const geometry = new THREE.BufferGeometry().setFromPoints([
                            centerPos, node.position
                        ]);
                        const material = new THREE.LineBasicMaterial({{ 
                            color: 0xFF6600,
                            opacity: edgeData.strength * 0.8,
                            transparent: true
                        }});
                        const line = new THREE.Line(geometry, material);
                        scene.add(line);
                        edgeObjects.push(line);
                    }});
                }}
            }}
        }});
        
        // Lighting
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(100, 100, 100);
        scene.add(directionalLight);
        
        // Mouse interaction
        document.addEventListener('mousemove', onMouseMove, false);
        document.addEventListener('wheel', onMouseWheel, false);
        document.addEventListener('click', onMouseClick, false);
        
        function onMouseMove(event) {{
            mouseX = (event.clientX / window.innerWidth) * 2 - 1;
            mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
            
            cameraTheta = mouseX * Math.PI;
            cameraPhi = (mouseY + 1) * Math.PI / 2;
        }}
        
        function onMouseWheel(event) {{
            cameraRadius += event.deltaY * 0.5;
            cameraRadius = Math.max(100, Math.min(2000, cameraRadius));
        }}
        
        function onMouseClick(event) {{
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            
            raycaster.setFromCamera(mouse, camera);
            
            const nodeArray = Object.values(nodeObjects);
            const intersects = raycaster.intersectObjects(nodeArray);
            
            if (intersects.length > 0) {{
                const selectedNode = intersects[0].object;
                console.log('Selected node:', selectedNode.userData);
                alert(`Node: ${{selectedNode.userData.label}}\\nType: ${{selectedNode.userData.node_type}}\\nProperties: ${{JSON.stringify(selectedNode.userData.properties, null, 2)}}`);
            }}
        }}
        
        // Control functions
        function resetCamera() {{
            cameraRadius = 500;
            cameraTheta = 0;
            cameraPhi = Math.PI / 2;
        }}
        
        function togglePhysics() {{
            console.log('Physics toggle not implemented in this demo');
        }}
        
        function changeLayout() {{
            console.log('Layout change not implemented in this demo');
        }}
        
        function exportView() {{
            const dataUrl = renderer.domElement.toDataURL();
            const link = document.createElement('a');
            link.download = 'hypergraph_view.png';
            link.href = dataUrl;
            link.click();
        }}
        
        // Animation loop
        function animate() {{
            requestAnimationFrame(animate);
            
            // Update camera position
            camera.position.x = cameraRadius * Math.sin(cameraPhi) * Math.cos(cameraTheta);
            camera.position.y = cameraRadius * Math.cos(cameraPhi);
            camera.position.z = cameraRadius * Math.sin(cameraPhi) * Math.sin(cameraTheta);
            
            camera.lookAt(scene.position);
            
            // Rotate nodes slightly for visual effect
            Object.values(nodeObjects).forEach(node => {{
                node.rotation.y += 0.01;
            }});
            
            renderer.render(scene, camera);
        }}
        
        // Start animation
        camera.position.set(0, 0, 500);
        animate();
        
        // Handle window resize
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>'''.format(
            node_count=hypergraph_data['metadata']['total_nodes'],
            edge_count=hypergraph_data['metadata']['total_hyperedges'],
            hypergraph_json=json.dumps(hypergraph_data)
        )
        
        return html_template
    
    def _node_to_dict(self, node: HyperedgeNode) -> Dict:
        """Convert HyperedgeNode to dictionary"""
        return {
            "id": node.id,
            "label": node.label,
            "node_type": node.node_type,
            "position": list(node.position),
            "properties": node.properties
        }
    
    def _hyperedge_to_dict(self, edge: Hyperedge) -> Dict:
        """Convert Hyperedge to dictionary"""
        return {
            "id": edge.id,
            "nodes": edge.nodes,
            "edge_type": edge.edge_type,
            "strength": edge.strength,
            "properties": edge.properties
        }
    
    def save_visualization(self, hypergraph_data: Dict, filename: str) -> bool:
        """Save 3D hypergraph visualization to HTML file"""
        try:
            html_content = self.generate_3d_visualization_html(hypergraph_data)
            with open(filename, 'w') as f:
                f.write(html_content)
            print(f"3D hypergraph visualization saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving visualization: {e}")
            return False
    
    def generate_all_visualizations(self, output_dir: str = ".") -> List[str]:
        """Generate all hypergraph visualizations"""
        visualizations = [
            ("atomspace_hypergraph.html", self.create_atomspace_hypergraph()),
            ("cognitive_reasoning_hypergraph.html", self.create_cognitive_reasoning_hypergraph())
        ]
        
        saved_files = []
        for filename, hypergraph_data in visualizations:
            # Apply layout optimization
            self.apply_force_directed_layout(50)
            
            filepath = f"{output_dir}/{filename}"
            if self.save_visualization(hypergraph_data, filepath):
                saved_files.append(filepath)
        
        return saved_files


def main():
    """Demo hypergraph visualizer functionality"""
    print("🔗 3D Hypergraph Visualizer Demo")
    
    visualizer = HypergraphVisualizer({
        'dimensions': 3,
        'layout_algorithm': 'force_directed_3d',
        'enable_physics': True,
        'interactive': True
    })
    
    # Generate AtomSpace hypergraph
    print("🧠 Creating AtomSpace hypergraph...")
    atomspace_graph = visualizer.create_atomspace_hypergraph()
    
    # Apply layout optimization
    print("🎯 Optimizing layout...")
    visualizer.apply_force_directed_layout(100)
    
    # Save AtomSpace visualization
    print("💾 Saving AtomSpace visualization...")
    visualizer.save_visualization(atomspace_graph, "demo_atomspace_hypergraph.html")
    
    # Generate cognitive reasoning hypergraph
    print("🤔 Creating cognitive reasoning hypergraph...")
    reasoning_graph = visualizer.create_cognitive_reasoning_hypergraph()
    visualizer.save_visualization(reasoning_graph, "demo_cognitive_hypergraph.html")
    
    # Generate all visualizations
    print("📊 Generating all visualizations...")
    saved_files = visualizer.generate_all_visualizations("./hypergraphs")
    
    print(f"✅ Generated {len(saved_files)} hypergraph visualizations:")
    for file in saved_files:
        print(f"  - {file}")
    
    print(f"📈 AtomSpace nodes: {atomspace_graph['metadata']['total_nodes']}")
    print(f"🔗 AtomSpace hyperedges: {atomspace_graph['metadata']['total_hyperedges']}")
    print(f"🧠 Reasoning nodes: {reasoning_graph['metadata']['total_nodes']}")
    print(f"⚡ Reasoning hyperedges: {reasoning_graph['metadata']['total_hyperedges']}")
    
    print("🎉 3D hypergraph visualization demo completed!")


if __name__ == "__main__":
    main()