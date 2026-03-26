## Dev Summary

- packaged crash root cause found: BOM in `ibases.v8i`
- packaged runtime now parses bases and keeps `SOVUT` launch args
- real 1C launcher renders embedded inside SovAuto
- external top-level 1C window not observed during packaged launcher stage
- full packaged gate still open: embedded `1С:Предприятие` transition remains unstable / UI hangs
