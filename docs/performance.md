# P/E performance — 2026-09-25

The Pine Profiler confirmed that All history was executing the unused rolling
queue. The retained change calls that queue only in Rolling lookback. No
arithmetic, data request, history length, input default or output was changed.
All-history median runtimes were lower in this small experiment; the ranges
overlap, so these samples do not establish a stable percentage speedup.
Rolling showed no demonstrated improvement.

## Sources and reproducible setup

Baseline commit: `f8d3f89259ed9c85caaf43d7def18ba1d1335c3e`.

| Artifact | SHA-256 |
|---|---|
| Baseline `indicators/pe.pine` | `c64f2d37636c217c96687f12885ab740380f60352d055bad354abb102986f5f0` |
| Retained `indicators/pe.pine` | `2c4d1b711e0c76ac552e693c24cb368a068b27978d323995897a79080da73bd2` |
| Baseline benchmark copy | `f6fc02bad0f7e054a91980a7433a9ed387553d33a9dd8b0e911432b4c8be9395` |
| Retained benchmark copy | `5a6e7325e4e9e185b10644e8517dd424dff2e19ad2fb49abdeadfb1291eafc7a` |

1. Use an editable script in the **chart-linked** Pine Editor, add/update it
   on the chart, then enable **More → Profiler mode**. The detached editor
   initially had no Profiler entry; after adding the exact current Pine v6
   source in the chart-linked editor, the switch appeared and worked. This
   corrects the earlier unavailable observation; no account-plan restriction
   was observed in this run.
2. Preserve the saved script before using its slot. Copy each version from
   the repository into a temporary file outside the repository, then append
   exactly the following suffix, including its initial blank line. These
   identical additions are measurement instrumentation, not production code:

   ```pine

   // Benchmark-only restart input and loaded-bar count.
   int benchmarkRun = input.int(1, "Benchmark run")
   plot(bar_index + 1, "Benchmark loaded bars", display=display.data_window)
   ```

3. Verify editor text against the file after normalizing clipboard CRLF to
   LF. Use standard 1D candles, `NASDAQ:AAPL` in the chart header, supplied
   as `BATS:AAPL` in the chart's runtime label (Cboe One), native USD,
   regular session and dividend adjustment off. Enter Replay with boundary
   **2026-09-24**, and leave playback paused. The last included closed bar is
   **2026-09-23**, close **337.02**. Do not advance Replay, pan to load more
   history, change symbol/TF/session or use `calc_bars_count` between runs.
4. Data Window independently showed **11,531 loaded bars**. The equivalence
   diagnostic also recorded first date **1980-12-12** and last date
   **2026-09-23**. All 30 measured runs reported **11,531 executions** of the
   final `plot(bar_index + 1, ...)` line (baseline line 244; retained line
   247). Bar count is not the count of valid EPS observations.
5. Apply the configurations below. For each, set `Benchmark run` to 1, then
   2, 3, 4 and 5, allowing each recalculation to finish. Changing this unused
   input restarts the script; simply reopening a tooltip or toggling the
   Profiler is not counted as another independent sample. Read the total
   runtime and executions from the final line's Profiler tooltip. Capture
   inputs and outputs along with each run. The baseline order was A/B/C;
   the retained order was C/B/A. Runs took place at 20:39–20:46 +04.
6. Repeat on unchanged data for the other version. Compare every raw sample,
   the median and min–max range. Verify numerical equivalence separately;
   do not use an instrumented correctness probe's runtime as a benchmark.

The restart method follows TradingView's
[repetitive profiling instructions](https://www.tradingview.com/pine-script-docs/writing/profiling-and-optimization/#repetitive-profiling).
Profiler runtimes include measurement overhead, so they are estimates of
instrumented execution, not chart-loading wall time or uninstrumented latency.

## Configurations and raw results

These three configurations cover both history branches, all three forward
states and both table states. They are branch coverage, not a full factorial
experiment isolating the individual cost of each input.

| ID | Average window | Forward | Table |
|---|---|---|---|
| A | All history | On; Reported-quarter estimate ×4 (proxy) | On |
| B | All history | Off; selected method remains Reported-quarter estimate ×4 (proxy) | Off |
| C | Rolling lookback | On; Growth assumption | On |

Every run used `EARNINGS_PER_SHARE_DILUTED`, growth **8%**, lookback **252**,
bands **on**, table position **Top right**, size **Normal**. Inputs other
than the documented restart input and configuration settings were unchanged.
The existing chart's other indicators were left in place; the reported
Profiler totals belong to the measured script only.

All times below are milliseconds, transcribed from Profiler tooltips; no
samples were discarded.

| Configuration / version | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 | Median | Min–max |
|---|---:|---:|---:|---:|---:|---:|---|
| A baseline | 268.0 | 271.1 | 289.0 | 211.1 | 303.7 | 271.1 | 211.1–303.7 |
| A retained | 214.0 | 193.8 | 132.7 | 152.3 | 122.2 | 152.3 | 122.2–214.0 |
| B baseline | 152.6 | 249.7 | 144.4 | 212.3 | 143.3 | 152.6 | 143.3–249.7 |
| B retained | 119.7 | 103.5 | 204.0 | 102.5 | 163.8 | 119.7 | 102.5–204.0 |
| C baseline | 168.1 | 204.6 | 195.0 | 154.4 | 141.3 | 168.1 | 141.3–204.6 |
| C retained | 201.0 | 179.4 | 205.7 | 182.6 | 197.0 | 197.0 | 179.4–205.7 |

The preceding exact-source baseline inspection on the same paused Replay
showed line 174's unconditional `statsQueueUpdate` call at **72.6 ms of
262.6 ms (27.6%)**, with **11,531 executions**, despite All history being
selected. This was hotspot discovery, not one of the five instrumented
samples. In the retained All-history run, the conditional header had a
Profiler entry but the queue call on line 175 had none. Rolling still
executes the queue normally. This removes demonstrated unnecessary work
without changing the queue algorithm.

The retained code adds one input-controlled branch; input changes restart
Pine over the loaded history, so switching back to Rolling rebuilds its full
window. All history still uses O(1) work/state per bar, and Rolling retains
its bounded O(N) memory, O(1) amortized update and O(N) occasional transfer.
The analyst request was already conditional and table writes already used
`barstate.islast`; neither is claimed as a new optimization.

A's median fell from 271.1 to 152.3 ms and B's from 152.6 to 119.7 ms. A's
ranges barely overlap; B's overlap substantially. C's median rose from
168.1 to 197.0 ms, with overlapping ranges. Five non-interleaved runs on one
symbol cannot separate every server-load effect or certify a general
speedup/regression. The retained benefit is the observed removal of the
unused queue path, with lower All-history medians in this dataset. No
additional table/string refactor, cache, history restriction or dependency
was introduced.

## Correctness

A separate temporary Pine probe appended an independently named copy of the
baseline history orchestration to the retained production source. Both
states consumed the same actual `pe` on every loaded bar. It compared sample
count, mean, sigma, visible mean, all four bands, z-score, verdict and status;
finite values used `max(1e-8, 1e-10 * abs(expected))`, and na states, counts
and strings matched exactly. An error on any bar stopped execution. All
three configurations reached the final bar with **Benchmark equivalence =
1**, **11,531 bars**, and no runtime error. Data requests, ratio formulas and
forward wiring were byte-unchanged between production versions.

| Configuration | Trailing | Proxy | Growth | Mean | +1σ | −1σ | +2σ | −2σ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A, both versions | 38.63 | 44.53 | na | 28.56 | 35.24 | 21.88 | 41.93 | 15.20 |
| B, both versions | 38.63 | na | na | 28.56 | 35.24 | 21.88 | 41.93 | 15.20 |
| C, both versions | 38.63 | na | 35.77 | 35.09 | 37.23 | 32.96 | 39.36 | 30.83 |

These table values are the UI's two-decimal display, not the tolerance used
by the all-bars probe. Probe SHA-256:
`636f1b0e3381cacf81b4b6aacf8dc5b695e9cf196a1e710a90275930afe62ae8`.
Changing only the new condition to run in All history instead of Rolling
produced **RE10142**, `Error on bar 9525: Benchmark numerical equivalence
failed` at line 278. Mutant SHA-256:
`aab681bcf71919083a27d8c696cd1f641b9dfa7eb968f1be6ebc1b4956555fbd`.

The local source guard was updated first and failed on the unguarded baseline.
After the change it passed; in-memory mutations reversing the mode, removing
the condition, using `pe[1]`, and changing the +1σ formula were all rejected.
Temporary benchmark/equivalence additions are absent from production.

Restoring the correct condition returned the probe to GREEN on the same
Rolling data. The exact retained production compiled without visible
warnings/errors at 20:43:39 +04. The generated repository harness, SHA-256
`fc39442088ee2d6b09360600a76fb7183b0829abf13e21a55dd28cdaef4d095e`,
then compiled and displayed **Smoke result = 1.0000** without a runtime
error at 20:52:06 +04 on the same AAPL 1D Replay chart. Editor text was
compared to each file before execution.

After verification, the saved Data Probe was restored byte-for-byte after
clipboard line-ending normalization (SHA-256
`aa0c5bda3b156428fe3c3aca058bd964fb71fe82b4c6c9ef72b8246fe80401ce`).
It compiled at 20:52:35 +04 and its original plots returned. Profiler and
Replay were switched off, Data Window/editor were closed, and the AAPL 1D
layout reported **All changes saved**. The existing P/E indicator and other
chart indicators were preserved.

Final local checks: `make check`, `make test`, and `git diff --check` passed.
These verify source/tooling integrity and regenerate the harness; the Pine
runtime results above are separate observations. No publication was made.
