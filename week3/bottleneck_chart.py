import pandas as pd
import matplotlib.pyplot as plt

file = "week3/outputs/transition_waiting_summary.csv"

df = pd.read_csv(file)

top = df.head(5)

plt.figure(figsize=(10, 6))

plt.barh(
    top["transition"],
    top["average_wait_minutes"]
)

plt.xlabel("Average Waiting Time (minutes)")
plt.ylabel("Clinical Transition")
plt.title("Top 5 Potential Bottlenecks")

plt.tight_layout()

plt.savefig(
    "week3/outputs/top_bottlenecks.png",
    dpi=300
)

plt.show()