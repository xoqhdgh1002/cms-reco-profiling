# Reco release profiling

Results:
- human-readable formatted [summary](results/summary.md)
- more detailed machine-readable [yaml](results/summary.yaml)
- reco time evolution: [full csv](results/release_timing.csv), [Phase2 major](results/major_release_timing.pdf), [Phase2](results/release_timing.pdf), [Run3](results/release_timing_run3.pdf)

# Workflow
```
https://cmssdt.cern.ch/jenkins/job/release-run-reco-profiling/ -> Build with parameters

1. Fill the RELEASE_FORMAT with the full release name, no whitespace, no quotes, e.g. RELEASE_FORMAT=CMSSW_12_5_0_pre1
2. WORKFLOW=35234.21 EVENTS=-1 DOCKER_IMG=cmssw/el8
3. Click Build
...
5. WORKFLOW=11834.21 EVENTS=-1 DOCKER_IMG=cmssw/el8
6. Click Build
...
5. WORKFLOW=136.889 EVENTS=-1 DOCKER_IMG=cmssw/el8
6. Click Build
...
7. Produce the profile yaml and csv files with
  ./main.py --releases CMSSW_12_5_0_pre1
  ./reco_times.py
```

## Updating the results
Automatically extracts key measurements from the reco profiling outputs in EOS, stores the results in YAML files for future use. Make sure you have done `cmsenv` somewhere beforehand.

```
[jpata@lxplus7108 reco-profiling]$ ./main.py --release CMSSW_12_5_0_pre1 --igprof
```

```
$ gh release view CMSSW_12_5_0_pre1 --json publishedAt
```

## Useful links
- CMS reco profiling landing page: http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/web
- landing page repo: https://github.com/jpata/cms-reco-profiling-web
- EOS path of results: `/eos/cms/store/user/cmsbuild/profiling`
- Jenkins jobs: https://cmssdt.cern.ch/jenkins/job/release-run-reco-profiling/
- cmssw bot scripts that run the automatic profiling: https://github.com/cms-sw/cms-bot/tree/master/reco_profiling/
- Profiling helper scripts: https://github.com/ico1036/ServiceWork/
