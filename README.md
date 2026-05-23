# OSDU Schema Tree Visualizer

**🪴 A clean, layered tree visualizer for exploring the OSDU data model schemas as Reference Data roots → Master Data stem → WPC branches → Dataset leaves.**

Created for the OSDU community to solve the "dense graph hairball" problem with existing tools.

## 🌳 The Vision

Your perfect metaphor realized:
- **🌍 Roots/Earth = Reference Data** (shared vocab, manifests, stable taxonomies)
- **🌳 Stem = Master Data** (Wells, Wellbores, ActivityPlan, Facilities — real entities with lifecycles)
- **🌿 Branches = Work Product Components (WPC)** (WellLogs, Seismic interpretations, Documents — the rich content layer)
- **🍃 Leaves = Datasets** (actual files: LAS, SEG-Y, images, etc.)

## 📖 Deep Research & Analysis Summary

### OSDU Data Platform Overview
OSDU standardizes subsurface data using JSON Schemas stored in the official [data-definitions](https://community.opengroup.org/osdu/data/data-definitions) repo.

**Key Categories** (from AWS, 47Lining, and community docs):
- **Reference Data**: Permissible values, controlled vocab (UOM, CRS, ActivityCode, etc.). Loaded first via manifests in `ReferenceValues/Manifests/`.
- **Master Data**: Authoritative instances (e.g. ActivityPlan schema you linked).
- **Work Product Components**: Metadata-rich objects linking masters + refs + datasets.
- **Datasets**: File containers.

### Schema Mechanics (Why It's Complicated)
- All schemas use JSON Schema + `x-osdu-*` extensions.
- **Inheritance**: `allOf` arrays referencing `AbstractMaster`, `AbstractWPC`, etc.
- **Dependencies**: Regex patterns in string properties enforce kind references (e.g. `master-data--Wellbore`).
- Result: Large DAG with cross-domain links → full viz tools (like the React one) become unusable.

**Example Schema Snippet** (ActivityPlan.1.0.0 — Master Data):
```json
{
  "title": "Activity Plan",
  "allOf": [{"$ref": "../abstract/AbstractMaster.1.0.0.json"}, {"$ref": "../abstract/AbstractProject.1.0.0.json"}],
  "properties": {
    "WellboreID": {"pattern": "^...master-data--Wellbore:...$"},
    "ActivityCodeID": {"pattern": "^...reference-data--ActivityCode:...$"}
  }
}
```

### Existing Tools & Why This One Wins
- **OSDU Schema Viz** (chadleong/osdu-viz): Excellent React Flow graph but loads the *entire* universe → slow + unreadable hairball.
- **This app**: Forces layers, filters, collapsible view, and focused Plotly tree. Perfect for exploration.

## 🚀 Usage

```bash
# 1. Get schemas
git clone https://community.opengroup.org/osdu/data/data-definitions.git

# 2. Get this app
git clone https://github.com/oliknutsen/osdu-tree.git
cd osdu-tree

# 3. Install
pip install streamlit networkx plotly pandas

# 4. Run (point at schemas folder)
streamlit run osdu_tree_viz.py
```

In the app:
- Enter path to your `data-definitions` clone
- Use sidebar filters (layers, domains, search)
- Click "Render Layered Graph" for the beautiful interactive tree!

## 📁 Files in This Repo
- `README.md` — Full guide + analysis
- `osdu_tree_viz.py` — Complete runnable Streamlit app (6267 bytes)

## 🛠️ App Features
- Auto-classifies 100s of schemas into 4 layers
- Extracts real dependencies from `$ref` + kind patterns
- Interactive Plotly layered layout (y = layer)
- Fast collapsible explorer grouped by your tree metaphor
- Sidebar stats (total schemas, edge count)

## 🔗 Links
- Schemas repo: https://community.opengroup.org/osdu/data/data-definitions
- E-R docs & workbooks: https://community.opengroup.org/osdu/data/data-definitions/-/tree/master/E-R
- OSDU Forum: https://osduforum.org/
- Accenture Ontology: https://accenture.github.io/OSDU-Ontology/

## 💡 Next Steps & Ideas
- Add E-R subdomain filters
- Mermaid / Graphviz export button
- Focus mode: show subtree for one schema
- Deploy to Streamlit Cloud

---

*Generated with Grok (xAI) • May 23, 2026 • For oliknutsen*

*"Now the OSDU universe has a clear tree structure you can actually explore."*