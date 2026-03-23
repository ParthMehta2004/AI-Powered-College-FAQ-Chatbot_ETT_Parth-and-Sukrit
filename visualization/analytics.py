import pandas as pd
import matplotlib.pyplot as plt

def show_stats():
    df = pd.read_csv("logs.csv")
    top = df["question"].value_counts().head(5)

    plt.bar(top.index, top.values)
    plt.xticks(rotation=45)
    plt.title("Top Questions")
    plt.show()
