#!/usr/bin/env python
import os
from itertools import ifilter
import yaml
import subprocess

dirname = "/eos/cms/store/user/cmsbuild/profiling/data/"
arch = "slc7_amd64_gcc900"

def getFileSize(fn):
    ret = os.path.getsize(fn)
    return ret

def makeIgProfSummaryMEM(infile, outfile):
    os.system("igprof-analyse --top 1000 --demangle --gdb -r MEM_LIVE {} | bzip2 -9 > {}".format(infile, outfile))

def makeIgProfSummaryCPU(infile, outfile):
    os.system("igprof-analyse --top 1000 --demangle --gdb -r PERF_TICKS {} | bzip2 -9 > {}".format(infile, outfile))

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

def parseStep(dirname, release, arch, wf, step):
    base = os.path.join(dirname, release, arch, wf)
    tmi = os.path.join(base, "{}_TimeMemoryInfo.log".format(step))
    rootfile = os.path.join(base, "{}.root.unused".format(step))
    cpu_event = getCPUEvent(tmi)
    peak_rss = getPeakRSS(tmi)
    file_size = getFileSize(rootfile)

    igprof_outpath = "results/igprof/{}/{}/{}".format(release.replace("CMSSW_", ""), wf, step)
    if not os.path.isdir(igprof_outpath):
        os.makedirs(igprof_outpath)
    makeIgProfSummaryCPU(os.path.join(base, "{}_igprofCPU.gz".format(step)), os.path.join(igprof_outpath, "cpu.txt.bz2"))
    makeIgProfSummaryMEM(os.path.join(base, "{}_igprofMEM.gz".format(step)), os.path.join(igprof_outpath, "mem.txt.bz2"))

    return {"cpu_event": cpu_event, "peak_rss": peak_rss, "file_size": file_size}

def getWorkflows(dirname, release, arch):
    ls = os.listdir(os.path.join(dirname, release, arch))
    ls = [x for x in ls if "." in x and int(x.split(".")[0])]
    return ls

def parseRelease(dirname, release, arch):
    wfs = getWorkflows(dirname, release, arch)
    ret = {}
    for wf in wfs:
        step3_data = parseStep(dirname, release, arch, wf, "step3")
        step4_data = parseStep(dirname, release, arch, wf, "step4")
        
        ret_wf = {}
        for k, v in step3_data.items():
            ret_wf["step3_" + k] = v
        for k, v in step4_data.items():
            ret_wf["step4_" + k] = v
        ret[wf.replace(".", "p")] = ret_wf
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
