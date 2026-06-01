import json
import os


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

    report_content = generate_comparison_report(results)
    save_report(report_content, "reports/performance-comparison-report.md")


if __name__ == "__main__":
    main()