import streamlit as st
import json
import os
from pathlib import Path
import re
import networkx as nx
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="OSDU Schema Tree Viz", layout="wide")
st.title("🪴 OSDU Schema Tree Visualizer")
st.caption("Reference Data (roots) → Master Data (stem) → WPC (branches) → Datasets (leaves)")

repo_path = st.text_input("Path to data-definitions folder", value="./data-definitions")
if not repo_path or not Path(repo_path).exists():
    st.warning("Please clone the repo and point to the folder above.")
    st.stop()

@st.cache_data
def load_and_parse_schemas(root_dir):
    schemas = {}
    G = nx.DiGraph()
    layer_map = {
        "reference-data": 0,
        "master-data": 1,
        "work-product-component": 2,
        "work-product": 2,
        "dataset": 3,
        "abstract": 3,
    }

    pattern = re.compile(r"(reference-data|master-data|work-product-component|work-product|dataset)--", re.I)

    for file_path in Path(root_dir).rglob("*.json"):
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            title = data.get("title") or file_path.stem
            path_str = str(file_path).lower()
            category = next((k for k in layer_map if k in path_str), "other")
            if category == "other":
                match = pattern.search(title + str(data))
                category = match.group(0).rstrip("--").lower() if match else "other"

            layer = layer_map.get(category, 3)

            refs = set()
            if isinstance(data.get("allOf"), list):
                for item in data["allOf"]:
                    if isinstance(item.get("$ref"), str):
                        refs.add(item["$ref"].split("/")[-1].replace(".json", ""))

            def extract_refs(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if k == "$ref" and isinstance(v, str):
                            refs.add(v.split("/")[-1].replace(".json", ""))
                        elif isinstance(v, str) and pattern.search(v):
                            refs.add(v)
                        else:
                            extract_refs(v)
                elif isinstance(obj, list):
                    for item in obj:
                        extract_refs(item)

            extract_refs(data.get("properties", {}))

            schemas[title] = {
                "title": title,
                "category": category.capitalize(),
                "layer": layer,
                "path": str(file_path),
                "description": data.get("description", "")[:200],
                "refs": list(refs)[:10]
            }

            G.add_node(title, layer=layer, category=category)
            for r in refs:
                if r and r != title:
                    G.add_edge(title, r)

        except Exception:
            continue

    return schemas, G

schemas, G = load_and_parse_schemas(repo_path)

st.sidebar.header("Filters")
search = st.sidebar.text_input("Search schema", "")
selected_layers = st.sidebar.multiselect("Layers", options=[0,1,2,3], default=[0,1,2,3], format_func=lambda x: ["🌍 Reference", "🌳 Master", "🌿 WPC", "🍃 Dataset"][x])

domains = sorted(set(s["category"] for s in schemas.values()))
selected_domains = st.sidebar.multiselect("Domains/Categories", options=domains, default=domains[:5])

filtered = {k: v for k, v in schemas.items() if v["layer"] in selected_layers and any(d in v["category"] for d in selected_domains) and (not search or search.lower() in k.lower())}

st.subheader(f"Found {len(filtered)} schemas in selected layers")

if st.button("Render Layered Graph (interactive)"):
    pos = {}
    layer_nodes = {l: [] for l in range(4)}
    for node, data in G.nodes(data=True):
        if node in filtered:
            layer_nodes[data.get("layer", 3)].append(node)

    for l, nodes in layer_nodes.items():
        for i, node in enumerate(nodes):
            pos[node] = (i * 1.5 - len(nodes)/2, -l * 3)

    edge_x, edge_y = [], []
    for edge in G.edges():
        if edge[0] in pos and edge[1] in pos:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color="#888"), hoverinfo="none", mode="lines"))
    node_x = [pos[n][0] for n in pos]
    node_y = [pos[n][1] for n in pos]
    node_text = [f"{n}<br>Layer {schemas.get(n, {}).get('layer', 0)} - {schemas.get(n, {}).get('category', '')}" for n in pos]
    node_color = [schemas.get(n, {}).get("layer", 0) for n in pos]

    fig.add_trace(go.Scatter(x=node_x, y=node_y, mode="markers+text", marker=dict(size=12, color=node_color, colorscale="Viridis", showscale=True), text=[n[:30] for n in pos], textposition="top center", hovertext=node_text, hoverinfo="text"))
    fig.update_layout(title="OSDU Layered Tree (drag to pan/zoom)", showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), height=800)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Collapsible Layered Tree Explorer")
for layer_name, layer_id in [("🌍 Reference Data (roots)", 0), ("🌳 Master Data (stem)", 1), ("🌿 Work Product Components (branches)", 2), ("🍃 Datasets (leaves)", 3)]:
    layer_schemas = {k: v for k, v in filtered.items() if v["layer"] == layer_id}
    if layer_schemas:
        with st.expander(f"{layer_name} — {len(layer_schemas)} schemas", expanded=layer_id == 0):
            for title, info in sorted(layer_schemas.items()):
                with st.expander(f"📌 {title} ({info['category']})", expanded=False):
                    st.write(info.get("description", ""))
                    st.caption(info.get("path", ""))
                    if info.get("refs"):
                        st.write("**Depends on:**", ", ".join(info["refs"]))

st.info("✅ Clean layered tree view for OSDU schemas. Customize as needed!")
st.sidebar.write(f"**Total schemas:** {len(schemas)} | **Dependencies:** {G.number_of_edges()}")