"""
Single Exploration Test - Papers Only
做一次探索，观察节点内容
"""

import sys
import os
import time
import requests

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000/api/v1"

print("=" * 70)
print("Single Exploration Test - Arxiv Papers Only")
print("=" * 70)

# 1. Clear existing frontier
print("\n[1] Clearing frontier...")
try:
    response = requests.delete(f"{API_BASE}/frontier/clear")
    print(f"  Status: {response.status_code}")
except Exception as e:
    print(f"  Error: {e}")

# 2. Add paper-specific seeds
print("\n[2] Adding paper research seeds...")
paper_seeds = [
    "transformer architecture",
    "attention mechanisms",
    "machine learning"
]

for seed in paper_seeds:
    try:
        response = requests.post(
            f"{API_BASE}/frontier/add",
            json={"seed": seed, "priority": 0.8}
        )
        print(f"  Added: {seed} - {response.status_code}")
    except Exception as e:
        print(f"  Error adding {seed}: {e}")

# 3. Check frontier status
print("\n[3] Checking frontier...")
try:
    response = requests.get(f"{API_BASE}/frontier")
    if response.status_code == 200:
        frontier = response.json()
        print(f"  Frontier size: {len(frontier)} seeds")
        for seed in frontier[:3]:
            print(f"    - {seed['seed']} (priority: {seed['priority']:.2f})")
except Exception as e:
    print(f"  Error: {e}")

# 4. Start exploration
print("\n[4] Starting exploration (max 3 iterations)...")
try:
    response = requests.post(
        f"{API_BASE}/explore/start",
        params={"max_iterations": 3, "strategy": "graph"}
    )

    if response.status_code == 200:
        result = response.json()
        task_id = result.get('task_id')
        print(f"  Task ID: {task_id}")
        print(f"  Status: {result.get('status')}")

        # 5. Wait for completion
        print("\n[5] Waiting for exploration to complete...")
        max_wait = 120
        start_time = time.time()

        while time.time() - start_time < max_wait:
            status_resp = requests.get(f"{API_BASE}/explore/status/{task_id}")
            if status_resp.status_code == 200:
                status_data = status_resp.json()
                current_status = status_data.get('status')

                print(f"  Status: {current_status}")

                if current_status in ['completed', 'failed']:
                    break

            time.sleep(5)

        # 6. Check results
        print("\n[6] Checking exploration results...")
        result_resp = requests.get(f"{API_BASE}/explore/result/{task_id}")
        if result_resp.status_code == 200:
            result_data = result_resp.json()
            print(f"  Nodes created: {result_data.get('nodes_created', 0)}")
            print(f"  Paths created: {result_data.get('paths_created', 0)}")

            nodes = result_data.get('nodes', [])
            if nodes:
                print(f"\n[7] Node Details:")
                for i, node in enumerate(nodes[:5], 1):
                    print(f"\n  Node {i}:")
                    print(f"    Title: {node.get('title', 'N/A')[:80]}")
                    print(f"    Source: {node.get('source', 'N/A')}")
                    print(f"    Type: {node.get('type', 'N/A')}")
                    print(f"    Value Score: {node.get('value_score', 0):.3f}")

                    content = node.get('content', '')
                    if content:
                        preview = content[:200] + "..." if len(content) > 200 else content
                        print(f"    Content: {preview}")
            else:
                print("  No nodes created!")
        else:
            print(f"  Error getting results: {result_resp.status_code}")

    else:
        print(f"  Error starting exploration: {response.status_code}")
        print(f"  Response: {response.text}")

except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

# 8. List all nodes in database
print("\n[8] All nodes in database...")
try:
    response = requests.get(f"{API_BASE}/nodes")
    if response.status_code == 200:
        all_nodes = response.json()
        print(f"  Total nodes: {len(all_nodes)}")
        for node in all_nodes:
            print(f"    - {node.get('title', 'N/A')[:60]}... (score: {node.get('value_score', 0):.2f})")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 70)
print("Test Complete!")
print("=" * 70)
