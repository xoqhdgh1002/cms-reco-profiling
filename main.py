#!/usr/bin/env python
import os
from itertools import ifilter
import yaml
import subprocess
import sys
import fnmatch
import bz2

DATA_DIR="/eos/cms/store/user/cmsbuild/profiling/data/"
DEPLOY_DIR="/eos/project/c/cmsweb/www/reco-prof/cgi-bin/data/releases"

IGPROF_DEPLOY_URL="https://cms-reco-profiling.web.cern.ch/cms-reco-profiling/cgi-bin/igprof-navigator/"
def makeCirclesURL(release, arch, wf, step):
    return "http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/circles/piechart.php?local=false&dataset={release}%2F{arch}%2F{wf}%2F{step}_circles&resource=time_thread&colours=default&groups=reco_PhaseII&threshold=0".format(release=release, arch=arch, wf=wf, step=step)

workflow_numev = {
    "23434.21": 100,
    "11834.21": 400
}

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-data", type=str, default=DATA_DIR, help="profiling data location")
    parser.add_argument("--release-pattern", type=str, help="Glob string to filter releases that are going to be processed", default="*")
    parser.add_argument("--outfile", type=str, help="output yaml file", default="out.yaml")
    parser.add_argument("--igprof-deploy-path", type=str, help="igprof-analyse cgi-bin deployment path", default=DEPLOY_DIR)
    parser.add_argument("--igprof-deploy-url", type=str, help="igprof-analyse cgi-bin deployment URL", default=IGPROF_DEPLOY_URL)
    parser.add_argument("--run-igprof-analysis", type=bool, help="if 1, parse the igprof results", default=0)
    args = parser.parse_args()
    return args

class CallStack:
    def __init__(self, func_data, measurement):
        self.func_data = func_data
        self.measurement = measurement

def cleanStack(stack):
    new_stack = []
    for s in stack:
        if not s in new_stack and len(s)>0:
            new_stack.append(s)
        if s.endswith("doEvent"):
            break
        if s.endswith("beginRun"):
            break
        if s.endswith("edm::Factory::makeModule"):
            break
        if s.endswith("edm::EventProcessor::init"):
            break
    return new_stack

def nameStack(stack):
    if "edm::PoolOutputModule::write" in stack:
        return "PoolOutputModule"
    elif "TBasket::ReadBasketBuffers" in stack or "TBranch::GetEntry" in stack:
        return "InputModule"
    elif "edm::EventPrincipal::clearEventPrincipal" in stack:
        return "edm::EventPrincipal::clearEventPrincipal"
    elif len(stack)>0 and stack[-1].endswith("doEvent"):
        for s in stack:
            if "::produce" in s:
                return s
    elif len(stack)>0 and stack[-1].endswith("beginRun"):
        return stack[-1]
    elif len(stack)>0 and stack[-1].endswith("makeModule"):
        return stack[-5]
    elif len(stack)>0 and stack[-1].endswith("edm::EventProcessor::init"):
        return stack[-1]
    return "other"

def makeIgProfGrouped(infile, outfile): 
    fi = bz2.BZ2File(infile, "rb")
    
    function_stacks = []
    for line in fi.readlines():
    
        #new stack
        if line.startswith("## "):
            stack = []
            stack_measurement = float(line.split()[3][1:].replace("'", ""))
        #line in existing stack
        elif line.startswith("#"):
            line = line.replace("(anonymous namespace)::", "")
            line = line.replace(", ", ",")
            line = line[line.index(" ")+1:]
            line = line.replace(" ", "")
            if "(" in line:
                line = line[:line.index("(")]
                stack.append(line)
        else:
            function_stacks.append(CallStack(stack, stack_measurement))

    ret = {}
    for istack, stack in enumerate(function_stacks):
        new_stack = cleanStack(stack.func_data)
        if len(new_stack) > 0:
            name = nameStack(new_stack)
            if not name in ret:
                ret[name] = 0
            ret[name] += stack.measurement

    with open(outfile, "w") as of:
        for k, v in sorted(ret.items(), key=lambda x: x[1], reverse=True):
            of.write("{};{:.2f}\n".format(k,v))

def getFileSize(fn):
    ret = os.path.getsize(fn)
    return ret

def makeIgProfSummaryMEM(infile, outfile):
    if os.path.isfile(infile):
        os.system("igprof-analyse --top 1000 --demangle --gdb -r MEM_LIVE {} | bzip2 -9 > {}".format(infile, outfile))
        #makeIgProfGrouped(outfile, outfile.replace(".txt.bz2", "_grouped.csv"))
        os.system("igprof-analyse --sqlite -v --demangle --gdb -r MEM_LIVE {} | python fix-igprof-sql.py | sqlite3 {}".format(infile, outfile.replace(".txt.bz2", ".sql3")))

def makeIgProfSummaryCPU(infile, outfile):
    os.system("igprof-analyse --top 1000 --demangle --gdb -r PERF_TICKS {} | bzip2 -9 > {}".format(infile, outfile))
    #makeIgProfGrouped(outfile, outfile.replace(".txt.bz2", "_grouped.csv"))
    os.system("igprof-analyse --sqlite -v --demangle --gdb {} | python fix-igprof-sql.py | sqlite3 {}".format(infile, outfile.replace(".txt.bz2", ".sql3")))

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

def parseStep(dirname, release, arch, wf, step, run_igprof_analysis=True, igprof_deploy_url=""):
    base = os.path.join(dirname, release, arch, wf)
    tmi = os.path.join(base, "{}_TimeMemoryInfo.log".format(step))
    rootfile = os.path.join(base, "{}.root.unused".format(step))
    if not os.path.isfile(rootfile):
        rootfile = os.path.join(base, "{}.root".format(step))

    cpu_event = getCPUEvent(tmi)
    peak_rss = getPeakRSS(tmi)
    file_size = getFileSize(rootfile)

    igprof_outpath = "results/igprof/{}/{}/{}".format(release, wf, step)
    igprof_cpu_file = os.path.join(igprof_outpath, "cpu_endjob.txt.bz2")

    if run_igprof_analysis:
        if not os.path.isdir(igprof_outpath):
            os.makedirs(igprof_outpath)

        makeIgProfSummaryCPU(os.path.join(base, "{}_igprofCPU.gz".format(step)), igprof_cpu_file)

        lastev = workflow_numev[wf] - 1
        midev = int(workflow_numev[wf]/2)

        igprof_mem_file_last = os.path.join(igprof_outpath, "mem_live.{}.txt.bz2".format(lastev))
        makeIgProfSummaryMEM(os.path.join(base, "{}_igprofMEM.{}.gz".format(step, lastev)), igprof_mem_file_last)

        igprof_mem_file_mid = os.path.join(igprof_outpath, "mem_live.{}.txt.bz2".format(midev))
        makeIgProfSummaryMEM(os.path.join(base, "{}_igprofMEM.{}.gz".format(step, midev)), igprof_mem_file_mid)
        
        igprof_mem_file_first = os.path.join(igprof_outpath, "mem_live.{}.txt.bz2".format(1))
        makeIgProfSummaryMEM(os.path.join(base, "{}_igprofMEM.{}.gz".format(step, 1)), igprof_mem_file_first)

    return {
        "cpu_event": cpu_event,
        "peak_rss": peak_rss,
        "file_size": file_size,
        "igprof_cpu": igprof_deploy_url + igprof_cpu_file.replace("results/igprof", "releases").replace(".txt.bz2", ""),
        "igprof_mem_last": igprof_deploy_url + igprof_mem_file_last.replace("results/igprof", "releases").replace(".txt.bz2", ""),
        "igprof_mem_mid": igprof_deploy_url + igprof_mem_file_mid.replace("results/igprof", "releases").replace(".txt.bz2", ""),
        "igprof_mem_first": igprof_deploy_url + igprof_mem_file_first.replace("results/igprof", "releases").replace(".txt.bz2", ""),
        "circles": makeCirclesURL(release, arch, wf, step)
    }

def getWorkflows(dirname, release, arch):
    ls = os.listdir(os.path.join(dirname, release, arch))
    ls = [x for x in ls if "." in x and int(x.split(".")[0])]
    return ls

def parseRelease(dirname, release, arch, **kwargs):
    print("parsing {} {} {}".format(dirname, release, arch))
    wfs = getWorkflows(dirname, release, arch)
    ret = {}
    for wf in wfs:
        step3_data = parseStep(dirname, release, arch, wf, "step3", **kwargs)
        step4_data = parseStep(dirname, release, arch, wf, "step4", **kwargs)
       
        ret_wf = {} 
        ret_wf["step3"] = step3_data
        ret_wf["step4"] = step4_data
        ret[wf.replace(".", "p")] = ret_wf
    return ret

def isValidScramArch(release, arch_string):
    return arch_string.startswith("slc")

def formatValue(item, value):
    units = {
        "cpu_event": "s/ev",
        "peak_rss": "MB",
        "file_size": "MB"
    }
    if item == "file_size":
        value = value/1000/1000
    return "{:.2f} {}".format(value, units[item])

def prepareReport(results):
    out = ""
    for release in sorted(results.keys()):
        out += "- {}\n".format(release)
        for wf in sorted(results[release].keys()):
            out += "  - {}\n".format(wf)
            for step in ["step3", "step4"]:
                out += "    - {}\n".format(step)
                for item in ["cpu_event", "peak_rss", "file_size"]:
                    value = results[release][wf][step][item]
                    out += "      - {}: {}\n".format(item, formatValue(item, value))

                #Write out the igprof and circles links                
                out += "      - profiles: "
                prof_links = []
                for item in ["igprof_cpu", "igprof_mem_first", "igprof_mem_mid", "igprof_mem_last", "circles"]:
                    value = results[release][wf][step][item]
                    prof_links.append("[{}]({})".format(item, value))
                out += ", ".join(prof_links) + "\n"

    return out
 
if __name__ == "__main__":
    args = parse_args()

    releases = getReleases(args.profile_data)

    #prepare the results
    results = {}
    for release in releases:
        for arch in os.listdir(os.path.join(args.profile_data, release)):
            if isValidScramArch(release, arch):
                if fnmatch.fnmatch(release, args.release_pattern):
                    parsed = parseRelease(
                        args.profile_data, release, arch,
                        run_igprof_analysis=args.run_igprof_analysis,
                        igprof_deploy_url=args.igprof_deploy_url,
                    )
                    results[release + "_" + arch] = parsed
                else:
                    print("skipping {}".format(release))

    #copy SQL outputs
    if os.access(args.igprof_deploy_path, os.W_OK):
        os.system("./deploy.sh {}".format(args.igprof_deploy_path))
    else:
        print("igprof-analyse sql path is not writable: {}, skipping deployment".format(args.igprof_deploy_path))

    with open(args.outfile.replace("yaml", "md"), "a") as fi:
        fi.write(prepareReport(results))

    #Write the summary yaml file
    with open(args.outfile, "a") as fi:
        fi.write(yaml.dump(results, default_flow_style=False))
