import json
import os
import pandas as pd
import matplotlib.pyplot as plt

def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_k6_metrics(file_path, test_name):
    data = load_json_file(file_path)
    metrics = data["metrics"]

    http_req_duration = metrics.get("http_req_duration", {})
    http_req_failed = metrics.get("http_req_failed", {})
    http_reqs = metrics.get("http_reqs", {})

    p95 = http_req_duration.get("p(95)", 0)
    avg = http_req_duration.get("avg", 0)
    error_rate = http_req_failed.get("rate", 0)
    total_requests = http_reqs.get("count", 0)

    return {
        "test_name": test_name,
        "p95_response_time_ms": p95,
        "average_response_time_ms": avg,
        "error_rate": error_rate,
        "total_requests": total_requests,
    }


def evaluate_status(result, threshold_p95_ms=3000, threshold_error_rate=0.1):
    p95 = result["p95_response_time_ms"]
    error_rate = result["error_rate"]

    if p95 < threshold_p95_ms and error_rate < threshold_error_rate:
        return "PASS"
    return "FAIL"


def classify_performance(result):
    p95 = result["p95_response_time_ms"]
    error_rate = result["error_rate"]

    if p95 < 1000 and error_rate == 0:
        return "EXCELLENT"
    elif p95 < 3000 and error_rate < 0.1:
        return "GOOD"
    elif p95 < 5000 or error_rate < 0.3:
        return "WARNING"
    else:
        return "CRITICAL"


def generate_comparison_report(results):
    report = "# k6 Performance Test Comparison Report\n\n"

    report += "## Summary Table\n\n"
    report += "| Test Name | P95 Response Time | Average Response Time | Error Rate | Total Requests | Status | Category |\n"
    report += "|---|---:|---:|---:|---:|---|---|\n"

    for result in results:
        status = evaluate_status(result)
        category = classify_performance(result)

        report += (
            f"| {result['test_name']} "
            f"| {result['p95_response_time_ms']:.2f} ms "
            f"| {result['average_response_time_ms']:.2f} ms "
            f"| {result['error_rate']:.2%} "
            f"| {result['total_requests']} "
            f"| {status} "
            f"| {category} |\n"
        )

        report += "\n## Performance Charts\n\n"
    report += "### P95 Response Time\n\n"
    report += "![P95 Response Time](charts/p95_response_time_chart.png)\n\n"

    report += "### Average Response Time\n\n"
    report += "![Average Response Time](charts/average_response_time_chart.png)\n\n"

    report += "### Error Rate\n\n"
    report += "![Error Rate](charts/error_rate_chart.png)\n\n"

    report += "### Total Requests\n\n"
    report += "![Total Requests](charts/total_requests_chart.png)\n\n"
    report += "\n## Overall Interpretation\n\n"
    report += generate_overall_interpretation(results)

    return report


def generate_overall_interpretation(results):
    failed_tests = []

    for result in results:
        status = evaluate_status(result)
        if status == "FAIL":
            failed_tests.append(result["test_name"])

    if len(failed_tests) == 0:
        return (
            "Seluruh skenario pengujian berhasil memenuhi threshold yang ditentukan. "
            "Hal ini menunjukkan bahwa sistem memiliki performa yang stabil pada skenario load, spike, dan stress test."
        )

    failed_test_names = ", ".join(failed_tests)

    return (
        f"Terdapat skenario pengujian yang belum memenuhi threshold, yaitu: {failed_test_names}. "
        "Hal ini menunjukkan bahwa sistem masih perlu dianalisis lebih lanjut, terutama pada aspek latency, "
        "kapasitas server, proses backend, dan penggunaan resource saat beban meningkat."
    )


def save_report(report_content, output_path):
    os.makedirs("reports", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(report_content)

    print(f"Comparison report berhasil disimpan ke: {output_path}")

def save_summary_to_csv(results, output_path):
    """
    Menyimpan ringkasan hasil performance test ke file CSV.
    """
    summary_data = []

    for result in results:
        status = evaluate_status(result)
        category = classify_performance(result)

        summary_data.append({
            "test_name": result["test_name"],
            "p95_response_time_ms": round(result["p95_response_time_ms"], 2),
            "average_response_time_ms": round(result["average_response_time_ms"], 2),
            "error_rate": round(result["error_rate"], 4),
            "total_requests": result["total_requests"],
            "status": status,
            "category": category
        })

    df = pd.DataFrame(summary_data)

    os.makedirs("reports", exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Summary CSV berhasil disimpan ke: {output_path}")

def generate_performance_charts(results):
    """
    Membuat grafik performa dari hasil load, spike, dan stress test.
    Grafik akan disimpan ke folder reports/charts.
    """
    chart_dir = "reports/charts"
    os.makedirs(chart_dir, exist_ok=True)

    test_names = [result["test_name"] for result in results]
    p95_values = [result["p95_response_time_ms"] for result in results]
    avg_values = [result["average_response_time_ms"] for result in results]
    error_rates = [result["error_rate"] * 100 for result in results]
    total_requests = [result["total_requests"] for result in results]

    # Chart 1: P95 Response Time
    plt.figure(figsize=(10, 6))
    plt.bar(test_names, p95_values)
    plt.title("P95 Response Time Comparison")
    plt.xlabel("Test Scenario")
    plt.ylabel("P95 Response Time (ms)")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(os.path.join(chart_dir, "p95_response_time_chart.png"))
    plt.close()

    # Chart 2: Average Response Time
    plt.figure(figsize=(10, 6))
    plt.bar(test_names, avg_values)
    plt.title("Average Response Time Comparison")
    plt.xlabel("Test Scenario")
    plt.ylabel("Average Response Time (ms)")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(os.path.join(chart_dir, "average_response_time_chart.png"))
    plt.close()

    # Chart 3: Error Rate
    plt.figure(figsize=(10, 6))
    plt.bar(test_names, error_rates)
    plt.title("Error Rate Comparison")
    plt.xlabel("Test Scenario")
    plt.ylabel("Error Rate (%)")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(os.path.join(chart_dir, "error_rate_chart.png"))
    plt.close()

    # Chart 4: Total Requests
    plt.figure(figsize=(10, 6))
    plt.bar(test_names, total_requests)
    plt.title("Total Requests Comparison")
    plt.xlabel("Test Scenario")
    plt.ylabel("Total Requests")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(os.path.join(chart_dir, "total_requests_chart.png"))
    plt.close()

    print(f"Performance charts berhasil disimpan ke folder: {chart_dir}")

def main():
    test_files = [
        {
            "file_path": "k6-results/login-load-test-result.json",
            "test_name": "Login Load Test",
        },
        {
            "file_path": "k6-results/login-spike-test-result.json",
            "test_name": "Login Spike Test",
        },
        {
            "file_path": "k6-results/login-stress-test-result.json",
            "test_name": "Login Stress Test",
        },
    ]

    results = []

    for test in test_files:
        result = extract_k6_metrics(test["file_path"], test["test_name"])
        results.append(result)

    generate_performance_charts(results)

    report_content = generate_comparison_report(results)
    save_report(report_content, "reports/performance-comparison-report.md")

    save_summary_to_csv(results, "reports/performance-summary.csv")

if __name__ == "__main__":
    main()