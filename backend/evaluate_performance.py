"""
Evaluation Script — Throughput & Latency Benchmarks
Run from EduNexus_v2/backend/:
    python evaluate_performance.py

Produces numbers for your project report:
  - FR-03: JD processing rate (records/minute)
  - NFR-01: Query latency (<5s)
  - NFR-03: 3-hop graph traversal (<500ms)
"""

import time
import uuid
from app.services.graph_builder import graph_builder
from app.services.gap_analyzer import gap_analyzer

# ── 1. Ingestion Throughput (FR-03 target: >500 records/min) ─────────────────

def benchmark_ingestion_throughput(batch_size: int = 500):
    print(f"\n{'='*55}")
    print(f"  BENCHMARK 1: Ingestion Throughput (batch={batch_size})")
    print(f"{'='*55}")

    # Build a test batch
    test_skills = ["Python", "Java", "SQL", "Docker", "Kubernetes",
                   "React", "Node.js", "Machine Learning", "AWS", "Git"]

    batch = [
        {
            "job_id": str(uuid.uuid4()),
            "title":  "Test Engineer",
            "skills": test_skills[:5]
        }
        for _ in range(batch_size)
    ]

    t_start = time.perf_counter()
    graph_builder.process_job_batch(batch)
    elapsed = time.perf_counter() - t_start

    records_per_second = batch_size / elapsed
    records_per_minute = records_per_second * 60

    print(f"  Batch size:          {batch_size} records")
    print(f"  Time taken:          {elapsed:.3f}s")
    print(f"  Throughput:          {records_per_minute:,.0f} records/minute")
    print(f"  FR-03 target:        >500 records/minute")
    print(f"  FR-03 PASSED:        {records_per_minute > 500}")

    return {
        "batch_size":            batch_size,
        "elapsed_seconds":       round(elapsed, 3),
        "records_per_minute":    round(records_per_minute, 0),
        "fr03_target":           500,
        "fr03_passed":           records_per_minute > 500
    }


# ── 2. Query Latency (NFR-01 and NFR-03) ─────────────────────────────────────

def benchmark_query_latency():
    print(f"\n{'='*55}")
    print(f"  BENCHMARK 2: Query Latency")
    print(f"{'='*55}")

    report = gap_analyzer.get_full_latency_report()

    print(f"\n  Results:")
    print(f"  Metrics query:         {report['metrics_query_ms']}ms")
    print(f"  Gap priority query:    {report['gap_priority_query_ms']}ms")
    print(f"  Recommendation query:  {report.get('recommendation_query_ms', 'N/A')}ms")
    print(f"  3-hop traversal:       {report['three_hop_traversal_ms']}ms")
    print(f"  NFR-01 (<5000ms):      {'PASSED ✅' if report['nfr01_passed'] else 'FAILED ❌'}")
    print(f"  NFR-03 (<500ms):       {'PASSED ✅' if report['nfr03_passed'] else 'FAILED ❌'}")

    return report


# ── 3. Full Report ────────────────────────────────────────────────────────────

def run_all_benchmarks():
    print("\n🔬 EduNexus V2 — Performance Evaluation")
    print("=" * 55)

    throughput = benchmark_ingestion_throughput(batch_size=500)
    latency    = benchmark_query_latency()

    print(f"\n{'='*55}")
    print("  SUMMARY FOR PROJECT REPORT")
    print(f"{'='*55}")
    print(f"  FR-03  Ingestion throughput:  {throughput['records_per_minute']:,.0f} rec/min  "
          f"{'✅' if throughput['fr03_passed'] else '❌'}")
    print(f"  NFR-01 Total query latency:   {latency['metrics_query_ms']}ms            "
          f"{'✅' if latency['nfr01_passed'] else '❌'}")
    print(f"  NFR-03 3-hop traversal:       {latency['three_hop_traversal_ms']}ms            "
          f"{'✅' if latency['nfr03_passed'] else '❌'}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    run_all_benchmarks()
