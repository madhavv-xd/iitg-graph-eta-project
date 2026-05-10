# Delivery Network Analysis

Analysis of delivery network performance using graph-based approaches to identify bottlenecks and optimize logistics operations.

## Project Overview

This project analyzes delivery network data to identify bottleneck hubs and understand delivery performance patterns. It uses network analysis techniques and graph neural networks to process logistics data.

## Dataset

- **Source**: delivery_data.csv
- **Total Records**: 142,267 trips
- **Route Types**: FTL (98,729), Carting (43,538)
- **SLA Breach Rate**: 84.47%

## Network Statistics

| Metric | Value |
|--------|-------|
| Nodes (Hubs) | 1,657 |
| Edges (Routes) | 2,783 |
| Density | 0.001014 |
| Connected Components | 64 |
| Largest Component | 1,353 nodes |

## Top Bottleneck Hubs

1. **Gurgaon_Bilaspur_HB** (Haryana) - Score: 0.733
2. **Bangalore_Nelmngla_H** (Karnataka) - Score: 0.567
3. **Helencha_ColnyDPP_D** (West Bengal) - Score: 0.505
4. **Simlapal_Central_D_1** (West Bengal) - Score: 0.503
5. **RampuraPhul_DC** (Punjab) - Score: 0.503

## Project Structure

```
.
├── main.py              # Main entry point
├── gnn.ipynb            # Graph Neural Network analysis notebook
├── delivery_data.csv    # Raw delivery data
├── outputs/
│   ├── delivery_network.graphml   # Network graph file
│   ├── graph_summary.json         # Network statistics
│   ├── node_metrics.csv           # Node-level metrics
│   ├── corridor_aggregates.csv    # Corridor performance
│   ├── corridor_stratified.csv    # Stratified corridor data
│   ├── train_clean.csv            # Training data
│   └── test_clean.csv             # Test data
└── pyproject.toml       # Project dependencies
```

## Requirements

- Python 3.12+
- See `pyproject.toml` for dependencies

## Setup

```bash
# Install dependencies
uv sync  # or pip install -r requirements.txt
```

## Usage

Run the main script:
```bash
python main.py
```

Open the notebook for analysis:
```bash
jupyter lab gnn.ipynb
```

## Phase 1 Status

- [x] Data preprocessing and cleaning
- [x] Network graph construction
- [x] Bottleneck identification
- [x] Performance metrics extraction

## Output Files

- `graph_summary.json` - Summary of network metrics
- `node_metrics.csv` - Per-hub performance metrics
- `delivery_network.graphml` - Graph representation for visualization
- `corridor_*.csv` - Corridor-level analysis data