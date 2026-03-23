import csv
from datetime import datetime

def log_query(question, answer):
    with open("logs.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), question, answer])
