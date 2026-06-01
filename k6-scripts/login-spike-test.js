import http from 'k6/http';
import { check, sleep } from 'k6';

/**
 * K6 Spike Test - Login Endpoint
 * 
 * Mensimulasikan lonjakan beban tiba-tiba dalam waktu singkat
 * untuk melihat respons sistem terhadap perubahan mendadak.
 * 
 * Stages:
 *   1. Normal: 5 VU (30s) — baseline normal
 *   2. Spike: 5 → 100 VU (5s) — lonjakan mendadak
 *   3. Peak: 100 VU (30s) — tahan di puncak
 *   4. Drop: 100 → 5 VU (5s) — turun mendadak
 *   5. Recovery: 5 VU (30s) — observasi pemulihan
 *   6. Spike 2: 5 → 100 VU (5s) — lonjakan kedua
 *   7. Peak 2: 100 VU (30s) — tahan di puncak lagi
 *   8. Ramp-down: 100 → 0 VU (10s) — selesai
 * 
 * Total durasi: ~2.5 menit
 * 
 * Cara menjalankan:
 *   k6 run cypress/performance/login-spike-test.js
 */

const envFile = JSON.parse(open('../cypress.env.json'));

const BASE_URL = 'https://api-customer-dev.temansantaimu.com';
const USER_PHONE = envFile.USER_PHONE;
const USER_PASSWORD = envFile.USER_PASSWORD;

export const options = {
    stages: [
        { duration: '30s', target: 5 },    // baseline normal
        { duration: '5s', target: 100 },   // SPIKE — lonjakan mendadak ke 100 VU
        { duration: '30s', target: 100 },  // tahan di puncak
        { duration: '5s', target: 5 },     // DROP — turun mendadak
        { duration: '30s', target: 5 },    // recovery / pemulihan
        { duration: '5s', target: 100 },   // SPIKE kedua
        { duration: '30s', target: 100 },  // tahan di puncak lagi
        { duration: '10s', target: 0 },    // ramp-down
    ],
    thresholds: {
        http_req_duration: ['p(95)<5000'],  // 95% request harus di bawah 5 detik
        http_req_failed: ['rate<0.3'],      // error rate di bawah 30%
    },
};

export default function () {
    const loginPayload = JSON.stringify({
        nomor: USER_PHONE,
        password: USER_PASSWORD,
    });

    const headers = {
        'Content-Type': 'application/json',
    };

    const res = http.post(`${BASE_URL}/auth/login`, loginPayload, { headers });

    check(res, {
        'status is 200': (r) => r.status === 200,
        'response time < 2000ms': (r) => r.timings.duration < 2000,
        'response time < 5000ms': (r) => r.timings.duration < 5000,
        'response has body': (r) => r.body && r.body.length > 0,
    });

    sleep(0.3); // jeda sangat pendek untuk memaksimalkan tekanan saat spike
}
