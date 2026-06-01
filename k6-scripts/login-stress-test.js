import http from 'k6/http';
import { check, sleep } from 'k6';

/**
 * K6 Stress Test - Login Endpoint
 * 
 * Meningkatkan beban secara bertahap ke angka ekstrem untuk menemukan
 * titik di mana sistem mulai rusak/lambat (breaking point).
 * 
 * 
 * Total durasi: ~6 menit
 * 
 * Cara menjalankan:
 *   k6 run cypress/performance/login-stress-test.js
 */

const envFile = JSON.parse(open('../cypress.env.json'));

const BASE_URL = 'https://api-customer-dev.temansantaimu.com';
const USER_PHONE = envFile.USER_PHONE;
const USER_PASSWORD = envFile.USER_PASSWORD;

export const options = {
    stages: [
        { duration: '30s', target: 10 },   // warm-up ke 10 VU
        { duration: '1m', target: 10 },    // tahan 10 VU
        { duration: '30s', target: 25 },   // naikkan ke 25 VU
        { duration: '1m', target: 25 },    // tahan 25 VU
        { duration: '30s', target: 50 },   // naikkan ke 50 VU
        { duration: '1m', target: 50 },    // tahan 50 VU
        { duration: '30s', target: 75 },   // naikkan ke 75 VU
        { duration: '1m', target: 75 },    // tahan 75 VU
        { duration: '30s', target: 100 },  // naikkan ke 100 VU
        { duration: '1m', target: 100 },   // tahan 100 VU (max stress)
        { duration: '30s', target: 0 },    // ramp-down / recovery
    ],
    thresholds: {
        http_req_duration: ['p(95)<5000'],  // 95% request harus di bawah 5 detik
        http_req_failed: ['rate<0.5'],      // error rate di bawah 50% (toleransi tinggi untuk stress)
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
        'response time < 3000ms': (r) => r.timings.duration < 3000,
        'response time < 5000ms': (r) => r.timings.duration < 5000,
        'response has body': (r) => r.body && r.body.length > 0,
    });

    sleep(0.5); // jeda per request
}