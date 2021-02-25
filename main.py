#!/usr/bin/python
import os
from itertools import ifilter

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

def formatRelease(release, parsed):
    ret = """
<h2>{release}</h2>
<ul>
<li>Step3</li>

<ul>
<li>CPU time: {step3_cpu_event:.2f} s/ev </li>
<li>peak RSS: {step3_peak_rss:.2f} MB </li>
</ul>

<li>Step4</li>
<ul>
<li>CPU time: {step4_cpu_event:.2f} s/ev </li>
<li>peak RSS: {step4_peak_rss:.2f} MB </li>
</ul>
</ul>
""".format(release=release, **parsed)
    return ret

if __name__ == "__main__":
    releases = getReleases(dirname)

    releases_str = ""
    for release in releases:
        parsed = parseRelease(dirname, release, arch)
        releases_str += formatRelease(release, parsed)     
    rep = """Content-type:text/html\r\n\r\n
<html>
<head>
<title>Reco profiling autoreport test</title>
</head>
<body>
Automatic reco profiling based on <a href="https://github.com/cms-sw/cms-bot/tree/master/reco_profiling">cmssw/cms-bot</a>,
<a href="https://cmssdt.cern.ch/jenkins/job/release-run-reco-profiling/">jenkins</a> and
<a href="https://github.com/ico1036/ServiceWork">Jiwoong's service work</a>.<br>
This report is prepared automatically using <a href="https://github.com/jpata/cms-reco-profiling">this script</a> and the data in {dirname}.<br>

{releases_str}
</body>
</html>
""".format(dirname=dirname, releases_str=releases_str)
    print(rep)
