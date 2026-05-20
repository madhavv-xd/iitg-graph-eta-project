import os
import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Delhivery Network Intelligence API",
    description="Graph-based logistics analytics backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load data on startup ──────────────────────────────────────
DATA_DIR = os.getenv("DATA_DIR", "../data/processed")

with open(f"{DATA_DIR}/frontend_data.json") as f:
    frontend_data = json.load(f)

node_metrics = pd.read_csv(f"{DATA_DIR}/node_metrics.csv")
corridor_agg = pd.read_csv(f"{DATA_DIR}/corridor_aggregates.csv")
benchmark    = pd.read_csv(f"{DATA_DIR}/model_benchmark.csv")

print(f"Data loaded — {len(node_metrics)} hubs, {len(corridor_agg)} corridors")


# ── Models ────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    source_hub_id: str
    dest_hub_id: str
    hour: int           # 0-23
    route_type: str     # FTL or Carting
    osrm_time: float    # hours


class RouteRequest(BaseModel):
    source_hub_id: str
    dest_hub_id: str
    hour: int
    day_of_week: int    # 0=Monday, 6=Sunday


# ── Routes ────────────────────────────────────────────────────

@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.get("/api/overview")
def get_overview():
    """Key network stats for dashboard KPI cards"""
    return frontend_data["overview"]


@app.get("/api/hubs")
def get_hubs(limit: int = 20):
    """Top bottleneck hubs ranked by score"""
    hubs = node_metrics.sort_values("bottleneck_score", ascending=False).head(limit)
    return hubs[[
        "hub_id","hub_name","state","bottleneck_rank",
        "betweenness_centrality","avg_outgoing_sla_breach",
        "avg_outgoing_factor","bottleneck_score",
        "in_degree","out_degree"
    ]].to_dict("records")


@app.get("/api/hub/{hub_id}")
def get_hub_detail(hub_id: str):
    """Detailed stats for a specific hub"""
    hub = node_metrics[node_metrics["hub_id"] == hub_id]
    if hub.empty:
        raise HTTPException(status_code=404, detail="Hub not found")

    hub_row = hub.iloc[0].to_dict()

    # Outgoing corridors
    out_corridors = corridor_agg[
        corridor_agg["source_center"] == hub_id
    ].sort_values("sla_breach_rate", ascending=False).head(10)

    hub_row["outgoing_corridors"] = out_corridors[[
        "destination_center","median_factor",
        "sla_breach_rate","trip_count"
    ]].to_dict("records")

    return hub_row


@app.get("/api/corridors")
def get_corridors(limit: int = 50, min_trips: int = 5):
    """Chronic corridors ranked by SLA contribution"""
    chronic = corridor_agg[
        (corridor_agg["median_factor"] > 1.2) &
        (corridor_agg["sla_breach_rate"] > 0.5) &
        (corridor_agg["trip_count"] >= min_trips)
    ].copy()
    chronic["sla_contribution"] = chronic["sla_breach_rate"] * chronic["trip_count"]
    chronic = chronic.sort_values("sla_contribution", ascending=False).head(limit)
    return chronic[[
        "source_center","destination_center",
        "median_factor","sla_breach_rate","trip_count","sla_contribution"
    ]].to_dict("records")


@app.get("/api/benchmark")
def get_benchmark():
    """Model performance comparison"""
    return benchmark.to_dict("records")


@app.get("/api/graph")
def get_graph(top_n: int = 50):
    """Network graph data for visualization"""
    return frontend_data["graph"]


@app.post("/api/predict")
def predict_eta(req: PredictRequest):
    """
    Predict delivery ETA using graph-enhanced model.
    Returns OSRM estimate + graph-enhanced estimate + SLA risk.
    """
    src = node_metrics[node_metrics["hub_id"] == req.source_hub_id]
    dst = node_metrics[node_metrics["hub_id"] == req.dest_hub_id]

    if src.empty:
        raise HTTPException(status_code=404, detail=f"Source hub {req.source_hub_id} not found")
    if dst.empty:
        raise HTTPException(status_code=404, detail=f"Destination hub {req.dest_hub_id} not found")

    src_row = src.iloc[0]
    dst_row = dst.iloc[0]

    # Corridor historical factor
    corridor = corridor_agg[
        (corridor_agg["source_center"] == req.source_hub_id) &
        (corridor_agg["destination_center"] == req.dest_hub_id)
    ]
    corr_factor = corridor.iloc[0]["median_factor"] if not corridor.empty else 1.8

    # Time boost
    hour = req.hour
    time_boost = 1.15 if (hour >= 22 or hour <= 4) else 0.95 if (8 <= hour <= 18) else 1.05

    # Route boost
    route_boost = 1.12 if req.route_type == "Carting" else 1.0

    # Graph-enhanced factor
    graph_factor = (
        0.4 * corr_factor +
        0.3 * src_row["avg_outgoing_factor"] +
        0.2 * (1 + src_row["betweenness_centrality"] * 2) +
        0.1 * (1 + dst_row["avg_incoming_factor"] * 0.5)
    )

    graph_eta   = req.osrm_time * graph_factor * time_boost * route_boost
    sla_risk    = min(0.99, src_row["avg_outgoing_sla_breach"] * 0.6 + dst_row["avg_outgoing_sla_breach"] * 0.4)
    risk_level  = "HIGH" if sla_risk > 0.85 else "MEDIUM" if sla_risk > 0.70 else "LOW"

    return {
        "osrm_estimate_hours" : round(req.osrm_time, 2),
        "graph_eta_hours"     : round(graph_eta, 2),
        "delay_factor"        : round(graph_eta / req.osrm_time, 3),
        "sla_risk_probability": round(sla_risk, 3),
        "risk_level"          : risk_level,
        "source_hub": {
            "name"          : src_row["hub_name"],
            "betweenness"   : round(src_row["betweenness_centrality"], 4),
            "sla_breach"    : round(src_row["avg_outgoing_sla_breach"], 3),
            "bottleneck_rank": int(src_row["bottleneck_rank"]),
        },
        "dest_hub": {
            "name"          : dst_row["hub_name"],
            "sla_breach"    : round(dst_row["avg_outgoing_sla_breach"], 3),
            "bottleneck_rank": int(dst_row["bottleneck_rank"]),
        },
        "corridor_historical_factor": round(corr_factor, 3),
        "recommendation": (
            f"Use {'FTL' if req.route_type == 'Carting' else req.route_type} on this corridor. "
            f"SLA risk is {risk_level} ({sla_risk:.1%}). "
            f"Graph model predicts {graph_eta:.1f}h vs OSRM's {req.osrm_time:.1f}h."
        )
    }


@app.post("/api/route-decision")
def route_decision(req: RouteRequest):
    """
    Recommend FTL or Carting for a given corridor and time.
    """
    src = node_metrics[node_metrics["hub_id"] == req.source_hub_id]
    dst = node_metrics[node_metrics["hub_id"] == req.dest_hub_id]

    if src.empty or dst.empty:
        raise HTTPException(status_code=404, detail="Hub not found")

    src_row = src.iloc[0]
    is_night   = req.hour >= 22 or req.hour <= 4
    is_weekend = req.day_of_week >= 5

    # FTL scores better on high-betweenness corridors
    ftl_score    = src_row["betweenness_centrality"] * 0.5 + (0.1 if is_night else 0)
    carting_score= (1 - src_row["betweenness_centrality"]) * 0.5 + (0.05 if is_weekend else 0)

    recommendation = "FTL" if ftl_score >= carting_score else "Carting"
    confidence     = abs(ftl_score - carting_score) / max(ftl_score, carting_score)

    return {
        "recommendation": recommendation,
        "confidence"    : round(confidence, 3),
        "ftl_score"     : round(ftl_score, 4),
        "carting_score" : round(carting_score, 4),
        "reasoning": (
            f"{'High' if src_row['betweenness_centrality'] > 0.1 else 'Low'} betweenness source hub "
            f"({'night' if is_night else 'day'} departure, "
            f"{'weekend' if is_weekend else 'weekday'}). "
            f"{recommendation} recommended."
        )
    }


@app.get("/api/state-stats")
def get_state_stats():
    """State-level aggregated performance"""
    return frontend_data["state_stats"]


@app.get("/health")
def health():
    return {"status": "ok", "hubs": len(node_metrics), "corridors": len(corridor_agg)}


# Mount static files last
app.mount("/", StaticFiles(directory="static", html=True), name="static")
