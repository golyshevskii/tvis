"""Verify the Pine sources and generate the compiler-run smoke harness."""

import hashlib
import re
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).absolute()
REPO_ROOT = SCRIPT_PATH.parent.parent
CHECKOUT_ROOT = REPO_ROOT.resolve(strict=True)
SCRIPT_RELATIVE_PATH = SCRIPT_PATH.relative_to(REPO_ROOT)
PRODUCTION_PATH = Path("indicators/pe.pine")
VALIDATION_PATH = Path("docs/validation.md")
README_PATH = Path("README.md")
LICENSE_PATH = Path("LICENSE")
HARNESS_PATH = Path("tmp/pe-contract-tests.pine")
START_MARKER = "// @contract pe-ratio:start"
END_MARKER = "// @contract pe-ratio:end"
STATS_START_MARKER = "// @contract pe-statistics:start"
STATS_END_MARKER = "// @contract pe-statistics:end"
ANALYST_MODE = "Reported-quarter estimate ×4 (proxy)"
LICENSE_HEADER = (
    "// This Pine Script® code is subject to the terms of the Mozilla Public License 2.0 "
    "at https://mozilla.org/MPL/2.0/\n// © golyshevskii\n"
)


def fail(message: str) -> SystemExit:
    return SystemExit(f"ERROR: {message}")


def required_file(relative_path: Path) -> Path:
    try:
        resolved_path = (REPO_ROOT / relative_path).resolve(strict=True)
    except FileNotFoundError:
        raise fail(f"required file is missing: {relative_path}") from None

    try:
        resolved_path.relative_to(CHECKOUT_ROOT)
    except ValueError:
        raise fail(f"required file resolves outside the repository: {relative_path}") from None
    if not resolved_path.is_file():
        raise fail(f"required path is not a file: {relative_path}")
    return resolved_path


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def read_source(relative_path: Path) -> tuple[str, str]:
    content = required_file(relative_path).read_bytes()
    return content.decode("utf-8"), sha256(content)


def extract_marked_block(source: str, start_marker: str, end_marker: str, label: str) -> str:
    lines = source.splitlines()
    if lines.count(start_marker) != 1 or lines.count(end_marker) != 1:
        raise fail(f"production source must contain exactly one {label} contract block")
    start = lines.index(start_marker)
    end = lines.index(end_marker)
    if end <= start + 1:
        raise fail(f"{label} contract block is empty or malformed")

    return "\n".join(lines[start + 1 : end]) + "\n"


def extract_contract(source: str) -> str:
    lines = source.splitlines()
    block = extract_marked_block(source, START_MARKER, END_MARKER, "pe-ratio")

    production_call = "pe = peRatio(close, epsTTM)"
    if lines.count(production_call) != 1:
        raise fail("production calculation must call the extracted peRatio contract")
    if any(re.match(r"^\s*pe\s*:=", line) for line in lines[lines.index(production_call) + 1 :]):
        raise fail("production calculation must not reassign pe after the contract call")
    return block


def extract_statistics_contract(source: str) -> str:
    return extract_marked_block(source, STATS_START_MARKER, STATS_END_MARKER, "pe-statistics")


def check_data_contract(source: str) -> None:
    lines = source.splitlines()
    compact = " ".join(source.split())
    mode_selection = 'fwdEPS = fwdMode == "Growth assumption" ? scenarioEPS : analystEPS'
    forward_call = "fwdPE = showFwd ? peRatio(close, fwdEPS) : na"
    required = (
        "not na(price) and price > 0 and not na(eps) and eps > 0 ? price / eps : na",
        "not na(reportedQuarterEstimate) and reportedQuarterEstimate > 0 ? reportedQuarterEstimate * 4 : na",
        'epsTTM = request.financial(syminfo.tickerid, epsId, "TTM", gaps=barmerge.gaps_off, ignore_invalid_symbol=true, currency=syminfo.currency)',
        f'if showFwd and fwdMode == "{ANALYST_MODE}" estQ := request.earnings(syminfo.tickerid, earnings.estimate, gaps=barmerge.gaps_off, lookahead=barmerge.lookahead_off, ignore_invalid_symbol=true, currency=syminfo.currency)',
        "scenarioEPS = growthScenarioEPS(epsTTM, growthPct)",
        "analystEPS = analystProxyEPS(estQ)",
        mode_selection,
        forward_call,
        'plot(pe, "Trailing P/E (TTM EPS)", color=TRAILING_COLOR, linewidth=2, style=plot.style_linebr)',
        'plot(fwdMode == ANALYST_MODE ? fwdPE : na, "Reported-quarter EPS ×4 proxy P/E", color=FORWARD_COLOR, linewidth=2, style=plot.style_linebr)',
        'plot(fwdMode == GROWTH_MODE ? fwdPE : na, "TTM EPS growth scenario P/E", color=FORWARD_COLOR, linewidth=2, style=plot.style_linebr)',
        'string forwardValue = not showFwd ? "Off" : na(fwdPE) ? "Unavailable" : str.tostring(fwdPE, "#.##")',
    )
    for statement in required:
        if statement not in compact:
            raise fail(f"production data contract is missing: {statement}")
    if "lookahead=" in compact.split("request.financial", maxsplit=1)[1].split(")", maxsplit=1)[0]:
        raise fail("request.financial must not receive lookahead")
    if compact.count("request.financial(") != 1 or compact.count("request.earnings(") != 1:
        raise fail("production must have exactly one financial and one earnings request")
    if re.search(r"growthPct\s*=\s*input\.float\(.*?maxval\s*=\s*300\)\s*/", source, re.DOTALL):
        raise fail("growthPct input must remain an unscaled percentage")
    if lines.count(mode_selection) != 1:
        raise fail("production must have exactly one forward mode selection")
    if lines.count(forward_call) != 1:
        raise fail("production must have exactly one Show Forward result assignment")
    if any(re.match(r"^\s*fwdPE\s*:=", line) for line in lines[lines.index(forward_call) + 1 :]):
        raise fail("production must not reassign fwdPE after the guarded result")
    forward_wiring = (
        f'const string ANALYST_MODE = "{ANALYST_MODE}"',
        'const string GROWTH_MODE = "Growth assumption"',
        'string forwardLabel = fwdMode == ANALYST_MODE ? "Reported Q ×4 proxy P/E" : "TTM growth scenario P/E"',
        "table.cell(t, 0, 2, forwardLabel, text_color=chart.fg_color, bgcolor=rowBg, text_size=txtSize)",
        "table.cell(t, 1, 2, forwardValue, text_color=chart.fg_color, bgcolor=rowBg, text_size=txtSize)",
    )
    for statement in forward_wiring:
        if sum(line.strip() == statement for line in lines) != 1:
            raise fail(f"production forward UI wiring must contain exactly once: {statement}")


def check_statistics_contract(source: str) -> None:
    lines = [line.strip() for line in source.splitlines()]
    compact = " ".join(source.split())
    required = (
        "nextM2 += delta * (value - nextMean)",
        "leftM2 + rightM2 + delta * delta * leftCount * rightCount / count",
        "while array.size(inValues) > 0",
        "float transferred = statsStackPop(inValues, inCounts, inMeans, inM2s)",
        "statsStackPush(outValues, outCounts, outMeans, outM2s, transferred)",
        "statsStackPop(outValues, outCounts, outMeans, outM2s)",
        "count > 1 ? math.sqrt(math.max(m2 / count, 0.0)) : na",
        "not na(value) and not na(mean) and not na(sigma) and sigma > 0 ? (value - mean) / sigma : na",
        'na(z) ? "n/a" : z > 2 ? "Very rich" : z > 1 ? "Rich" : z < -2 ? "Very cheap" : z < -1 ? "Cheap" : "Normal"',
        'lookback = input.int(252, "Rolling lookback (bars)", minval=10, maxval=5000)',
        "float meanPE = statsMean(sampleCount, sampleMean)",
        "float sdPE = statsSigma(sampleCount, sampleM2)",
        "float visibleMeanPE = not na(pe) ? meanPE : na",
        'plot(visibleMeanPE, "Mean trailing P/E", color=chart.fg_color, linewidth=1, style=plot.style_linebr)',
        'na(visibleMeanPE) ? "n/a" : str.tostring(visibleMeanPE, "#.##")',
        'fill(pu1, pl1, color=color.new(chart.fg_color, 90), title="±1σ zone", fillgaps=false)',
        "zscore = statsZ(pe, meanPE, sdPE)",
        "verdict = statsVerdict(zscore)",
        "zStatus = displayZStatus(pe, sampleCount, sdPE, zscore)",
    )
    for statement in required:
        if statement not in compact:
            raise fail(f"production statistics contract is missing: {statement}")
    production_wiring = (
        "[nextAllCount, nextAllMean, nextAllM2] = statsAdd(allCount, allMean, allM2, pe)",
        "[nextRollingBars, rollingCount, rollingMean, rollingM2] = statsQueueUpdate(rollingInValues, rollingInCounts, rollingInMeans, rollingInM2s, rollingOutValues, rollingOutCounts, rollingOutMeans, rollingOutM2s, rollingBars, lookback, pe)",
        'bool allHistory = lbMode == "All history"',
        "u1 = meanPE + sdPE",
        "l1 = meanPE - sdPE",
        "u2 = meanPE + 2 * sdPE",
        "l2 = meanPE - 2 * sdPE",
    )
    for statement in production_wiring:
        if lines.count(statement) != 1:
            raise fail(f"production statistics wiring must contain exactly once: {statement}")
    band_plots = (
        'pu1 = plot(showBands and not na(pe) ? u1 : na, "+1σ", color=color.new(chart.fg_color, 55), style=plot.style_linebr)',
        'pl1 = plot(showBands and not na(pe) ? l1 : na, "-1σ", color=color.new(chart.fg_color, 55), style=plot.style_linebr)',
        'plot(showBands and not na(pe) ? u2 : na, "+2σ", color=color.new(color.red, 65), style=plot.style_linebr)',
        'plot(showBands and not na(pe) ? l2 : na, "-2σ", color=color.new(color.green, 65), style=plot.style_linebr)',
    )
    for statement in band_plots:
        if lines.count(statement) != 1:
            raise fail(f"production band plot must contain exactly once: {statement}")
    forbidden = ("ta.sma(pe, lookback)", "ta.stdev(pe, lookback)", "s2 / n -", "statsRemove(", "varip")
    for statement in forbidden:
        if statement in compact:
            raise fail(f"production statistics contract contains forbidden logic: {statement}")


def render_harness(source: str, source_hash: str) -> str:
    contract = extract_contract(source)
    statistics_contract = extract_statistics_contract(source)
    return f"""{LICENSE_HEADER}
// Generated by scripts/check_pe.py; edit indicators/pe.pine instead.
// Production SHA-256: {source_hash}
//@version=6
indicator("P/E contract smoke", max_bars_back=5000)

{contract}
{statistics_contract}
closeEnough(float actual, float expected) =>
    not na(actual) and math.abs(actual - expected) <= math.max(1e-8, 1e-10 * math.abs(expected))

summarize(array<float> values) =>
    int count = 0
    float mean = 0.0
    float m2 = 0.0
    for value in values
        [nextCount, nextMean, nextM2] = statsAdd(count, mean, m2, value)
        count := nextCount
        mean := nextMean
        m2 := nextM2
    [count, statsMean(count, mean), statsSigma(count, m2)]

rollingSummary(array<float> values, int window) =>
    array<float> inValues = array.new<float>()
    array<int> inCounts = array.new<int>()
    array<float> inMeans = array.new<float>()
    array<float> inM2s = array.new<float>()
    array<float> outValues = array.new<float>()
    array<int> outCounts = array.new<int>()
    array<float> outMeans = array.new<float>()
    array<float> outM2s = array.new<float>()
    int bars = 0
    int count = 0
    float mean = 0.0
    float m2 = 0.0
    for value in values
        [nextBars, nextCount, nextMean, nextM2] = statsQueueUpdate(inValues, inCounts, inMeans, inM2s, outValues, outCounts, outMeans, outM2s, bars, window, value)
        bars := nextBars
        count := nextCount
        mean := nextMean
        m2 := nextM2
    [count, statsMean(count, mean), statsSigma(count, m2)]

bool ratioFixtures = closeEnough(peRatio(100.0, 5.0), 20.0) and na(peRatio(float(na), 5.0)) and na(peRatio(0.0, 5.0)) and na(peRatio(100.0, float(na))) and na(peRatio(100.0, 0.0)) and na(peRatio(100.0, -5.0)) and closeEnough(peRatio(100.0, 0.000001), 100000000.0)
bool growthFixtures = closeEnough(growthScenarioEPS(5.0, 8.0), 5.4) and closeEnough(peRatio(100.0, growthScenarioEPS(5.0, 8.0)), 100.0 / 5.4) and closeEnough(growthScenarioEPS(5.0, -50.0), 2.5) and closeEnough(growthScenarioEPS(5.0, 300.0), 20.0) and na(growthScenarioEPS(float(na), 8.0)) and na(growthScenarioEPS(0.0, 8.0)) and na(growthScenarioEPS(-5.0, 8.0))
bool analystFixtures = closeEnough(analystProxyEPS(2.5), 10.0) and closeEnough(peRatio(100.0, analystProxyEPS(2.5)), 10.0) and na(analystProxyEPS(float(na))) and na(analystProxyEPS(0.0)) and na(analystProxyEPS(-2.5))

[emptyCount, emptyMean, emptySigma] = summarize(array.from(float(na)))
[oneCount, oneMean, oneSigma] = summarize(array.from(5.0))
[constantCount, constantMean, constantSigma] = summarize(array.from(7.0, 7.0, 7.0))
[historyCount, historyMean, historySigma] = summarize(array.from(10.0, 20.0, 30.0))
[gapCount, gapMean, gapSigma] = summarize(array.from(10.0, float(na), 20.0, 30.0, float(na)))
[transitionCount, transitionMean, transitionSigma] = summarize(array.from(10.0, 10.0, 20.0))
[largeCount, largeMean, largeSigma] = summarize(array.from(100000000.0, 100000001.0, 100000002.0))
[warmupCount, warmupMean, warmupSigma] = rollingSummary(array.from(float(na), 2.0, float(na), 4.0), 10)
[rollingCount, rollingMean, rollingSigma] = rollingSummary(array.from(999.0, float(na), 2.0, float(na), 4.0, float(na), float(na), float(na), float(na), float(na), float(na)), 10)
[longGapCount, longGapMean, longGapSigma] = rollingSummary(array.from(5.0, float(na), float(na), float(na), float(na), float(na), float(na), float(na), float(na), float(na), float(na)), 10)
[largeRollingCount, largeRollingMean, largeRollingSigma] = rollingSummary(array.from(100000000.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0), 10)
[largeSparseCount, largeSparseMean, largeSparseSigma] = rollingSummary(array.from(100000000.0, float(na), 2.0, float(na), 4.0, float(na), float(na), float(na), float(na), float(na), float(na)), 10)

float historyExpectedSigma = math.sqrt(200.0 / 3.0)
bool emptyFixtures = emptyCount == 0 and na(emptyMean) and na(emptySigma)
bool oneFixtures = oneCount == 1 and closeEnough(oneMean, 5.0) and na(oneSigma)
bool constantFixtures = constantCount == 3 and closeEnough(constantMean, 7.0) and closeEnough(constantSigma, 0.0) and na(statsZ(7.0, constantMean, constantSigma)) and statsVerdict(statsZ(7.0, constantMean, constantSigma)) == "n/a"
bool historyFixtures = historyCount == 3 and closeEnough(historyMean, 20.0) and closeEnough(historySigma, historyExpectedSigma) and closeEnough(statsZ(30.0, historyMean, historySigma), math.sqrt(1.5))
bool gapFixtures = gapCount == 3 and closeEnough(gapMean, 20.0) and closeEnough(gapSigma, historyExpectedSigma) and na(statsZ(float(na), gapMean, gapSigma))
bool longGapFixtures = longGapCount == 0 and na(longGapMean) and na(longGapSigma)
bool transitionFixtures = transitionCount == 3 and closeEnough(transitionMean, 40.0 / 3.0) and closeEnough(transitionSigma, math.sqrt(200.0 / 9.0))
bool largeFixtures = largeCount == 3 and closeEnough(largeMean, 100000001.0) and closeEnough(largeSigma * largeSigma, 2.0 / 3.0)
bool warmupFixtures = warmupCount == 2 and closeEnough(warmupMean, 3.0) and closeEnough(warmupSigma, 1.0)
bool rollingFixtures = rollingCount == 2 and closeEnough(rollingMean, 3.0) and closeEnough(rollingSigma, 1.0)
bool largeRollingFixtures = largeRollingCount == 10 and closeEnough(largeRollingMean, 7.0) and closeEnough(largeRollingSigma, 0.0) and largeSparseCount == 2 and closeEnough(largeSparseMean, 3.0) and closeEnough(largeSparseSigma, 1.0)
bool bandFixtures = closeEnough(historyMean + historySigma, 20.0 + historyExpectedSigma) and closeEnough(historyMean - historySigma, 20.0 - historyExpectedSigma) and closeEnough(historyMean + 2.0 * historySigma, 20.0 + 2.0 * historyExpectedSigma) and closeEnough(historyMean - 2.0 * historySigma, 20.0 - 2.0 * historyExpectedSigma)
bool verdictFixtures = statsVerdict(2.0) == "Rich" and statsVerdict(2.000001) == "Very rich" and statsVerdict(1.999999) == "Rich" and statsVerdict(1.0) == "Normal" and statsVerdict(1.000001) == "Rich" and statsVerdict(0.999999) == "Normal" and statsVerdict(-0.999999) == "Normal" and statsVerdict(-1.0) == "Normal" and statsVerdict(-1.000001) == "Cheap" and statsVerdict(-1.999999) == "Cheap" and statsVerdict(-2.0) == "Cheap" and statsVerdict(-2.000001) == "Very cheap"
bool statusFixtures = displayZStatus(float(na), 3, 1.0, float(na)) == "Missing P/E" and displayZStatus(5.0, 1, float(na), float(na)) == "Need ≥2" and displayZStatus(7.0, 3, float(na), float(na)) == "Undefined" and displayZStatus(7.0, 3, 0.0, float(na)) == "σ=0" and displayZStatus(7.0, 3, 1.0, float(na)) == "Undefined" and displayZStatus(20.0, 3, 1.0, 1.25) == "1.25 sd"
bool smokePass = ratioFixtures and growthFixtures and analystFixtures and emptyFixtures and oneFixtures and constantFixtures and historyFixtures and gapFixtures and longGapFixtures and transitionFixtures and largeFixtures and warmupFixtures and rollingFixtures and largeRollingFixtures and bandFixtures and verdictFixtures and statusFixtures
if barstate.islast and not smokePass
    runtime.error("P/E contract smoke check failed")
if barstate.islast
    log.info("STATISTICS_GREEN|rolling=" + str.tostring(rollingCount) + "," + str.tostring(rollingMean) + "," + str.tostring(rollingSigma) + "|history=" + str.tostring(historyCount) + "," + str.tostring(historyMean) + "," + str.tostring(historySigma) + "|large_variance=" + str.tostring(largeSigma * largeSigma))
plot(smokePass ? 1 : 0, "Smoke result")
"""


def validated_harness_path() -> Path:
    harness_path = REPO_ROOT / HARNESS_PATH
    try:
        harness_path.parent.resolve(strict=False).relative_to(CHECKOUT_ROOT)
    except ValueError:
        raise fail(f"harness directory resolves outside the repository: {harness_path.parent}") from None
    if harness_path.is_symlink():
        raise fail(f"generated harness must not be a symlink: {HARNESS_PATH}")
    return harness_path


def check(check_harness: bool = True) -> tuple[str, str]:
    required_file(SCRIPT_RELATIVE_PATH)
    production, production_hash = read_source(PRODUCTION_PATH)
    if not production.startswith(LICENSE_HEADER):
        raise fail("production MPL-2.0/golyshevskii header changed")
    extract_contract(production)
    extract_statistics_contract(production)
    check_data_contract(production)
    check_statistics_contract(production)
    required_file(README_PATH)
    required_file(VALIDATION_PATH)
    required_file(LICENSE_PATH)

    harness_path = validated_harness_path()
    if check_harness and harness_path.exists():
        expected_harness = render_harness(production, production_hash)
        if harness_path.read_text(encoding="utf-8") != expected_harness:
            raise fail("generated harness is stale: run `make test`")

    print(f"OK production SHA-256 {production_hash}")
    print("OK MPL-2.0 attribution and production-linked contract block")
    print("LOCAL CHECKS PASSED; Pine compilation/runtime were not run")
    return production, production_hash


def generate() -> None:
    production, production_hash = check(check_harness=False)
    harness_path = validated_harness_path()
    harness_path.parent.mkdir(exist_ok=True)
    harness_path.write_text(render_harness(production, production_hash), encoding="utf-8")
    print(f"GENERATED {HARNESS_PATH} from production SHA-256 {production_hash}")
    print("PINE NOT RUN; import the harness into Pine Editor and execute it on a chart")


def main(arguments: list[str]) -> int:
    if arguments == ["check"]:
        check()
        return 0
    if arguments == ["generate"]:
        generate()
        return 0
    raise fail("usage: check_pe.py check|generate")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
