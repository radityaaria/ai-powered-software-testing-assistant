import http from 'k6/http';
import { check, sleep } from 'k6';

/**
 * K6 Load Test - Login Endpoint
 * 
 * Menguji performa endpoint login customer temansantaimu.
 * 
 * Cara menjalankan:
 *   k6 run cypress/performance/login-load-test.js
 */

const envFile = JSON.parse(open('../cypress.env.json'));

const BASE_URL = 'https://api-customer-dev.temansantaimu.com';
const USER_PHONE = envFile.USER_PHONE;
const USER_PASSWORD = envFile.USER_PASSWORD;

export const options = {
    stages: [
        { duration: '10s', target: 5 },   // ramp-up ke 5 virtual users
        { duration: '30s', target: 5 },   // tahan 5 VU selama 30 detik
        { duration: '10s', target: 10 },   // naikkan ke 10 VU
        { duration: '30s', target: 10 },   // tahan 10 VU selama 30 detik
        { duration: '10s', target: 0 },    // ramp-down ke 0
    ],
    thresholds: {
        http_req_duration: ['p(95)<3000'], // 95% request harus di bawah 3 detik
        http_req_failed: ['rate<0.1'],     // error rate harus di bawah 10%
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

    // const res = http.post(`${BASE_URL}/auth/admin/login`, loginPayload, { headers }); // Panel admin
    const res = http.post(`${BASE_URL}/auth/login`, loginPayload, { headers });

    check(res, {
        'status is 200': (r) => r.status === 200,
        'response time < 3000ms': (r) => r.timings.duration < 3000,
        'response has body': (r) => r.body && r.body.length > 0,
    });

    sleep(1); // jeda 1 detik antar request per VU
}
