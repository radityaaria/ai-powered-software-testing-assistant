import json
import sys
import os


def load_json_file(file_path):
    """
    Membaca file JSON dan mengembalikan datanya dalam bentuk dictionary Python.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def is_k6_summary_format(data):
    """
    Mengecek apakah file JSON berasal dari hasil asli k6 --summary-export.
    """
    return "metrics" in data


def extract_from_k6_summary(data):
    """
    Mengambil metric penting dari file hasil asli k6.
    """
    metrics = data["metrics"]

    http_req_duration = metrics.get("http_req_duration", {})
    http_req_failed = metrics.get("http_req_failed", {})
    http_reqs = metrics.get("http_reqs", {})

    return {
        "test_name": "k6 Performance Test",
        "test_type": "real k6 summary",
        "p95_response_time_ms": http_req_duration.get("p(95)", 0),
        "average_response_time_ms": http_req_duration.get("avg", 0),
        "error_rate": http_req_failed.get("rate", 0),
        "total_requests": http_reqs.get("count", 0),
        "threshold_p95_ms": 3000,
        "threshold_error_rate": 0.1
    }


def extract_from_sample_json(data):
    """
    Mengambil metric dari file sample JSON manual.
    """
    return {
        "test_name": data["test_name"],
        "test_type": data["test_type"],
        "p95_response_time_ms": data["p95_response_time_ms"],
        "average_response_time_ms": data["average_response_time_ms"],
        "error_rate": data["error_rate"],
        "total_requests": data["total_requests"],
        "threshold_p95_ms": data["threshold_p95_ms"],
        "threshold_error_rate": data["threshold_error_rate"]
    }


def normalize_k6_result(data):
    """
    Menyamakan format data, baik dari sample JSON maupun hasil asli k6.
    """
    if is_k6_summary_format(data):
        return extract_from_k6_summary(data)
    else:
        return extract_from_sample_json(data)


def evaluate_result(result):
    """
    Mengevaluasi hasil performance test berdasarkan threshold p95 dan error rate.
    """
    p95 = result["p95_response_time_ms"]
    error_rate = result["error_rate"]

    threshold_p95 = result["threshold_p95_ms"]
    threshold_error_rate = result["threshold_error_rate"]

    is_p95_pass = p95 < threshold_p95
    is_error_rate_pass = error_rate < threshold_error_rate

    if is_p95_pass and is_error_rate_pass:
        status = "PASS"
        interpretation = (
            "Test berhasil karena p95 response time dan error rate "
            "masih berada di bawah threshold yang ditentukan."
        )
    elif not is_p95_pass and is_error_rate_pass:
        status = "FAIL"
        interpretation = (
            "Test gagal karena p95 response time melebihi threshold, "
            "meskipun error rate masih rendah. Ini menunjukkan adanya masalah latency."
        )
    elif is_p95_pass and not is_error_rate_pass:
        status = "FAIL"
        interpretation = (
            "Test gagal karena error rate melebihi threshold, "
            "meskipun response time masih memenuhi batas yang ditentukan."
        )
    else:
        status = "FAIL"
        interpretation = (
            "Test gagal karena p95 response time dan error rate "
            "sama-sama melebihi threshold."
        )

    return status, interpretation

def classify_performance(result):
    """
    Mengklasifikasikan kualitas performa berdasarkan p95 dan error rate.
    """
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

def generate_recommendation(result, status, performance_category):
    """
    Memberikan rekomendasi sederhana berdasarkan hasil performance test.
    """
    p95 = result["p95_response_time_ms"]
    error_rate = result["error_rate"]

    if performance_category == "EXCELLENT":
        return (
            "Performa sistem sangat baik. Endpoint mampu menangani beban pengujian "
            "dengan response time rendah dan tanpa error."
        )

    elif performance_category == "GOOD":
        return (
            "Performa sistem masih baik. Namun, tetap disarankan melakukan pengujian "
            "dengan beban lebih tinggi untuk mengetahui batas kemampuan sistem."
        )

    elif performance_category == "WARNING":
        if p95 >= 3000:
            return (
                "Terdapat indikasi latency yang perlu diperhatikan. Disarankan melakukan "
                "analisis pada backend, query database, proses autentikasi, dan penggunaan CPU."
            )
        elif error_rate >= 0.1:
            return (
                "Error rate mulai meningkat. Disarankan memeriksa log server, validasi response, "
                "serta kemungkinan timeout atau rate limiting."
            )
        else:
            return (
                "Performa perlu dipantau lebih lanjut karena terdapat indikasi awal penurunan kualitas layanan."
            )

    else:
        return (
            "Performa sistem berada pada kondisi kritis. Disarankan melakukan optimasi backend, "
            "database, konfigurasi server, serta monitoring CPU, memory, dan network secara menyeluruh."
        )

def print_report(result, status, interpretation, performance_category, recommendation):
    """
    Menampilkan laporan hasil analisis ke terminal.
    """
    print("k6 Performance Result Analyzer")
    print("=" * 40)

    print(f"Test Name: {result['test_name']}")
    print(f"Test Type: {result['test_type']}")
    print(f"P95 Response Time: {result['p95_response_time_ms']:.2f} ms")
    print(f"Average Response Time: {result['average_response_time_ms']:.2f} ms")
    print(f"Error Rate: {result['error_rate']:.2%}")
    print(f"Total Requests: {result['total_requests']}")
    print(f"Threshold P95: {result['threshold_p95_ms']} ms")
    print(f"Threshold Error Rate: {result['threshold_error_rate']:.2%}")
    print(f"Final Status: {status}")
    print(f"Performance Category: {performance_category}")
    print(f"Interpretation: {interpretation}")
    print(f"Recommendation: {recommendation}")

def generate_markdown_report(result, status, interpretation, performance_category, recommendation):
    """
    Membuat isi report dalam format Markdown.
    """
    report = f"""# k6 Performance Test Report

## Test Summary

| Metric | Value |
|---|---:|
| Test Name | {result['test_name']} |
| Test Type | {result['test_type']} |
| P95 Response Time | {result['p95_response_time_ms']:.2f} ms |
| Average Response Time | {result['average_response_time_ms']:.2f} ms |
| Error Rate | {result['error_rate']:.2%} |
| Total Requests | {result['total_requests']} |
| Threshold P95 | {result['threshold_p95_ms']} ms |
| Threshold Error Rate | {result['threshold_error_rate']:.2%} |
| Final Status | {status} |
| Performance Category | {performance_category} |

## Interpretation

{interpretation}

## Recommendation

{recommendation}
"""
    return report

def save_report_to_file(report_content, output_path):
    """
    Menyimpan report Markdown ke file.
    """
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(report_content)

    print(f"Report berhasil disimpan ke: {output_path}")

def generate_output_report_path(input_file_path):
    """
    Membuat nama file report otomatis berdasarkan nama file input.
    Contoh:
    k6-results/login-spike-test-result.json -> reports/login-spike-test-result_report.md
    """
    file_name = os.path.basename(input_file_path)
    file_name_without_extension = os.path.splitext(file_name)[0]

    output_file_name = f"{file_name_without_extension}_report.md"
    output_path = os.path.join("reports", output_file_name)

    return output_path

def main():
    """
    Program utama.
    Bisa membaca file default atau file dari argument terminal.
    """

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "k6-results/hasil_k6.json"

    try:
        raw_data = load_json_file(file_path)
        result = normalize_k6_result(raw_data)

        status, interpretation = evaluate_result(result)
        performance_category = classify_performance(result)
        recommendation = generate_recommendation(
            result,
            status,
            performance_category
        )

        print_report(
            result,
            status,
            interpretation,
            performance_category,
            recommendation
        )

        report_content = generate_markdown_report(
            result,
            status,
            interpretation,
            performance_category,
            recommendation
        )

        output_path = generate_output_report_path(file_path)
        save_report_to_file(report_content, output_path)

    except FileNotFoundError:
        print(f"ERROR: File tidak ditemukan: {file_path}")
        print("Pastikan nama file dan lokasi folder sudah benar.")

    except KeyError as error:
        print(f"ERROR: Key JSON tidak ditemukan: {error}")
        print("Struktur file JSON tidak sesuai dengan format yang diharapkan.")

    except json.JSONDecodeError:
        print("ERROR: File bukan JSON valid.")
        print("Pastikan file hasil k6 memiliki format JSON yang benar.")

if __name__ == "__main__":
    main()