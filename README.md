# Delivery Network Graph Analysis

A comprehensive graph-based network analysis system for identifying bottleneck hubs, analyzing corridor performance, predicting ETAs, and optimizing logistics operations at Delhivery, India's leading logistics and supply chain services company.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebooks-orange.svg)](https://jupyter.org/)
[![NetworkX](https://img.shields.io/badge/NetworkX-2.8-blue)](https://networkx.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-1.7-red)](https://xgboost.readthedocs.io/)

---

## Table of Contents

1. [Quick Stats](#quick-stats)
2. [Project Overview](#project-overview)
3. [Data Schema](#data-schema)
4. [Methodology](#methodology)
5. [Project Phases](#project-phases)
6. [Model Details](#model-details)
7. [Key Findings](#key-findings)
8. [Project Structure](#project-structure)
9. [Installation & Setup](#installation--setup)
10. [Usage](#usage)
11. [Output Files](#output-files)
12. [Visualizations](#visualizations)
13. [Future Enhancements](#future-enhancements)
14. [License](#license)

---

## Quick Stats

| Metric | Value |
|--------|-------|
| Total Hubs (Nodes) | 1,657 |
| Total Corridors (Edges) | 2,783 |
| Trips Analyzed | 14,817 |
| SLA Breach Rate | 84.5% |
| Median Delay Factor | 1.7× |
| Chronically Delayed Corridors | 953 (34.2%) |
| Model Improvement (MAE) | 15.7% |
| Classifier Accuracy | 99.6% |

---

## Project Overview

This project transforms raw logistics operational data into actionable insights using graph theory and machine learning. By modeling Delhivery's delivery network as a directed weighted graph, we identify structural bottlenecks that cause cascading delays across the network.

### Problem Statement

Delhivery operates a complex logistics network with:
- **1,657 distribution hubs** across India
- **2,783 active corridors** connecting these hubs
- **84.5% of deliveries** currently breaching Service Level Agreements (SLA)

The root cause of delays is not uniformly distributed—it is concentrated in specific structurally critical hubs and chronically delayed corridors. This analysis identifies those bottlenecks and quantifies their impact.

### Approach

1. **Graph Construction**: Model the delivery network as a directed weighted graph
2. **Bottleneck Identification**: Use centrality metrics to identify critical hubs
3. **Performance Analysis**: Analyze corridor-level delay patterns
4. **ETA Prediction**: Use Node2Vec embeddings to enhance ML predictions
5. **Route Optimization**: Classify optimal route types (FTL vs Carting)

---

## Data Schema

### Raw Data (`delivery_data.csv`)

| Column | Type | Description |
|--------|------|-------------|
| `trip_id` | string | Unique trip identifier |
| `source_hub` | string | Origin hub name |
| `destination_hub` | string | Destination hub name |
| `route_type` | string | FTL (Full Truck Load) or Carting |
| `actual_time` | float | Actual transit time (minutes) |
| `osrm_time` | float | OSRM estimated time (minutes) |
| `actual_distance` | float | Actual distance traveled (km) |
| `osrm_distance` | float | OSRM estimated distance (km) |
| `trip_state` | string | State where trip originated |
| `day_of_week` | integer | Day of week (0-6) |
| `trip_date` | date | Date of trip |

### Derived Features

| Feature | Description |
|---------|-------------|
| `segment_factor` | actual_time / osrm_time (delay ratio) |
| `sla_breach` | 1 if segment_factor > 1.2, else 0 |
| `time_bucket` | Categorical: night, early_morning, morning, afternoon, evening, late_night |
| `is_weekend` | Boolean flag for weekend trips |

---

## Methodology

### Graph Construction

The delivery network is modeled as a **directed weighted graph** G = (V, E) where:

- **V** = 1,657 hub nodes
- **E** = 2,783 directed edges (corridors)
- **Edge weight** = median segment_factor for all trips on that corridor

```
Graph Construction Algorithm:
1. For each unique (source, destination) pair in trips:
   a. Calculate median segment_factor across all trips
   b. Create edge with weight = median_factor
2. Add node attributes: hub name, state, degrees
3. Compute centrality metrics for all nodes
```

### Bottleneck Score Calculation

Each hub is assigned a composite **bottleneck score** combining structural importance and operational performance:

```
bottleneck_score = 0.35 × betweenness_centrality 
                 + 0.25 × avg_delay_factor 
                 + 0.25 × sla_breach_rate 
                 + 0.15 × out_degree_normalized
```

### Node2Vec Embeddings

Graph structural information is captured using Node2Vec—a scalable feature learning technique for graphs:

- **Dimensions**: 64
- **Walk Length**: 30
- **Walks per Node**: 200
- **p (return parameter)**: 1
- **q (in-out parameter)**: 1

This captures both **local neighborhood structure** (Breadth-First Search) and **global network structure** (Depth-First Search).

---

## Project Phases

### Phase 1: Data Pipeline & Graph Construction

**Objective**: Clean data, engineer features, construct the network graph.

**Steps**:
1. **Data Cleaning**: Removed 2,600 invalid records with non-positive segment_factor
2. **Feature Engineering**:
   - Time buckets: night (0-6), early_morning (6-9), morning (9-12), afternoon (12-15), evening (15-18), late_night (18-24)
   - SLA breach flag (segment_factor > 1.2)
   - Capped delay factors at 99th percentile to handle outliers
3. **Graph Construction**: Built directed weighted graph with NetworkX
4. **Node Metrics**: Computed betweenness centrality, degree centrality, average delay, SLA rate per hub

**Output**: `delivery_network.graphml`, `node_metrics.csv`, `corridor_aggregates.csv`

---

### Phase 2: Bottleneck & Corridor Audit

**Objective**: Identify and rank bottleneck hubs and chronically delayed corridors.

**Hub-Level Analysis**:
- Ranked all 1,657 hubs by composite bottleneck score
- Top 5 hubs identified as priority intervention targets
- **Gurgaon**: Network choke point (34.5% betweenness centrality)
- **Bangalore**: Second critical hub (23.6% betweenness)

**Corridor-Level Analysis**:
- Flagged 953 corridors (34.2%) as chronically delayed
- Criteria: segment_factor > 1.2, SLA breach rate > 50%, trip_count > 10
- Computed SLA contribution: absolute late deliveries per corridor

**Network-Level Analysis**:
- State-wise delay patterns
- Time-of-day performance variations
- Route type comparison (FTL vs Carting)

**Output**: `bottleneck_hubs_ranked.csv`, `chronic_corridors.csv`, `sla_contribution.csv`

---

### Phase 3: Graph-Enhanced ETA Prediction

**Objective**: Predict transit time using graph-enhanced machine learning.

**Models**:

| Model | Description | MAE | RMSE | 15% Accuracy |
|-------|-------------|-----|------|---------------|
| Baseline XGBoost | Trip features only | 0.829 | 1.447 | 23.83% |
| Graph-Enhanced XGBoost | Trip + Node2Vec embeddings | 0.699 | 1.233 | 30.86% |

**Improvement**: 15.7% better MAE, 30% better 15% accuracy

**Feature Importance** (graph-enhanced model):
1. Corridor historical delay factor
2. Source hub betweenness centrality
3. Destination hub bottleneck score
4. Trip distance

**Key Insight**: Network structural position (where a hub sits in the network) is a stronger predictor of delay than trip distance alone.

**Output**: `baseline_model.json`, `enhanced_model.json`, `test_predictions.csv`, `model_benchmark.csv`

---

### Phase 4: FTL vs Carting Decision Framework

**Objective**: Classify optimal route type for each shipment.

**Problem Setup**:
- Binary classification: FTL (1) vs Carting (0)
- Class imbalance: 70% FTL, 30% Carting
- Handled using `scale_pos_weight` parameter in XGBoost

**Features** (56 total):
- Trip features (4): distance, time, day_of_week, is_weekend
- Hub graph metrics (8): betweenness, bottleneck_score, SLA breach, degrees for source and destination
- Corridor stats (5): median_factor, SLA rate, p75_factor, p90_factor, trip_count
- Node2Vec embeddings (32): 16 dimensions for each endpoint

**Results**:

| Metric | Value |
|--------|-------|
| Accuracy | 99.6% |
| ROC-AUC | 0.9998 |
| Precision (FTL) | 99.7% |
| Recall (FTL) | 99.8% |

**Key Finding**: **99.4% of corridors use only ONE route type**

```
Corridors with 1 route type:  2,494
Corridors with both types:       14
```

This reveals that route choice is **structurally determined**, not a free operational decision. The corridor itself dictates whether FTL or Carting is viable based on distance, infrastructure, and traffic patterns.

**Corridor Recommendations**:
- FTL only: 2,546 corridors
- Carting only: 1,935 corridors
- FTL preferred (when both exist): 57 corridors
- Carting preferred (when both exist): 41 corridors

**Scoring Formula** (for flexible corridors):
```
score = 0.6 × median_factor + 0.4 × sla_breach_rate
```
(Lower score wins)

**Output**: `phase4_features.json`, `ftl_carting_model.json`, `ftl_carting_predictions.csv`, `route_decision_framework.csv`

---

## Model Details

### XGBoost Hyperparameters

**ETA Prediction (Phase 3)**:
```python
params = {
    'objective': 'reg:squarederror',
    'max_depth': 6,
    'learning_rate': 0.1,
    'n_estimators': 100,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'random_state': 42
}
```

**Route Classification (Phase 4)**:
```python
params = {
    'objective': 'binary:logistic',
    'max_depth': 6,
    'learning_rate': 0.1,
    'n_estimators': 100,
    'scale_pos_weight': 2.33,  # Handle 70/30 imbalance
    'random_state': 42
}
```

### Node2Vec Configuration

```python
from node2vec import Node2Vec
node2vec = Node2Vec(graph, dimensions=64, walk_length=30, 
                    num_walks=200, workers=1, p=1, q=1)
```

---

## Key Findings

1. **Gurgaon** is the network choke point with 34.5% betweenness centrality—more than one in three optimal delivery routes pass through this hub
2. **Bangalore** is the second critical hub with 23.6% betweenness centrality
3. **34% of corridors (953)** are chronically delayed, causing the majority of SLA breaches
4. **Graph features improve ETA prediction by ~16%** (MAE: 0.829 → 0.699)
5. **99.4% of corridors are structurally dedicated** to one route type—route choice is determined by infrastructure, not management decision
6. **Top 10% of corridors carry 34% of delivery volume**—focusing on high-traffic corridors yields highest ROI
7. **Upgrading top 3 hubs could recover ~Rs 2.3 Crore annually** in revenue

---

## Project Structure

```
.
├── README.md                 # This file
├── pyproject.toml            # Project configuration
├── main.py                   # Entry point
├── data/
│   ├── raw/
│   │   └── delivery_data.csv # Raw operational data
│   └── processed/
│       ├── train_clean.csv   # Cleaned training data
│       ├── test_clean.csv    # Cleaned test data
│       ├── delivery_network.graphml
│       ├── node_metrics.csv
│       ├── corridor_aggregates.csv
│       ├── corridor_stratified.csv
│       ├── chronic_corridors.csv
│       ├── bottleneck_hubs_ranked.csv
│       ├── sla_contribution.csv
│       ├── node2vec_embeddings.csv
│       ├── baseline_model.json
│       ├── enhanced_model.json
│       ├── test_predictions.csv
│       ├── model_benchmark.csv
│       ├── phase4_features.json
│       ├── ftl_carting_model.json
│       ├── ftl_carting_predictions.csv
│       └── route_decision_framework.csv
├── notebooks/
│   ├── phase1_data_pipeline.ipynb
│   ├── phase2_bottleneck_audit.ipynb
│   ├── phase3_graph_models.ipynb
│   ├── phase4_ftl_vs_carting.ipynb
│   └── phase5_outputs_memo.ipynb
├── src/
│   ├── __init__.py
│   └── (utility modules)
└── outputs/
    ├── phase2_visuals/  # 9 charts (hub rankings, corridor analysis, state patterns)
    ├── phase3_visuals/  # 5 charts (feature importance, prediction comparisons)
    ├── phase4_visuals/  # 6 charts (confusion matrix, route distributions)
    └── phase5_visuals/
```

---

## Installation & Setup

### Prerequisites

- Python 3.12+
- 8GB RAM minimum (for graph operations)
- Jupyter Lab or Jupyter Notebook

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/delivery-network-graph-analysis.git
cd delivery-network-graph-analysis

# Install dependencies (using uv - recommended)
uv sync

# Or using pip
pip install -r requirements.txt

# Verify installation
python -c "import pandas; import networkx; import xgboost; print('OK')"

# Start Jupyter Lab
jupyter lab
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | ≥3.0 | Data manipulation |
| numpy | ≥2.4 | Numerical computing |
| networkx | ≥3.6 | Graph operations |
| node2vec | ≥0.4 | Graph embeddings |
| xgboost | ≥3.2 | ML models |
| scikit-learn | ≥1.8 | Evaluation metrics |
| matplotlib | ≥3.10 | Visualization |
| seaborn | ≥0.13 | Statistical plots |
| jupyterlab | ≥4.5 | Interactive notebooks |

---

## Usage

Run the Jupyter notebooks in sequential order to reproduce the full analysis:

### Phase 1: Data Pipeline & Graph Construction
- **File**: `notebooks/phase1_data_pipeline.ipynb`
- **Purpose**: Clean data, engineer features, construct network graph
- **Runtime**: ~5 minutes
- **Key outputs**: `delivery_network.graphml`, `node_metrics.csv`

### Phase 2: Bottleneck & Corridor Audit
- **File**: `notebooks/phase2_bottleneck_audit.ipynb`
- **Purpose**: Identify and rank bottleneck hubs, analyze corridor performance
- **Runtime**: ~3 minutes
- **Key outputs**: `bottleneck_hubs_ranked.csv`, `chronic_corridors.csv`

### Phase 3: Graph-Enhanced ETA Prediction
- **File**: `notebooks/phase3_graph_models.ipynb`
- **Purpose**: Build and compare baseline vs graph-enhanced prediction models
- **Runtime**: ~10 minutes
- **Key outputs**: `enhanced_model.json`, `model_benchmark.csv`

### Phase 4: FTL vs Carting Decision Framework
- **File**: `notebooks/phase4_ftl_vs_carting.ipynb`
- **Purpose**: Classify optimal route type for each corridor
- **Runtime**: ~5 minutes
- **Key outputs**: `ftl_carting_model.json`, `route_decision_framework.csv`

---

## Output Files

### Graph Files
| File | Description |
|------|-------------|
| `delivery_network.graphml` | Full NetworkX directed weighted graph (1,657 nodes, 2,783 edges) |

### Node-Level Outputs
| File | Description |
|------|-------------|
| `node_metrics.csv` | All hub metrics: betweenness, bottleneck_score, degrees, avg delay/SLA |
| `bottleneck_hubs_ranked.csv` | Hubs ranked by composite bottleneck score |
| `node2vec_embeddings.csv` | 64-dimensional Node2Vec embeddings for each hub |

### Corridor-Level Outputs
| File | Description |
|------|-------------|
| `corridor_aggregates.csv` | Per-corridor metrics: median_factor, SLA rate, trip_count |
| `corridor_stratified.csv` | Corridors with route type distribution |
| `chronic_corridors.csv` | Flagged corridors with chronic delays |
| `sla_contribution.csv` | Absolute SLA breaches per corridor |

### Model Outputs
| File | Description |
|------|-------------|
| `baseline_model.json` | XGBoost model (trip features only) |
| `enhanced_model.json` | XGBoost model (with Node2Vec embeddings) |
| `ftl_carting_model.json` | Route type classifier |
| `test_predictions.csv` | Phase 3 test set predictions |
| `model_benchmark.csv` | Model comparison metrics |
| `ftl_carting_predictions.csv` | Phase 4 predictions |
| `route_decision_framework.csv` | Per-corridor route recommendations |

---

## Visualizations

### Phase 2 Outputs (9 charts)
- Hub bottleneck ranking chart
- Top 20 bottleneck hubs bar chart
- Corridor delay distribution histogram
- SLA breach rate by state
- Time-of-day performance patterns
- Route type comparison (FTL vs Carting delays)
- Hub degree distribution
- Network density analysis
- Correlation heatmap

### Phase 3 Outputs (5 charts)
- Feature importance (baseline model)
- Feature importance (graph-enhanced model)
- Actual vs Predicted scatter plot
- Residual distribution
- Model comparison bar chart

### Phase 4 Outputs (6 charts)
- Confusion matrix heatmap
- Route type distribution pie chart
- Feature importance (classifier)
- Corridor recommendation summary
- Score distribution by route type
- Model ROC curve

---

## Future Enhancements

### Short Term (0-3 months)
- **Temporal Analysis**: Track bottleneck changes over time (daily/weekly/monthly)
- **Route Optimization**: Algorithmic bypass of high-delay hubs

### Medium Term (3-6 months)
- **Interactive Dashboard**: Streamlit/Dash dashboard for operations team
- **What-if Modeling**: Simulate impact of hub capacity changes

### Long Term (6-12 months)
- **External Data Integration**: Weather, traffic, holidays
- **GNN Implementation**: Graph Neural Networks for delay prediction
- **Real-time Scoring**: API for live corridor performance scoring

---

## Technical Notes

- **Memory**: Graph operations require ~4GB RAM; embeddings require additional ~2GB
- **Runtime**: Full pipeline runs in ~25 minutes on standard hardware
- **Storage**: Processed data and models require ~500MB disk space
- **Python Version**: Requires Python 3.12+ (uses modern type hints and pattern matching)

---

## License

MIT License - See LICENSE file for details.

---

## Acknowledgments

- Delhivery Network Operations Team for data access and domain expertise
- Built with open-source tools: NetworkX, Node2Vec, XGBoost, scikit-learn

---

*Built for Delhivery Network Operations Team | May 2026*