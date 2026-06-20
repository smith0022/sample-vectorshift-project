from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse')
def parse_pipeline(pipeline: str = Form(...)):
    try:
        data = json.loads(pipeline)
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        
        num_nodes = len(nodes)
        num_edges = len(edges)
        
        # Build adjacency list
        adj = {node['id']: [] for node in nodes}
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            if source in adj:
                adj[source].append(target)
                
        # Cycle detection using DFS
        visited = {} # 0: unvisited, 1: visiting, 2: visited
        def has_cycle(v):
            visited[v] = 1
            for neighbor in adj.get(v, []):
                if visited.get(neighbor, 0) == 1:
                    return True
                if visited.get(neighbor, 0) == 0:
                    if has_cycle(neighbor):
                        return True
            visited[v] = 2
            return False
            
        is_dag = True
        for node in nodes:
            if visited.get(node['id'], 0) == 0:
                if has_cycle(node['id']):
                    is_dag = False
                    break
                    
        return {'num_nodes': num_nodes, 'num_edges': num_edges, 'is_dag': is_dag}
    except Exception as e:
        return {'error': str(e)}
