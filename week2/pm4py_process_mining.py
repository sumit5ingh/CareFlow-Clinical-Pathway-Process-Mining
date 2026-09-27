import pandas as pd

df = pd.read_csv("careflow_event_log_clean.csv")

print(df.head())
print(df.columns)
print(df.shape)

import pm4py

log = pm4py.format_dataframe(
    df,
    case_id="Case_ID",
    activity_key="Activity_Name",
    timestamp_key="Timestamp"
)

print(log.head())

from pm4py.algo.discovery.alpha import algorithm as alpha_miner

net, initial_marking, final_marking = alpha_miner.apply(log)



from pm4py.visualization.petri_net import visualizer as pn_visualizer

gviz = pn_visualizer.apply(
    net,
    initial_marking,
    final_marking
)

pn_visualizer.view(gviz)


from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner

heu_net = heuristics_miner.apply_heu(log)

from pm4py.visualization.heuristics_net import visualizer as hn_visualizer

gviz = hn_visualizer.apply(heu_net)

hn_visualizer.view(gviz)

from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualizer

dfg = dfg_discovery.apply(log)

gviz = dfg_visualizer.apply(dfg)

dfg_visualizer.view(gviz)

from collections import Counter

traces = []

for case_id, group in log.groupby("Case_ID"):
    activities = tuple(group.sort_values("Timestamp")["Activity_Name"])
    traces.append(activities)

trace_counts = Counter(traces)

for trace, count in trace_counts.most_common(10):
    print(count, ":", " → ".join(trace))


print("Number of cases:", log["Case_ID"].nunique())

print("Number of events:", len(log))

print(
    "Unique activities:",
    log["Activity_Name"].nunique()
)

print(
    log["Activity_Name"].value_counts()
)