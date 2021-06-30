# Automatic reco profiling

Results:
- [formatted](results/summary.md)
- [yaml](results/summary.yaml)
- Phase2 evolution: [csv](results/release_timing.csv), [pdf](results/release_timing.pdf)

## Updating
Automatically extracts key measurements from the reco profiling outputs in EOS, stores the results in YAML files for future use.

```
[jpata@lxplus7108 reco-profiling]$ ./main.py
```

## Useful links
- CMS reco profiling landing page (WIP): http://cms-reco-profiling.web.cern.ch/cms-reco-profiling/web
- landing page source: https://github.com/jpata/cms-reco-profiling-web
- EOS path: `/eos/cms/store/user/cmsbuild/profiling`
- Jenkins jobs: https://cmssdt.cern.ch/jenkins/job/release-run-reco-profiling/
- cmssw bot scripts that run the automatic profiling: https://github.com/cms-sw/cms-bot/tree/master/reco_profiling/
- Custom profiling web page: https://jiwoong.web.cern.ch/jiwoong/
- Profiling helper scripts: https://github.com/ico1036/ServiceWork/


# Workflow
```
https://cmssdt.cern.ch/jenkins/job/release-run-reco-profiling/ -> Build with parameters

1. Fill the RELEASE_FORMAT with the full release name, no spaces, no quotes, e.g. RELEASE_FORMAT=CMSSW_12_0_0_pre3
2. WORKFLOW=23434.21 EVENTS=100
3. Click Build
...
5. WORKFLOW=11834.21 EVENTS=400
6. Click Build
...
7. Produce the profile yaml, sql with
  ./main.py --releases CMSSW_12_0_0_pre3 --igprof
  ./reco_times.py
```

Make sure the [gh cli](https://github.com/cli/cli) is available under `$PATH` and cmssw git checkout is set up under `$CMSSW_BASE/src`.
