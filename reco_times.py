import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import yaml
import datetime
import pandas as pd

def stripArch(release_arch):
    idx = release_arch.index("slc")
    return release_arch[:idx-1]

with open('results/summary.yaml') as fi:
    data = yaml.full_load(fi)

    renamed_data = {}
    for rel in data.keys():
        renamed_data[stripArch(rel)] = data[rel]
    data = renamed_data

    releases = sorted(list(data.keys()))

    dates = []
    reco_times = []
    total_times = []
    output_times = []
    labels = []
    workflows = []
    peak_rss = []
    for rel in releases:
        print(rel)
        for wf in ["11834p21", "29234p21", "20634p21", "23434p21", "34834p21", "35234p21"]:
            if wf in data[rel]: 
                tev = data[rel][wf]["step3"]["cpu_event"]
                tout = data[rel][wf]["step3"]["poolout_avg"]

                reldate = datetime.datetime.strptime(data[rel]["release_date"], "%Y-%m-%dT%H:%M:%SZ")
                dates.append(reldate)
                reco_times.append(tev - tout)
                total_times.append(tev)
                output_times.append(tout)
                peak_rss.append(data[rel][wf]["step3"]["peak_rss"])
                workflows.append(wf)

                label = rel.replace("CMSSW_", "")
                labels.append(label)

    df = pd.DataFrame()
    df["release_date"] = dates
    df["reco_time"] = reco_times
    df["total_time"] = total_times
    df["output_time"] = output_times
    df["label"] = labels
    df["workflow"] = workflows
    df["peak_rss"] = peak_rss

    df = df.sort_values(by=["release_date", "workflow"])
    df.to_csv("results/release_timing.csv") 
