# Network Operations Strategy Memo
**Delhivery — Graph-Based Network Intelligence Analysis**
**Prepared for: Head of Network Operations**
**Date: May 2026**
**Classification: Internal — Operations**

---

## Executive Summary

A graph-based analysis of Delhivery's logistics network reveals that
**84.5% of all deliveries currently breach SLA**, with actual
transit times running a median of **1.7× longer** than
OSRM predictions. The root cause is not uniformly distributed — it is
concentrated in a small number of structurally critical hubs and
chronically delayed corridors.

This analysis identifies the **top 5 bottleneck hubs** responsible for a
disproportionate share of SLA failures, quantifies the revenue at risk,
and provides specific intervention recommendations for each hub.
Upgrading the top 3 hubs alone is projected to reduce SLA breaches by
approximately **20%**, recovering an estimated
**Rs 2.3 Crore** in annual revenue.

---

## 1. Network Overview

| Metric | Value |
|--------|-------|
| Total hubs in network | 1,657 |
| Total corridors | 2,783 |
| Unique trips analysed | 14,817 |
| Overall SLA breach rate | 84.5% |
| Median delay factor (actual / OSRM) | 1.70× |
| Late deliveries per day (estimated) | 417 |
| Annual revenue at risk | Rs 11.4 Crore |

The network is sparse — most corridors carry fewer than 10 trips.
Traffic is distributed across many routes rather than concentrated
in a few highways, which means **hub-level interventions yield higher
leverage than corridor-level fixes.**

---

## 2. Top 5 Bottleneck Hubs

Hubs are ranked by a composite bottleneck score combining structural
importance (betweenness centrality), average delay factor, SLA breach
rate, and connectivity. A higher score means greater negative impact
on the overall network.

### Hub 1 — Gurgaon_Bilaspur_HB (Haryana), Haryana
**Bottleneck Score: 0.733 — Highest in network**

This hub sits on **34.5% of all critical
delivery paths** in the network — more than one in three optimal routes
passes through here. With 49 outgoing corridors and a SLA
breach rate of **79.4%** on outgoing trips, delays
here cascade across the largest downstream surface area of any hub.

- Betweenness centrality : 0.345
- Avg outgoing delay     : 1.60×
- SLA breach rate        : 79.4%
- **Recommended intervention: Parallel route addition + capacity upgrade**

---

### Hub 2 — Bangalore_Nelmngla_H (Karnataka), Karnataka
**Bottleneck Score: 0.573**

The second most critical hub, serving as a major gateway with
35 outgoing corridors. Betweenness centrality of
0.236 indicates it sits on nearly a quarter of
all critical network paths. SLA breach rate of
77.4% makes it the second largest contributor
to late deliveries.

- Betweenness centrality : 0.236
- Avg outgoing delay     : 1.54×
- SLA breach rate        : 77.4%
- **Recommended intervention: Capacity upgrade + route type shift**

---

### Hub 3 — Ranaghat_ArickDPP_D (West Bengal), West Bengal
**Bottleneck Score: 0.505**

Unlike the top two hubs which score on betweenness, this hub scores
due to an extreme delay factor of **11.6×** —
the highest average outgoing delay in the entire network. Every
shipment leaving this hub takes over 11 times longer than predicted.
This is a facility-level problem, not a structural one.

- Betweenness centrality : 0.002
- Avg outgoing delay     : 11.6×
- SLA breach rate        : 100.0%
- **Recommended intervention: Review and reassign route type**

---

### Hub 4 — Helencha_ColnyDPP_D (West Bengal), West Bengal
**Bottleneck Score: 0.505**

Extreme delay factor of 11.6× with 100% SLA breach
rate on all outgoing trips. Impact is localised but severity warrants
immediate attention.

- **Recommended intervention: Facility upgrade**

---

### Hub 5 — Faridabad_Old (Haryana), Haryana
**Bottleneck Score: 0.503**

Identical delay profile — 11.6× delay factor and
100% SLA breach rate. Two of the top 5 hubs are in Haryana,
suggesting a state-level infrastructure issue worth investigating.

- **Recommended intervention: Facility upgrade**

---

## 3. Chronic Corridor Analysis

Of 2783 corridors in the network, **953
(34.3%) are chronically delayed** — actual transit time consistently
exceeds OSRM predictions by more than 20% on more than half of all trips.

Top corridors by SLA breach contribution (breach rate × volume):

| Corridor | Delay Factor | SLA Breach | Trips | SLA Contribution |
|----------|-------------|------------|-------|-----------------|
| Bangalore → Bengaluru | 1.45× | 74.3% | 151 | 112 |
| Bhiwandi → Mumbai Hub (Maharashtra) | 2.24× | 96.9% | 105 | 102 |
| Mumbai → Bhiwandi | 2.48× | 97.9% | 99 | 97 |
| Bangalore → Bengaluru | 1.44× | 74.6% | 127 | 95 |
| Bengaluru → Bengaluru | 1.53× | 70.4% | 121 | 85 |
| Pune → Bhiwandi | 1.38× | 74.0% | 107 | 79 |
| Bhiwandi → Mumbai | 2.44× | 100.0% | 78 | 78 |
| Bengaluru → Bangalore | 1.40× | 73.9% | 102 | 75 |

The Bhiwandi–Mumbai cluster accounts for the highest contribution,
driven by high volume combined with near-100% breach rates.

---

## 4. ETA Model Performance

A graph-enhanced model was benchmarked against a standard baseline:

| Metric | Baseline | Graph-Enhanced | Improvement |
|--------|----------|----------------|-------------|
| MAE | 0.829 | 0.700 | -15.6% |
| 15% Accuracy | 23.8% | 31.0% | +30.0% |

The graph model predicts ETAs **15.6% more accurately** by
incorporating hub structural position and corridor history.
The most important predictive features were corridor historical
delay factor and source hub betweenness — confirming that network
position, not just trip distance, drives delivery time.

---

## 5. Route Type Findings

- 99.4% of corridors are structurally dedicated to one route type
- On corridors where both operate: Carting 1.96× vs FTL 1.78× median delay
- Of 4579 corridors: 2603 recommended FTL, 1976 recommended Carting

Route type on most corridors is not a freely interchangeable decision —
it is structurally determined by the corridor itself.

---

## 6. Recommendations

### Immediate (0–3 months)
1. **Gurgaon hub** — Parallel route + capacity upgrade.
   Affects 34.5% of all network paths.
2. **Bangalore hub** — Facility audit + capacity upgrade.
3. **Ranaghat & Helencha** — Route assignment review.

### Medium-term (3–6 months)
4. **Bhiwandi–Mumbai corridor cluster** — Priority scheduling or dedicated capacity.
5. **Deploy graph-enhanced ETA model** — Replace OSRM for customer-facing promises.

### Strategic (6–12 months)
6. **Haryana hub infrastructure** — State-level review warranted.
7. **Dynamic route type tooling** — Build operational UI for the 14 flexible corridors.

---

## 7. Revenue Impact

| Scenario | Deliveries Recovered/Day | Annual Revenue Recovered |
|----------|--------------------------|--------------------------|
| Top 3 hubs upgraded | 83 | Rs 2.3 Crore |
| Top 5 hubs upgraded | 117 | Rs 3.2 Crore |
| All chronic corridors | 188 | Rs 5.1 Crore |

*Based on Rs 750/trip conservative estimate.
Replace with actual SLA penalty per contract for precise figures.*

---

## 8. Methodology

Network modelled as a directed weighted graph:
1,657 hubs · 2,783 corridors · 14,817 trips

ETA model: XGBoost with node2vec graph embeddings.
FTL vs Carting: XGBoost classifier, 99.6% accuracy.
Dataset: approximately 30 days of operations.

---
*Delhivery Graph Intelligence System — Data Science Team*
