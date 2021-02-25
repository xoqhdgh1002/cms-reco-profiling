#!/usr/bin/python
import os
from itertools import ifilter
import yaml

dirname = "/eos/cms/store/user/cmsbuild/profiling/data/"
arch = "slc7_amd64_gcc900"

def getReleases(dirname):
    ls = os.listdir(dirname)
    ls = [x for x in ls if x.startswith("CMSSW_")]
    return ls

def grep(fn, match):
    ret = []
    with open(fn) as fi:
        for line in fi.readlines():
            if match in line:
                ret.append(line)
    return ret

def getCPUEvent(fn):
    result = grep(fn, "TimeReport       event loop CPU/event =")[0]
    cpu_event = float(result.split("=")[1]) 
    return cpu_event

def getPeakRSS(fn):
    result = grep(fn, "RSS")
    rss_vals = [float(r.split()[7]) for r in result]
    return max(rss_vals)

def parseStep(dirname, release, arch, step):
    tmi = os.path.join(dirname, release, arch, "{}_TimeMemoryInfo.log".format(step))
    cpu_event = getCPUEvent(tmi)
    peak_rss = getPeakRSS(tmi)
    return {"cpu_event": cpu_event, "peak_rss": peak_rss}

def parseRelease(dirname, release, arch):
    step3_data = parseStep(dirname, release, arch, "step3")
    step4_data = parseStep(dirname, release, arch, "step4")
    
    ret = {}
    for k, v in step3_data.items():
        ret["step3_" + k] = v
    for k, v in step4_data.items():
        ret["step4_" + k] = v

    return ret

if __name__ == "__main__":
    releases = getReleases(dirname)

    releases_str = ""
    results = {}
    for release in releases:
        parsed = parseRelease(dirname, release, arch)
        results[release] = parsed
        results[release]["arch"] = arch

    print(yaml.dump(results, default_flow_style=False))
