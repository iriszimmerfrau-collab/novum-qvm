#!/usr/bin/env python3
"""
PFQVS vs Qiskit Statevector Simulator — benchmark suite.

Measures wall-clock time for equivalent operations at varying qubit counts.
Outputs results in three canonical formats:
  1. JSON  — machine-readable, ASV/pytest-benchmark style (benchmark_results.json)
  2. CSV   — tabular import for spreadsheets/pandas      (benchmark_results.csv)
  3. LaTeX — paste-ready table for the paper              (benchmark_table.tex)

Plus a human-readable console summary.

Operations benchmarked
----------------------
1. State initialization
2. Single-qubit gate (H) throughput  — n sequential H gates on n-qubit register
3. Two-qubit gate (CNOT) throughput  — n-1 sequential CNOTs forming a chain
4. Bell state preparation            — H(0) + CNOT(0,1), fixed 2 qubits
5. Grover's search                   — full grovers_search call
6. Deutsch-Jozsa                     — full deutsch_jozsa call

Each trial is repeated REPS times; median, mean, std, min, max are recorded.
"""

import datetime
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import time

import numpy as np

# ── PFQVS ────────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from novum_qvm import PFQVS_QuantumComputer, __version__ as PFQVS_VERSION

# ── Qiskit ───────────────────────────────────────────────────────────────────
try:
    from qiskit.quantum_info import Statevector
    from qiskit import QuantumCircuit
    import qiskit
    HAS_QISKIT = True
    QISKIT_VERSION = qiskit.__version__
except ImportError:
    HAS_QISKIT = False
    QISKIT_VERSION = None
    print("WARNING: qiskit not found — Qiskit columns will be N/A", flush=True)

# ── Configuration ────────────────────────────────────────────────────────────
REPS        = 7          # repetitions per data point
WARMUP      = 2          # warmup iterations (discarded)
QUBIT_SIZES = [2, 4, 6, 8, 10, 12, 14, 16]
OUTPUT_DIR  = os.path.dirname(os.path.abspath(__file__))


# ══════════════════════════════════════════════════════════════════════════════
#  System information
# ══════════════════════════════════════════════════════════════════════════════

def _shell(cmd):
    """Run a shell command, return stripped stdout or empty string."""
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return ""


def collect_system_info() -> dict:
    """Collect comprehensive system metadata."""

    # CPU info
    cpu_model = ""
    cpu_cores_phys = os.cpu_count()
    cpu_freq_mhz = None
    cache_size = ""

    if platform.system() == "Linux":
        cpu_model = _shell("lscpu | grep 'Model name' | sed 's/Model name: *//'")
        try:
            cpu_cores_phys = int(_shell("lscpu | grep '^CPU(s):' | awk '{print $2}'"))
        except ValueError:
            pass
        freq = _shell("lscpu | grep 'CPU max MHz' | awk '{print $NF}'")
        if freq:
            try:
                cpu_freq_mhz = float(freq)
            except ValueError:
                pass
        cache_size = _shell("lscpu | grep 'L3 cache' | sed 's/L3 cache: *//'")
    elif platform.system() == "Darwin":
        cpu_model = _shell("sysctl -n machdep.cpu.brand_string")
        try:
            cpu_cores_phys = int(_shell("sysctl -n hw.physicalcpu"))
        except ValueError:
            pass
        freq = _shell("sysctl -n hw.cpufrequency_max")
        if freq:
            try:
                cpu_freq_mhz = int(freq) / 1_000_000
            except ValueError:
                pass
        cache_size = _shell("sysctl -n hw.l3cachesize")

    # Memory
    mem_total_gb = None
    if platform.system() == "Linux":
        mem_kb = _shell("grep MemTotal /proc/meminfo | awk '{print $2}'")
        if mem_kb:
            try:
                mem_total_gb = round(int(mem_kb) / 1_048_576, 2)
            except ValueError:
                pass
    elif platform.system() == "Darwin":
        mem_bytes = _shell("sysctl -n hw.memsize")
        if mem_bytes:
            try:
                mem_total_gb = round(int(mem_bytes) / (1024**3), 2)
            except ValueError:
                pass

    # NumPy BLAS
    numpy_blas = ""
    try:
        blas_info = np.show_config(mode="dicts")
        if isinstance(blas_info, dict) and "blas_opt_info" in blas_info:
            numpy_blas = str(blas_info["blas_opt_info"].get("libraries", ""))
    except Exception:
        try:
            import io, contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                np.show_config()
            config_text = buf.getvalue()
            for line in config_text.splitlines():
                if "libraries" in line.lower() and "blas" in line.lower():
                    numpy_blas = line.strip()
                    break
        except Exception:
            pass

    return {
        "timestamp_utc":    datetime.datetime.utcnow().isoformat() + "Z",
        "hostname":         platform.node(),
        "os": {
            "system":       platform.system(),
            "release":      platform.release(),
            "version":      platform.version(),
            "arch":         platform.machine(),
        },
        "cpu": {
            "model":        cpu_model or platform.processor() or "unknown",
            "cores_logical": os.cpu_count(),
            "cores_physical": cpu_cores_phys,
            "freq_max_mhz": cpu_freq_mhz,
            "l3_cache":     cache_size or None,
        },
        "memory_gb":        mem_total_gb,
        "python": {
            "version":      platform.python_version(),
            "implementation": platform.python_implementation(),
            "compiler":     platform.python_compiler(),
        },
        "packages": {
            "numpy":        np.__version__,
            "novum_qvm":    PFQVS_VERSION,
            "qiskit":       QISKIT_VERSION,
        },
        "numpy_blas":       numpy_blas or None,
        "benchmark_config": {
            "repetitions":  REPS,
            "warmup":       WARMUP,
            "timer":        "time.perf_counter",
            "unit":         "milliseconds",
            "qubit_sizes":  QUBIT_SIZES,
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
#  Timing
# ══════════════════════════════════════════════════════════════════════════════

def benchmark(fn, reps=REPS, warmup=WARMUP) -> dict:
    """Run fn() with warmup + measured reps. Return full statistics in ms."""
    # warmup (discarded)
    for _ in range(warmup):
        fn()

    times = []
    for _ in range(reps):
        t0 = time.perf_counter()
        fn()
        elapsed = (time.perf_counter() - t0) * 1000.0
        times.append(elapsed)

    times.sort()
    return {
        "times_ms":  times,
        "min":       times[0],
        "max":       times[-1],
        "mean":      statistics.mean(times),
        "median":    statistics.median(times),
        "stddev":    statistics.stdev(times) if len(times) > 1 else 0.0,
        "rounds":    reps,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  Benchmark definitions
# ══════════════════════════════════════════════════════════════════════════════

# -- 1. State Initialization --------------------------------------------------
def bench_init_pfqvs(n):
    PFQVS_QuantumComputer(n_qubits=n)

def bench_init_qiskit(n):
    Statevector(np.zeros(1 << n, dtype=complex))

# -- 2. H-gate chain ----------------------------------------------------------
def bench_h_chain_pfqvs(n):
    qc = PFQVS_QuantumComputer(n_qubits=n)
    for i in range(n):
        qc.apply_gate('H', i)

def bench_h_chain_qiskit(n):
    circ = QuantumCircuit(n)
    for i in range(n):
        circ.h(i)
    Statevector(circ)

# -- 3. CNOT chain -------------------------------------------------------------
def bench_cnot_chain_pfqvs(n):
    qc = PFQVS_QuantumComputer(n_qubits=n)
    for i in range(n - 1):
        qc.apply_gate('CNOT', i, i + 1)

def bench_cnot_chain_qiskit(n):
    circ = QuantumCircuit(n)
    for i in range(n - 1):
        circ.cx(i, i + 1)
    Statevector(circ)

# -- 4. Bell state (fixed 2 qubits) -------------------------------------------
def bench_bell_pfqvs():
    qc = PFQVS_QuantumComputer(n_qubits=2)
    psi = np.zeros(4, dtype=complex); psi[0] = 1.0
    qc._set_flat_state(psi)
    qc.apply_gate('H', 0)
    qc.apply_gate('CNOT', 0, 1)

def bench_bell_qiskit():
    circ = QuantumCircuit(2)
    circ.h(0)
    circ.cx(0, 1)
    Statevector(circ)

# -- 5. Grover's search -------------------------------------------------------
def bench_grover_pfqvs(n):
    qc = PFQVS_QuantumComputer(n_qubits=n)
    qc.grovers_search('1' * n, shots=500)

def bench_grover_qiskit(n):
    N = 1 << n
    target_idx = N - 1
    psi = np.ones(N, dtype=complex) / np.sqrt(N)
    n_iter = max(1, int(round(np.pi / 4.0 * np.sqrt(N))))
    for _ in range(n_iter):
        psi[target_idx] *= -1.0
        mean = psi.mean()
        psi = 2.0 * mean - psi
    psi /= np.linalg.norm(psi)
    Statevector(psi)

# -- 6. Deutsch-Jozsa ----------------------------------------------------------
def bench_dj_pfqvs(n):
    qc = PFQVS_QuantumComputer(n_qubits=n)
    qc.deutsch_jozsa(lambda x: 0, shots=500)

def bench_dj_qiskit(n):
    N = 1 << n
    psi = np.ones(N, dtype=complex) / np.sqrt(N)
    ft = np.fft.fft(psi) / np.sqrt(N)
    ft /= np.linalg.norm(ft)
    Statevector(ft)


# ══════════════════════════════════════════════════════════════════════════════
#  Runner
# ══════════════════════════════════════════════════════════════════════════════

BENCHMARKS = [
    {
        "name":        "state_init",
        "description": "State initialization (Perlin vs zero-vector)",
        "pfqvs_fn":    bench_init_pfqvs,
        "qiskit_fn":   bench_init_qiskit,
        "sizes":       QUBIT_SIZES,
        "param":       "n_qubits",
    },
    {
        "name":        "h_chain",
        "description": "H-gate chain (n sequential Hadamards)",
        "pfqvs_fn":    bench_h_chain_pfqvs,
        "qiskit_fn":   bench_h_chain_qiskit,
        "sizes":       QUBIT_SIZES,
        "param":       "n_qubits",
    },
    {
        "name":        "cnot_chain",
        "description": "CNOT chain (n-1 sequential CNOTs)",
        "pfqvs_fn":    bench_cnot_chain_pfqvs,
        "qiskit_fn":   bench_cnot_chain_qiskit,
        "sizes":       [n for n in QUBIT_SIZES if n >= 2],
        "param":       "n_qubits",
    },
    {
        "name":        "grover",
        "description": "Grover's search (full algorithm)",
        "pfqvs_fn":    bench_grover_pfqvs,
        "qiskit_fn":   bench_grover_qiskit,
        "sizes":       [n for n in QUBIT_SIZES if n <= 16],
        "param":       "n_qubits",
    },
    {
        "name":        "deutsch_jozsa",
        "description": "Deutsch-Jozsa (full algorithm)",
        "pfqvs_fn":    bench_dj_pfqvs,
        "qiskit_fn":   bench_dj_qiskit,
        "sizes":       QUBIT_SIZES,
        "param":       "n_qubits",
    },
]


def run_benchmarks():
    sysinfo = collect_system_info()
    all_results = []

    total = sum(len(b["sizes"]) for b in BENCHMARKS) + 1  # +1 for bell
    done = 0

    for bdef in BENCHMARKS:
        name  = bdef["name"]
        desc  = bdef["description"]
        sizes = bdef["sizes"]

        print(f"\n{'─'*72}")
        print(f"  {desc}")
        print(f"{'─'*72}")
        hdr = f"{'qubits':>6}  {'PFQVS (ms)':>14}  {'Qiskit (ms)':>14}  {'speedup':>10}"
        print(hdr)
        print(f"{'──────':>6}  {'──────────────':>14}  {'──────────────':>14}  {'──────────':>10}")

        for n in sizes:
            done += 1
            pct = done / total * 100
            sys.stdout.write(f"\r  [{pct:5.1f}%] n={n:>2} ... ")
            sys.stdout.flush()

            p_stats = benchmark(lambda n=n: bdef["pfqvs_fn"](n))

            if HAS_QISKIT:
                q_stats = benchmark(lambda n=n: bdef["qiskit_fn"](n))
                ratio = q_stats["median"] / p_stats["median"] if p_stats["median"] > 0 else float("inf")
                q_med_str = f"{q_stats['median']:.3f}"
                ratio_str = f"{ratio:.2f}x"
            else:
                q_stats = None
                q_med_str = "N/A"
                ratio_str = "N/A"
                ratio = None

            sys.stdout.write("\r")
            print(f"{n:>6}  {p_stats['median']:>14.3f}  {q_med_str:>14}  {ratio_str:>10}")

            entry = {
                "benchmark":   name,
                "description": desc,
                "param":       bdef["param"],
                "param_value": n,
                "pfqvs":       p_stats,
                "qiskit":      q_stats,
                "speedup_qiskit_over_pfqvs": ratio,
            }
            # strip raw times from JSON to keep it clean (keep stats)
            for key in ("pfqvs", "qiskit"):
                if entry[key] is not None:
                    entry[key] = {k: v for k, v in entry[key].items() if k != "times_ms"}

            all_results.append(entry)

    # Bell state (fixed, not parameterized)
    done += 1
    print(f"\n{'─'*72}")
    print(f"  Bell state preparation (2 qubits, fixed)")
    print(f"{'─'*72}")
    p_bell = benchmark(bench_bell_pfqvs)
    if HAS_QISKIT:
        q_bell = benchmark(bench_bell_qiskit)
        bell_ratio = q_bell["median"] / p_bell["median"] if p_bell["median"] > 0 else float("inf")
        print(f"  PFQVS  : {p_bell['median']:.3f} ms  (std {p_bell['stddev']:.3f})")
        print(f"  Qiskit : {q_bell['median']:.3f} ms  (std {q_bell['stddev']:.3f})")
        print(f"  Speedup: {bell_ratio:.2f}x (Qiskit / PFQVS)")
    else:
        q_bell = None
        bell_ratio = None
        print(f"  PFQVS  : {p_bell['median']:.3f} ms  |  Qiskit: N/A")

    bell_entry = {
        "benchmark":   "bell_state",
        "description": "Bell state preparation (H + CNOT, 2 qubits)",
        "param":       "n_qubits",
        "param_value": 2,
        "pfqvs":       {k: v for k, v in p_bell.items() if k != "times_ms"},
        "qiskit":      {k: v for k, v in q_bell.items() if k != "times_ms"} if q_bell else None,
        "speedup_qiskit_over_pfqvs": bell_ratio,
    }
    all_results.append(bell_entry)

    # ── Scaling exponents ─────────────────────────────────────────────────
    print(f"\n{'─'*72}")
    print(f"  Empirical scaling exponents  (time ~ 2^(alpha * n))")
    print(f"{'─'*72}")
    print(f"  {'benchmark':<16}  {'PFQVS alpha':>12}  {'Qiskit alpha':>12}")
    print(f"  {'-'*16}  {'-'*12}  {'-'*12}")

    scaling = {}
    for bdef in BENCHMARKS:
        name = bdef["name"]
        rows = [r for r in all_results if r["benchmark"] == name]
        ns = np.array([r["param_value"] for r in rows], dtype=float)
        ps = np.array([r["pfqvs"]["median"] for r in rows], dtype=float)

        valid_p = ps > 0
        if valid_p.sum() >= 2:
            p_alpha = float(np.polyfit(ns[valid_p], np.log2(ps[valid_p]), 1)[0])
        else:
            p_alpha = None

        q_alpha = None
        if HAS_QISKIT:
            qs = np.array([r["qiskit"]["median"] if r["qiskit"] else np.nan for r in rows])
            valid_q = ~np.isnan(qs) & (qs > 0)
            if valid_q.sum() >= 2:
                q_alpha = float(np.polyfit(ns[valid_q], np.log2(qs[valid_q]), 1)[0])

        scaling[name] = {"pfqvs_alpha": p_alpha, "qiskit_alpha": q_alpha}
        pa_str = f"{p_alpha:.4f}" if p_alpha is not None else "N/A"
        qa_str = f"{q_alpha:.4f}" if q_alpha is not None else "N/A"
        print(f"  {name:<16}  {pa_str:>12}  {qa_str:>12}")

    return sysinfo, all_results, scaling


# ══════════════════════════════════════════════════════════════════════════════
#  Output writers
# ══════════════════════════════════════════════════════════════════════════════

def write_json(sysinfo, results, scaling, path):
    """Write ASV / pytest-benchmark style JSON."""
    doc = {
        "schema_version":   "1.0",
        "format":           "pfqvs-benchmark",
        "generated_utc":    datetime.datetime.utcnow().isoformat() + "Z",
        "system":           sysinfo,
        "scaling_exponents": scaling,
        "benchmarks":       results,
    }
    with open(path, "w") as f:
        json.dump(doc, f, indent=2, default=str)
    print(f"  -> JSON written to {path}")


def write_csv(results, path):
    """Write flat CSV suitable for pandas / spreadsheet import."""
    cols = [
        "benchmark", "param", "param_value",
        "pfqvs_median_ms", "pfqvs_mean_ms", "pfqvs_std_ms",
        "pfqvs_min_ms", "pfqvs_max_ms",
        "qiskit_median_ms", "qiskit_mean_ms", "qiskit_std_ms",
        "qiskit_min_ms", "qiskit_max_ms",
        "speedup",
    ]
    with open(path, "w") as f:
        f.write(",".join(cols) + "\n")
        for r in results:
            p = r["pfqvs"]
            q = r["qiskit"]
            row = [
                r["benchmark"],
                r["param"],
                str(r["param_value"]),
                f"{p['median']:.4f}",
                f"{p['mean']:.4f}",
                f"{p['stddev']:.4f}",
                f"{p['min']:.4f}",
                f"{p['max']:.4f}",
                f"{q['median']:.4f}" if q else "",
                f"{q['mean']:.4f}" if q else "",
                f"{q['stddev']:.4f}" if q else "",
                f"{q['min']:.4f}" if q else "",
                f"{q['max']:.4f}" if q else "",
                f"{r['speedup_qiskit_over_pfqvs']:.2f}" if r['speedup_qiskit_over_pfqvs'] is not None else "",
            ]
            f.write(",".join(row) + "\n")
    print(f"  -> CSV written to {path}")


def write_latex(sysinfo, results, scaling, path):
    """Write a self-contained LaTeX fragment with benchmark tables."""
    lines = []
    L = lines.append

    L("% Auto-generated by benchmark.py")
    L(f"% {sysinfo['timestamp_utc']}")
    L(f"% CPU: {sysinfo['cpu']['model']}")
    L(f"% RAM: {sysinfo['memory_gb']} GB")
    L(f"% Python {sysinfo['python']['version']}, "
      f"NumPy {sysinfo['packages']['numpy']}, "
      f"novum-qvm {sysinfo['packages']['novum_qvm']}, "
      f"Qiskit {sysinfo['packages']['qiskit'] or 'N/A'}")
    L(f"% Repetitions: {REPS}, Warmup: {WARMUP}, Timer: time.perf_counter")
    L("")

    # ── Main comparison table ─────────────────────────────────────────
    L("\\begin{table}[t]")
    L("\\centering")
    L("\\caption{PFQVS vs.\\ Qiskit Statevector: median wall-clock time (ms) over "
      f"{REPS} trials after {WARMUP} warmup iterations.  "
      "Speedup $>1$ means PFQVS is slower; $<1$ means PFQVS is faster.}}")
    L("\\label{tab:bench_comparison}")
    L("\\begin{tabular}{@{}llrrr@{}}")
    L("\\toprule")
    L("Benchmark & $n$ & PFQVS (ms) & Qiskit (ms) & Ratio \\\\")
    L("\\midrule")

    prev_bench = None
    for r in results:
        name = r["benchmark"].replace("_", "\\_")
        n    = r["param_value"]
        p_med = r["pfqvs"]["median"]
        q_med = r["qiskit"]["median"] if r["qiskit"] else None
        spd   = r["speedup_qiskit_over_pfqvs"]

        bench_col = name if r["benchmark"] != prev_bench else ""
        prev_bench = r["benchmark"]

        q_str = f"{q_med:.3f}" if q_med is not None else "---"
        s_str = f"{spd:.2f}$\\times$" if spd is not None else "---"
        L(f"{bench_col} & {n} & {p_med:.3f} & {q_str} & {s_str} \\\\")

    L("\\bottomrule")
    L("\\end{tabular}")
    L("\\end{table}")
    L("")

    # ── Scaling exponent table ────────────────────────────────────────
    L("\\begin{table}[t]")
    L("\\centering")
    L("\\caption{Empirical scaling exponents $\\alpha$ from log-linear fit "
      "$\\log_2 t = \\alpha\\, n + c$ where $n$ is qubit count and $t$ is "
      "median wall-clock time (ms).}}")
    L("\\label{tab:scaling}")
    L("\\begin{tabular}{@{}lcc@{}}")
    L("\\toprule")
    L("Benchmark & PFQVS $\\alpha$ & Qiskit $\\alpha$ \\\\")
    L("\\midrule")
    for name, sc in scaling.items():
        label = name.replace("_", "\\_")
        pa = f"{sc['pfqvs_alpha']:.4f}" if sc["pfqvs_alpha"] is not None else "---"
        qa = f"{sc['qiskit_alpha']:.4f}" if sc["qiskit_alpha"] is not None else "---"
        L(f"{label} & {pa} & {qa} \\\\")
    L("\\bottomrule")
    L("\\end{tabular}")
    L("\\end{table}")

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  -> LaTeX written to {path}")


# ══════════════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 72)
    print("  PFQVS vs Qiskit Statevector — Benchmark Suite")
    print("=" * 72)

    sysinfo = collect_system_info()

    # Print system info
    print(f"\n  System Information")
    print(f"  {'─'*60}")
    print(f"  Host       : {sysinfo['hostname']}")
    print(f"  OS         : {sysinfo['os']['system']} {sysinfo['os']['release']} ({sysinfo['os']['arch']})")
    print(f"  CPU        : {sysinfo['cpu']['model']}")
    print(f"  Cores      : {sysinfo['cpu']['cores_physical']} physical, {sysinfo['cpu']['cores_logical']} logical")
    if sysinfo['cpu']['freq_max_mhz']:
        print(f"  CPU freq   : {sysinfo['cpu']['freq_max_mhz']:.0f} MHz max")
    if sysinfo['cpu']['l3_cache']:
        print(f"  L3 cache   : {sysinfo['cpu']['l3_cache']}")
    if sysinfo['memory_gb']:
        print(f"  Memory     : {sysinfo['memory_gb']} GB")
    print(f"  Python     : {sysinfo['python']['version']} ({sysinfo['python']['implementation']})")
    print(f"  NumPy      : {sysinfo['packages']['numpy']}")
    print(f"  novum-qvm  : {sysinfo['packages']['novum_qvm']}")
    print(f"  Qiskit     : {sysinfo['packages']['qiskit'] or 'not installed'}")
    print(f"  Timer      : time.perf_counter")
    print(f"  Reps/trial : {REPS} (+ {WARMUP} warmup)")
    print(f"  Timestamp  : {sysinfo['timestamp_utc']}")

    # Run benchmarks
    sysinfo, results, scaling = run_benchmarks()

    # Write outputs
    print(f"\n{'═'*72}")
    print("  Writing output files")
    print(f"{'═'*72}")

    json_path  = os.path.join(OUTPUT_DIR, "benchmark_results.json")
    csv_path   = os.path.join(OUTPUT_DIR, "benchmark_results.csv")
    latex_path = os.path.join(OUTPUT_DIR, "benchmark_table.tex")

    write_json(sysinfo, results, scaling, json_path)
    write_csv(results, csv_path)
    write_latex(sysinfo, results, scaling, latex_path)

    print(f"\n{'═'*72}")
    print("  Benchmark complete.")
    print(f"{'═'*72}\n")