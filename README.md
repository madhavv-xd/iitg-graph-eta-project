# Delivery Network Graph Analysis

A graph-based network analysis system for identifying bottleneck hubs, analyzing corridor performance, and optimizing logistics operations at Delhivery (a major Indian logistics company).

## Quick Stats

| Metric | Value |
|--------|-------|
| Total Hubs | 1,657 |
| Total Corridors | 2,783 |
| SLA Breach Rate | 84.5% |
| Median Delay Factor | 1.7x |

## Project Overview

This project applies **classical graph theory** and **network analysis techniques** to:
- Construct a directed weighted graph representing the delivery network
- Identify structural bottlenecks using centrality metrics
- Analyze corridor-level performance patterns
- Predict ETAs using graph-enhanced machine learning
- Classify optimal route types (FTL vs Carting) for shipments

### Core Metrics

| Metric | Description |
|--------|-------------|
| **segment_factor** | Actual time / OSRM time (values > 1 = delays) |
| **SLA breach** | Flag when factor > 1.2 (20% over estimate) |
| **Betweenness Centrality** | How often a hub lies on shortest paths |
| **Bottleneck Score** | Composite: 35% betweenness + 25% delay + 25% SLA + 15% out-degree |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1: Data Pipeline & Graph Construction                   │
│  Phase 2: Bottleneck & Corridor Audit                           │
│  Phase 3: Graph-Enhanced ETA Prediction                        │
│  Phase 4: FTL vs Carting Decision Framework                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Data Pipeline & Graph Construction

**Data Cleaning**: Removed 2,600 invalid records (non-positive segment_factor).

**Feature Engineering**:
- Time buckets: night, early_morning, morning, afternoon, evening, late_night
- SLA breach flag (factor > 1.2)
- Delay factor capped at 99th percentile

**Graph Construction**:
- 1,657 nodes (distribution hubs)
- 2,783 edges (corridors)
- Edge weight = median_factor (delay indicator)

**Node Metrics**: betweenness centrality, bottleneck score, degrees, avg delay/SLA per hub.

---

## Phase 2: Bottleneck & Corridor Audit

**Hub-Level Audit**: All 1,657 hubs ranked by bottleneck score. Top hubs identified as priority intervention targets.

**Corridor-Level Audit**: 
- 953 of 2,783 corridors (34.2%) flagged as chronically delayed (factor >1.2, SLA >50%, trips >10)
- SLA contribution metric: absolute late deliveries per corridor

**Network-Level Audit**: State patterns, time-of-day patterns, route type comparisons.

---

## Phase 3: Graph-Enhanced ETA Prediction

Compares baseline XGBoost (trip features only) vs graph-enhanced model (with Node2Vec embeddings).

| Model | MAE | RMSE | 15% Accuracy |
|-------|-----|------|---------------|
| Baseline XGBoost | 0.829 | 1.447 | 23.83% |
| Graph-Enhanced | 0.699 | 1.233 | 30.86% |

**Improvement: 15.7% better MAE** with graph features.

**Node2Vec Configuration**: 64 dimensions, 30 walk length, 200 walks per node, captures local + global structure.

---

## Phase 4: FTL vs Carting Decision Framework

An XGBoost classifier that recommends the optimal route type for each shipment.

**Problem Setup**:
- Target: FTL (1) or Carting (0)
- Class imbalance: 70% FTL, 30% Carting (handled with scale_pos_weight)

**Features (56 total)**:
- Trip features: distance, time, day_of_week, weekend flag
- Hub graph metrics: betweenness, bottleneck_score, SLA breach, degrees (source + destination)
- Corridor stats: median_factor, SLA rate, p75/p90 factors, trip_count
- Node2Vec embeddings: 32 dimensions (16 per endpoint)

**Results**:

| Metric | Value |
|--------|-------|
| Accuracy | 99.6% |
| ROC-AUC | 0.9998 |

**Key Finding**: 99.4% of corridors use only ONE route type. Route choice is structurally determined, not freely chosen.

```
Corridors with 1 route type:  2,494
Corridors with both types:       14
```

**Corridor Recommendations**:
- FTL only: 2,546 corridors
- Carting only: 1,935 corridors
- FTL preferred: 57 corridors (when both exist)
- Carting preferred: 41 corridors (when both exist)

**Scoring Formula**:
```
score = 0.6 × median_factor + 0.4 × sla_breach_rate
```
(Lower score wins)

---

## Key Findings

1. **Gurgaon** is the network choke point (35% betweenness centrality)
2. **Bangalore** is second critical hub (23% betweenness)
3. **34% of corridors** are chronically delayed
4. **Top 10% of corridors** carry 34% of delivery volume
5. **Graph features improve ETA prediction** by ~16% (Phase 3)
6. **Route type is corridor-specific** - 99.4% of corridors dedicated to one mode (Phase 4)

---

## Project Structure

```
.
├── README.md
├── pyproject.toml
├── data/
│   ├── raw/delivery_data.csv
│   └── processed/
│       ├── train_clean.csv, test_clean.csv
│       ├── delivery_network.graphml
│       ├── node_metrics.csv, corridor_aggregates.csv
│       ├── corridor_stratified.csv, chronic_corridors.csv
│       ├── bottleneck_hubs_ranked.csv, sla_contribution.csv
│       ├── node2vec_embeddings.csv
│       ├── baseline_model.json, enhanced_model.json
│       ├── test_predictions.csv, model_benchmark.csv
│       ├── phase4_features.json, ftl_carting_model.json
│       ├── ftl_carting_predictions.csv
│       └── route_decision_framework.csv
├── notebooks/
│   ├── phase1_data_pipeline.ipynb
│   ├── phase2_bottleneck_audit.ipynb
│   ├── phase3_graph_models.ipynb
│   └── phase4_ftl_vs_carting.ipynb
├── src/
│   ├── pipeline.py, features.py, graph_builder.py, utils.py
└── outputs/
    ├── phase2_visuals/ (9 charts)
    ├── phase3_visuals/ (5 charts)
    └── phase4_visuals/ (6 charts)
```

---

## Installation & Setup

```bash
# Using uv (recommended)
uv sync

# Or pip
pip install -r requirements.txt

# Start Jupyter Lab
jupyter lab
```

**Dependencies**: pandas, numpy, networkx, xgboost, node2vec, matplotlib, seaborn, scikit-learn, jupyterlab

---

## Usage

Run notebooks in order:
1. `phase1_data_pipeline.ipynb` - Graph construction
2. `phase2_bottleneck_audit.ipynb` - Bottleneck analysis
3. `phase3_graph_models.ipynb` - ETA prediction
4. `phase4_ftl_vs_carting.ipynb` - Route type classifier

---

## Output Files

| File | Description |
|------|-------------|
| `delivery_network.graphml` | Full NetworkX graph |
| `node_metrics.csv` | Hub metrics (betweenness, bottleneck score, etc.) |
| `corridor_aggregates.csv` | Corridor-level metrics |
| `bottleneck_hubs_ranked.csv` | Ranked bottleneck hubs |
| `chronic_corridors.csv` | Chronically delayed corridors |
| `ftl_carting_model.json` | Phase 4 classifier |
| `route_decision_framework.csv` | Per-corridor route recommendations |

---

## Future Enhancements

- Temporal analysis (track bottleneck changes over time)
- Route optimization (bypass high-delay hubs)
- Interactive dashboard (Streamlit/Dash)
- What-if scenario modeling
- External data (weather, traffic, holidays)
- GNN implementation for delay prediction