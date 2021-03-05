# Automatic reco profiling

Results:
- [formatted](results/summary.md)
- [yaml](results/summary.yaml)

## Updating
Automatically extracts key measurements from the reco profiling outputs in EOS, stores the results in YAML files for future use.

```
[jpata@lxplus7108 reco-profiling]$ ./main.py
```

## Useful links
- CMS reco profiling landing page (WIP): http://cms-reco-profiling.web.cern.ch/cms-reco-profiling
- EOS path: `/eos/cms/store/user/cmsbuild/profiling`
- Jenkins jobs: https://cmssdt.cern.ch/jenkins/job/release-run-reco-profiling/
- cmssw bot scripts that run the automatic profiling: https://github.com/cms-sw/cms-bot/tree/master/reco_profiling/
- Custom profiling web page: https://jiwoong.web.cern.ch/jiwoong/
- Profiling helper scripts: https://github.com/ico1036/ServiceWork/
