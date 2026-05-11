# Delivery Network Graph Analysis

A comprehensive graph-based network analysis system for identifying bottleneck hubs, analyzing corridor performance, and optimizing logistics operations at Delhivery (a major Indian logistics company).

## Table of Contents

1. [Project Overview](#project-overview)
2. [Business Context](#business-context)
3. [Data Description](#data-description)
4. [Architecture](#architecture)
5. [Phase 1: Data Pipeline & Graph Construction](#phase-1-data-pipeline--graph-construction)
6. [Phase 2: Bottleneck & Corridor Audit](#phase-2-bottleneck--corridor-audit)
7. [Phase 3: Graph-Enhanced ETA Prediction](#phase-3-graph-enhanced-eta-prediction)
8. [Key Findings](#key-findings)
8. [Project Structure](#project-structure)
9. [Installation & Setup](#installation--setup)
10. [Usage](#usage)
11. [Output Files](#output-files)
12. [Visualization Reference](#visualization-reference)
13. [Technical Details](#technical-details)
14. [Future Enhancements](#future-enhancements)

---

## Project Overview

This project implements a **Graph Neural Network (GNN)-inspired** approach to analyze delivery logistics data. Rather than using deep learning GNNs, it applies **classical graph theory** and **network analysis techniques** to:

- Construct a directed weighted graph representing the delivery network
- Identify structural bottlenecks using centrality metrics
- Analyze corridor-level performance patterns
- Provide actionable insights for logistics optimization

### Core Metrics Used

| Metric | Description |
|--------|-------------|
| **segment_factor** | Ratio of actual delivery time to OSRM-estimated time (values > 1 indicate delays) |
| **SLA breach** | Flag indicating deliveries that exceeded 120% of estimated time (factor > 1.2) |
| **Betweenness Centrality** | Measures how often a hub lies on shortest paths between other hubs |
| **Bottleneck Score** | Composite score combining betweenness (35%), delay factor (25%), SLA breach rate (25%), and out-degree (15%) |

---

## Business Context

### The Problem

Delhivery operates a vast logistics network across India with:
- **1,657 distribution hubs** across multiple states
- **2,783 active corridors** (route segments between hubs)
- **84.5% SLA breach rate** - an alarming 84.5% of deliveries arrive late
- Two primary transportation modes: **FTL (Full Truck Load)** and **Carting**

### The Goal

Identify which hubs and corridors are responsible for the majority of delays, enabling operations teams to prioritize intervention efforts where they will have the greatest impact.

### Why Graph Analysis?

Traditional analytics aggregate metrics at the corridor or hub level but miss the **network effect** - the idea that delays propagate through the network. A hub with moderate delay but high connectivity can affect many more downstream deliveries than a highly delayed but isolated corridor. Graph analysis captures this structural importance through **betweenness centrality**.

---

## Data Description

### Source Data: `data/raw/delivery_data.csv`

| Column | Description |
|--------|-------------|
| `trip_uuid` | Unique trip identifier |
| `source_center` | Source hub ID (e.g., IND000000ACB) |
| `source_name` | Source hub name with location (e.g., Gurgaon_Bilaspur_HB (Haryana)) |
| `destination_center` | Destination hub ID |
| `destination_name` | Destination hub name |
| `route_type` | Either "FTL" (Full Truck Load) or "Carting" |
| `segment_actual_time` | Actual time taken for the segment (hours) |
| `segment_osrm_time` | OSRM-estimated time for the segment (hours) |
| `segment_factor` | Actual time / OSRM time ratio (delay indicator) |
| `segment_osrm_distance` | Distance in kilometers |
| `od_start_time` | Trip start timestamp |
| `trip_creation_time` | Trip creation timestamp |

### Data Statistics

```
Total Records:          142,267 trip segments
Valid Records:          139,667 (after removing negative/zero segment_factor)
Unique Trips:           14,817

Route Type Distribution:
  - FTL (Full Truck Load):    98,729 trips (70.7%)
  - Carting:                 43,538 trips (29.3%)

Time of Day Distribution:
  - night:           46,564 trips (33.3%)
  - early_morning:   26,203 trips (18.8%)
  - morning:         13,584 trips (9.7%)
  - afternoon:       15,121 trips (10.8%)
  - evening:         21,537 trips (15.4%)
  - late_night:      19,258 trips (13.8%)

SLA Breach Rate:     84.5% of all trips
Median Delay Factor: 1.7x (deliveries take 70% longer than estimated)
```

---

## Architecture

### Three-Phase Approach

```
┌─────────────────────────────────────────────────────────────────┐
│                    DELIVERY NETWORK ANALYSIS                    │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 1: Data Pipeline & Graph Construction                   │
│  ├── Data Cleaning & Preprocessing                              │
│  ├── Feature Engineering (time buckets, SLA flags)              │
│  ├── Corridor Aggregation (source → destination stats)          │
│  ├── Graph Construction (NetworkX DiGraph)                      │
│  └── Node Metrics Computation (centrality, delay, SLA)         │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 2: Bottleneck & Corridor Audit                           │
│  ├── Hub-Level Audit (bottleneck ranking, risk matrix)          │
│  ├── Corridor-Level Audit (chronic delays, SLA contribution)   │
│  └── Network-Level Audit (state patterns, time patterns)       │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 3: Graph-Enhanced ETA Prediction                         │
│  ├── Baseline XGBoost (trip-level features only)                │
│  ├── Node2Vec Embeddings (learn graph structure)                │
│  ├── Graph-Enhanced XGBoost (features + graph embeddings)        │
│  └── Model Comparison & Evaluation                              │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Data Processing | pandas, numpy | Data cleaning, aggregation, feature engineering |
| Graph Construction | NetworkX | Directed weighted graph creation and manipulation |
| Network Analysis | NetworkX built-in algorithms | Betweenness centrality, degree metrics, connectivity |
| Visualization | matplotlib, seaborn | Charts for bottleneck ranking, heatmaps, scatter plots |
| Execution Environment | Jupyter Lab, Python 3.12 | Interactive analysis and development |

---

## Phase 1: Data Pipeline & Graph Construction

### Step 1: Data Cleaning

```python
# Remove rows with non-positive segment_factor (data entry errors)
df = df[df["segment_factor"] > 0]  # Dropped 2,600 rows

# Fill missing hub names with center IDs
df["source_name"] = df["source_name"].fillna(df["source_center"])
df["destination_name"] = df["destination_name"].fillna(df["destination_center"])
```

### Step 2: Feature Engineering

**Time Buckets**: The hour of `od_start_time` is categorized into 6 periods:
- `night` (0-4), `early_morning` (4-8), `morning` (8-12)
- `afternoon` (12-16), `evening` (16-20), `late_night` (20-24)

**SLA Breach Flag**: Trips are flagged as SLA breach if `segment_factor > 1.2` (actual time exceeds estimate by 20%)

**Delay Factor Cap**: Extreme outliers in `segment_factor` are capped at the 99th percentile to prevent skewed aggregations

### Step 3: Corridor Aggregation

Individual trip segments are aggregated to corridor level (source → destination pairs):

| Aggregated Field | Description |
|-----------------|-------------|
| `trip_count` | Number of unique trips on this corridor |
| `median_factor` | Median delay factor (typical delay) |
| `mean_factor` | Mean delay factor |
| `p75_factor`, `p90_factor` | 75th and 90th percentile delay factors |
| `sla_breach_rate` | Percentage of trips that are late |
| `median_actual_time` | Typical actual delivery time (hours) |
| `median_osrm_time` | Typical OSRM estimate (hours) |
| `median_distance` | Typical distance (km) |
| `route_types` | List of route types used (FTL, Carting, or both) |

**Stratified Aggregation**: Additionally, corridors are stratified by `route_type` and `time_bucket`, creating 4,565 unique corridor+route+time combinations for detailed analysis.

### Step 4: Graph Construction

A **directed weighted graph** is built where:

**Nodes (Hubs)**:
- Each unique `source_center` and `destination_center` becomes a node
- Node attributes: `name` (human-readable), `state` (extracted from name)
- Total nodes: **1,657**

**Edges (Corridors)**:
- Each unique (source, destination) pair becomes a directed edge
- Edge weight = `median_factor` (higher = more delayed corridor)
- Edge attributes: all corridor aggregation metrics
- Total edges: **2,783**

```
Example Node:
  Node ID: IND000000ACB
  Attributes: {
    "name": "Gurgaon_Bilaspur_HB (Haryana)",
    "state": "Haryana"
  }

Example Edge (IND000000ACB → IND000000AAL):
  Attributes: {
    "weight": 2.25,
    "median_factor": 2.25,
    "sla_breach_rate": 1.0,
    "trip_count": 18,
    "median_actual_time": 31.0,
    "median_osrm_time": 15.0,
    "median_distance": 14.49,
    "route_types": "['Carting']"
  }
```

### Step 5: Node Metrics Computation

For each hub, the following metrics are computed:

| Metric | Description | Formula |
|--------|-------------|---------|
| `in_degree` | Number of corridors incoming to this hub | Count of incoming edges |
| `out_degree` | Number of corridors outgoing from this hub | Count of outgoing edges |
| `betweenness_centrality` | Structural importance | Fraction of shortest paths passing through this hub |
| `avg_outgoing_factor` | Average delay factor of outgoing corridors | Mean of edge `median_factor` for outgoing edges |
| `avg_outgoing_sla_breach` | Average SLA breach rate of outgoing corridors | Mean of edge `sla_breach_rate` for outgoing edges |
| `bottleneck_score` | Composite ranking score | 0.35×normalized(betweenness) + 0.25×normalized(avg_factor) + 0.25×normalized(avg_sla) + 0.15×normalized(out_degree) |

**Betweenness Centrality Computation**: Computed on the largest weakly connected component (1,353 nodes) using 500 samples for computational efficiency. Exact computation would take hours on this graph size.

---

## Phase 2: Bottleneck & Corridor Audit

### Part 1: Hub-Level Audit

**Bottleneck Ranking**: All 1,657 hubs are ranked by their `bottleneck_score`. The top hubs represent the highest-priority targets for operational intervention.

**Hub Risk Matrix**: A scatter plot visualization with:
- X-axis: Betweenness centrality (structural importance)
- Y-axis: Average outgoing SLA breach rate (delay severity)
- Bubble size: Out-degree (corridor reach)
- Color: Bottleneck score

This matrix helps identify hubs in the "danger zone" (high betweenness + high SLA breach).

### Part 2: Corridor-Level Audit

**Chronic Corridors Identification**: Corridors are flagged as "chronically delayed" if:
- `median_factor > 1.2` (consistently delayed)
- `sla_breach_rate > 0.5` (more than half of trips are late)
- `trip_count > 10` (sufficient data for confidence)

**SLA Contribution Metric**: Calculated as `sla_breach_rate × trip_count`, this measures the **absolute number of late deliveries** attributable to each corridor (not just the percentage).

**Results**: 953 out of 2,783 corridors (34.2%) are flagged as chronically delayed.

### Part 3: Network-Level Audit

**State-Level Analysis**: Aggregates hub metrics by state to identify geographic patterns in delay performance.

**Time-of-Day Analysis**: Examines how delay patterns vary by time bucket (night, early_morning, morning, etc.).

**Route Type Analysis**: Compares FTL vs. Carting performance across the network.

---

## Phase 3: Graph-Enhanced ETA Prediction

### Overview

Phase 3 builds on the graph constructed in Phase 1 to create an **ETA (Estimated Time of Arrival) prediction model**. The key innovation is comparing two approaches:

1. **Baseline XGBoost**: Uses only trip-level features (distance, route type, time of day)
2. **Graph-Enhanced XGBoost**: Augments trip features with graph-derived embeddings and metrics

The goal is to demonstrate that incorporating graph structure improves prediction accuracy.

### Step 1: Baseline Model (Trip-Level Features)

The baseline model uses standard trip features:

| Feature | Description |
|---------|-------------|
| `segment_osrm_time` | OSRM-estimated time (hours) |
| `segment_osrm_distance` | Distance (km) |
| `route_type` | FTL or Carting (encoded) |
| `time_bucket` | Time of day category (encoded) |
| `day_of_week` | Day of week from `od_start_time` |
| `is_weekend` | Binary weekend flag |

### Step 2: Node2Vec Embeddings

**Node2Vec** is used to learn low-dimensional vector representations of each hub (node) that capture graph structure:

```python
from node2vec import Node2Vec

node2vec = Node2Vec(G, dimensions=64, walk_length=30, num_walks=200, workers=1)
model = node2vec.fit(window=10, min_count=1)
```

- **dimensions**: 64 (embedding size)
- **walk_length**: 30 (each random walk has 30 nodes)
- **num_walks**: 200 (200 walks per node)
- **Algorithm**: Combines BFS and DFS to capture both local and global structure

The resulting embeddings capture:
- Structural similarity between hubs
- Connectivity patterns in the network
- Proximity in terms of both topology and delay behavior

### Step 3: Graph-Enhanced Features

For each trip, we augment the baseline features with:

| Feature | Source |
|---------|--------|
| `source_embedding` | Node2Vec embedding of source hub |
| `dest_embedding` | Node2Vec embedding of destination hub |
| `source_betweenness` | Betweenness centrality of source hub |
| `dest_betweenness` | Betweenness centrality of destination hub |
| `source_out_degree` | Out-degree of source hub |
| `dest_in_degree` | In-degree of destination hub |
| `corridor_median_factor` | Historical delay factor for this corridor |
| `corridor_sla_breach` | Historical SLA breach rate for this corridor |

This creates a **64 + 64 + 6 = 134** dimensional feature space for the enhanced model.

### Step 4: Model Training & Evaluation

Both models use XGBoost regressor with identical hyperparameters:

```python
model = XGBRegressor(
    n_estimators=200,
    max_depth=8,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
```

### Results

| Model | MAE | RMSE | 15% Accuracy |
|-------|-----|------|---------------|
| **Baseline XGBoost** | 0.829 | 1.447 | 23.83% |
| **Graph-Enhanced XGBoost** | 0.699 | 1.233 | 30.86% |

**Improvement**:
- **15.7% better MAE** (0.829 → 0.699)
- **14.8% better RMSE** (1.447 → 1.233)
- **29.5% better 15% accuracy** (23.83% → 30.86%)

The graph-enhanced model significantly outperforms the baseline, proving that graph structure adds predictive value beyond trip-level features alone.

### Key Insights

1. **Node2Vec embeddings capture delay patterns**: Hubs with similar structural roles (similar embeddings) tend to have similar delay behaviors.

2. **Betweenness centrality is predictive**: A hub's structural importance (betweenness) correlates with its delay characteristics.

3. **Corridor history matters**: Including the historical median delay factor of the specific corridor provides strong signal.

4. **Graph features bridge data gaps**: For new routes with no historical data, the embeddings can still provide reasonable estimates based on similar hubs.

---

## Key Findings

### Network Topology

| Metric | Value |
|--------|-------|
| Total Nodes (Hubs) | 1,657 |
| Total Edges (Corridors) | 2,783 |
| Graph Density | 0.001014 |
| Connected Components | 64 |
| Largest Component | 1,353 nodes (81.7% of network) |

### Top 10 Bottleneck Hubs

| Rank | Hub Name | State | Betweenness | Avg Delay | SLA Breach | Score |
|------|----------|-------|-------------|-----------|------------|-------|
| 1 | Gurgaon_Bilaspur_HB | Haryana | 0.3547 | 1.599 | 79.4% | 0.733 |
| 2 | Bangalore_Nelmngla_H | Karnataka | 0.2299 | 1.544 | 77.4% | 0.561 |
| 3 | Mariani_Mainroad_D | Assam | 0.0000 | 11.600 | 100% | 0.503 |
| 4 | Helencha_ColnyDPP_D | West Bengal | 0.0000 | 11.600 | 100% | 0.503 |
| 5 | Mahasamund_RajpurRD_D | Chhattisgarh | 0.0000 | 11.600 | 100% | 0.503 |
| 6 | Jabalpur | Madhya Pradesh | 0.0000 | 11.600 | 100% | 0.503 |
| 7 | Ranaghat_ArickDPP_D | West Bengal | 0.0000 | 11.600 | 100% | 0.503 |
| 8 | RampuraPhul_DC | Punjab | 0.0000 | 11.600 | 100% | 0.503 |
| 9 | Simlapal_Central_D_1 | West Bengal | 0.0000 | 11.600 | 100% | 0.503 |
| 10 | Faridabad_Old | Haryana | 0.0000 | 11.600 | 100% | 0.503 |

### Key Insights

1. **Gurgaon is the network choke point**: With 35% of all shortest paths passing through it, Gurgaon (IND000000ACB) is by far the most structurally critical hub. Any delay here cascades to a huge number of downstream deliveries.

2. **Bangalore is the second critical hub**: With 23% betweenness centrality and high SLA breach rates, Bangalore (IND562132AAA) is the second-most important hub.

3. **Some hubs have extreme delay factors**: Several hubs (e.g., in Assam, West Bengal, Chhattisgarh) show delay factors of 11.6x - these are likely remote or difficult-to-access locations.

4. **34% of corridors are chronically delayed**: 953 out of 2,783 corridors meet the chronic delay criteria, indicating systemic performance issues.

5. **Mumbai-Bhiwandi corridor is critical**: The top chronic corridors are all in the Mumbai metropolitan area, with the Mumbai → Bhiwandi and Bhiwandi → Mumbai corridors showing 97-100% SLA breach rates.

6. **Top 10% of corridors carry 34% of trips**: A small subset of high-volume corridors carries a disproportionate share of total delivery volume, making them high-priority targets.

7. **Route type matters**: FTL and Carting have different delay characteristics - Carting corridors tend to be shorter but more numerous.

---

## Project Structure

```
.
├── README.md                      # This file
├── main.py                        # Main entry point (placeholder)
├── pyproject.toml                 # Project dependencies
├── uv.lock                        # Locked dependencies
├── .python-version                # Python version specification
│
├── data/                          # Data directory
│   ├── raw/                       # Raw data (input)
│   │   └── delivery_data.csv      # Original delivery dataset
│   └── processed/                # Processed data (output)
│       ├── train_clean.csv        # Cleaned training data
│       ├── test_clean.csv         # Cleaned test data
│       ├── graph_summary.json     # Network statistics summary
│       ├── delivery_network.graphml  # NetworkX graph file
│       ├── node_metrics.csv       # Per-hub metrics and bottleneck scores
│       ├── corridor_aggregates.csv # Per-corridor aggregated metrics
│       ├── corridor_stratified.csv # Corridor metrics by route/time
│       ├── chronic_corridors.csv  # Chronically delayed corridors
│       ├── bottleneck_hubs_ranked.csv # Ranked bottleneck hubs
│       └── sla_contribution.csv   # Corridor SLA contribution rankings
│
├── notebooks/                     # Jupyter notebooks
│   ├── phase1_data_pipeline.ipynb # Phase 1: Graph construction
│   ├── phase2_bottleneck_audit.ipynb # Phase 2: Bottleneck analysis
│   └── phase3_graph_models.ipynb  # Phase 3: ETA prediction model
│
├── src/                          # Python source code
│   ├── __init__.py               # Package init
│   ├── pipeline.py               # Data pipeline functions
│   ├── features.py              # Feature engineering
│   ├── graph_builder.py          # Graph construction
│   ├── models.py                # (Reserved for ML models)
│   └── utils.py                  # Utility functions
│
├── outputs/                      # Generated outputs
│   ├── phase2_visuals/          # Phase 2 visualization outputs
│   │   ├── 01_bottleneck_hubs_ranked.png    # Top 20 bottleneck bar chart
│   │   ├── 02_hub_risk_matrix.png           # Hub risk scatter plot
│   │   ├── 03_chronic_corridors.png        # Top 20 chronic corridors
│   │   ├── 04_corridor_volume_vs_breach.png # Volume vs breach scatter
│   │   ├── 05_state_heatmap.png            # State-level performance heatmap
│   │   ├── 06_routetype_timebucket_heatmap.png # Route/time heatmap
│   │   ├── 07_ftl_vs_carting.png           # FTL vs Carting comparison
│   │   ├── 08_delay_distribution.png       # Delay factor distribution
│   │   └── 09_network_graph_top30.png      # Network visualization
│   └── phase3_visuals/          # Phase 3 model outputs
│       ├── 01_model_comparison.png        # Baseline vs Graph-Enhanced comparison
│       ├── 02_predicted_vs_actual.png      # Prediction scatter plot
│       ├── 03_feature_importance.png       # XGBoost feature importance
│       ├── 04_residuals.png                # Residual analysis
│       └── 05_error_distribution.png       # Error distribution by model
│
└── .venv/                        # Python virtual environment
```

---

## Installation & Setup

### Prerequisites

- Python 3.12 or higher
- uv package manager (recommended) or pip

### Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Using pip
pip install -r requirements.txt
```

### Dependencies (from pyproject.toml)

```
ipykernel>=7.2.0
jupyterlab>=4.5.7
matplotlib>=3.10.9
networkx>=3.6.1
node2vec>=0.4.3
numpy>=2.4.4
pandas>=3.0.2
scikit-learn>=1.8.0
seaborn>=0.13.2
xgboost>=3.2.0
```

---

## Usage

### Running the Notebooks

```bash
# Start Jupyter Lab
jupyter lab
```

Then open and run the notebooks in order:
1. `notebooks/phase1_data_pipeline.ipynb` - Phase 1: Graph construction and node metrics
2. `notebooks/phase2_bottleneck_audit.ipynb` - Phase 2: Bottleneck and corridor audit with visualizations
3. `notebooks/phase3_graph_models.ipynb` - Phase 3: Graph-enhanced ETA prediction model

### Python Script (main.py)

```bash
python main.py
```

(Note: Currently a placeholder - the analysis is primarily notebook-driven)

---

## Output Files

### Processed Data Files (in `data/processed/`)

| File | Description |
|------|-------------|
| `train_clean.csv` | Cleaned training data with engineered features |
| `test_clean.csv` | Cleaned test data |
| `graph_summary.json` | Quick reference for key network statistics in JSON format |
| `delivery_network.graphml` | NetworkX DiGraph with all node/edge attributes |
| `node_metrics.csv` | Per-hub metrics: ID, name, state, degrees, betweenness, delay, SLA, bottleneck score |
| `corridor_aggregates.csv` | Per-corridor metrics: source, destination, trip count, delay factors, SLA rate |
| `corridor_stratified.csv` | Corridor metrics broken down by route_type and time_bucket |
| `chronic_corridors.csv` | Corridors flagged as chronically delayed with SLA contribution |
| `bottleneck_hubs_ranked.csv` | All hubs ranked by bottleneck score |
| `sla_contribution.csv` | Corridors ranked by SLA contribution (absolute late deliveries) |

### Visualization Files (in `outputs/phase2_visuals/`)

See [Visualization Reference](#visualization-reference) below for details on each chart.

### Phase 3 Model Files (in `data/processed/`)

| File | Description |
|------|-------------|
| `node2vec_embeddings.csv` | 64-dimensional Node2Vec embeddings for all 1,657 hubs |
| `baseline_model.json` | Trained baseline XGBoost model (trip features only) |
| `enhanced_model.json` | Trained graph-enhanced XGBoost model |
| `test_predictions.csv` | Predictions on test set from both models |
| `model_benchmark.csv` | Comparison metrics (MAE, RMSE, 15% accuracy) |

### Phase 3 Visualization Files (in `outputs/phase3_visuals/`)

| # | Chart | Description |
|---|-------|-------------|
| 01 | Model Comparison | Bar chart comparing Baseline vs Graph-Enhanced metrics |
| 02 | Predicted vs Actual | Scatter plot of predicted vs actual delay factors |
| 03 | Feature Importance | Top 20 XGBoost feature importance scores |
| 04 | Residuals | Residual analysis for both models |
| 05 | Error Distribution | Histogram of prediction errors by model |

---

## Visualization Reference

| # | Chart | Description |
|---|-------|-------------|
| 01 | Bottleneck Ranking | Horizontal bar chart showing top 20 bottleneck hubs by score |
| 02 | Hub Risk Matrix | Scatter plot: betweenness (x) vs SLA breach (y), bubble size = out-degree |
| 03 | Chronic Corridors | Top 20 corridors by SLA contribution (absolute late deliveries) |
| 04 | Volume vs Breach | Scatter: trip count (x) vs SLA breach (y), color = delay factor |
| 05 | State Heatmap | Performance heatmap by state |
| 06 | Route-Time Heatmap | Delay patterns by route type and time of day |
| 07 | FTL vs Carting | Comparison of two transportation modes |
| 08 | Delay Distribution | Distribution of delay factors across network |
| 09 | Network Graph | Visual representation of top 30 hubs and their connections |

---

## Technical Details

### Graph Properties

- **Directed**: Yes (corridors have direction: source → destination)
- **Weighted**: Yes (edge weight = median_factor)
- **Connected Components**: 64 (indicates some isolated hub pairs)
- **Largest Component**: 1,353 nodes (81.7% of network)

### Centrality Computation

Betweenness centrality is computed using NetworkX's built-in algorithm with:
- `weight="weight"` - uses delay factor as edge weight
- `normalized=True` - scales to [0,1] range
- `k=500` - samples 500 nodes for computational efficiency (exact computation would take hours)

### Bottleneck Score Formula

```
bottleneck_score = 0.35 × normalized(betweenness)
                 + 0.25 × normalized(avg_outgoing_factor)
                 + 0.25 × normalized(avg_outgoing_sla_breach)
                 + 0.15 × normalized(out_degree)
```

All components are min-max normalized to [0,1] range before weighting.

### Data Cleaning Decisions

1. **Dropped 2,600 rows** with non-positive segment_factor (data entry errors)
2. **Capped delay factors** at 99th percentile to prevent outlier skew in aggregations
3. **Filled missing hub names** with center IDs for consistency
4. **SLA threshold** set at factor > 1.2 (20% over estimate) based on business context

---

## Future Enhancements

### Potential Improvements

1. **Temporal Analysis**: Add time-series component to track how bottleneck scores change over weeks/months

2. **Route Optimization**: Use the graph to recommend alternative routes that bypass high-delay hubs

3. **Prediction Model**: Build a supervised model to predict delay factors for new corridors based on graph features

4. **GNN Implementation**: Implement actual Graph Neural Networks for node-level delay prediction

5. **Interactive Dashboard**: Build a Streamlit or Dash dashboard for interactive exploration

6. **What-if Scenarios**: Model the impact of "fixing" a bottleneck hub on overall network performance

7. **External Data Integration**: Incorporate weather, traffic, or holiday data as node/edge features

---

## License & Credits

- **Data Source**: Delhivery logistics operations data
- **Analysis Approach**: Graph-based network analysis using NetworkX
- **Created**: IITG Summer Project

---

## Contact

For questions or contributions, please refer to the project repository.