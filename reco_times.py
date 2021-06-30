import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import yaml
import datetime
import pandas as pd

def stripArch(release_arch):
    idx = release_arch.index("slc")
    return release_arch[:idx-1]

def releaseTimePlot(df):
    plot_order = [
        '11_2_0_pre2',
        '11_2_0_pre3',
        '11_2_0_pre4',
        '11_2_0_pre5',
        '11_2_0_pre6',
        '11_2_0_pre7',
        '11_2_0_pre8',
        '11_2_0_pre9',
        '11_2_0_pre10',
        '11_2_0_pre11',
    #    '11_2_0',
        '11_3_0_pre1',
        '11_3_0_pre2',
        '11_3_0_pre3',
        '11_3_0_pre4',
        '11_3_0_pre5',
        '11_3_0_pre6', 
    #    '11_3_0',
        '12_0_0_pre1',
        '12_0_0_pre2',
        '12_0_0_pre3'
    ]
    
    idx_order = [list(df.label).index(p) for p in plot_order]
    sdf = df.iloc[idx_order]
    
    sdf.plot("release_date", ["total_time", "reco_time", "output_time"], marker=".", figsize=(8,4))
    
    #plt.xticks(range(len(df)), df["label"], rotation=90);
    plt.ylabel("average CPU time / event")
    plt.xlabel("release date")
    plt.ylim(0, 150)
    plt.savefig("results/release_timing.pdf")

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
    for rel in releases:
        tev = data[rel]["23434p21"]["step3"]["cpu_event"]
        tout = data[rel]["23434p21"]["step3"]["poolout_avg"]

        reldate = datetime.datetime.strptime(data[rel]["release_date"], "%Y-%m-%dT%H:%M:%SZ")
        dates.append(reldate)
        reco_times.append(tev - tout)
        total_times.append(tev)
        output_times.append(tout)
 
        label = rel.replace("CMSSW_", "")
        labels.append(label)

    df = pd.DataFrame()
    df["release_date"] = dates
    df["reco_time"] = reco_times
    df["total_time"] = total_times
    df["output_time"] = output_times
    df["label"] = labels

    df = df.sort_values(by="release_date")
    df.to_csv("results/release_timing.csv") 

    releaseTimePlot(df)
