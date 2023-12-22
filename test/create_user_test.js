import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
    stages: [
        { duration: '30s', target: 20 },
        { duration: '1m', target: 20 },
        { duration: '10s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'],
    },
};

const BASE_URL = 'http://localhost:8000';

function uniqueEmail() {
    const date = Date.now().toString();
    return `test_${date}@example.com`;
}

export default function () {
    check(http.get(`${BASE_URL}/users/`), {
        'is status 200': (r) => r.status === 200,
    });

   check(http.get(`${BASE_URL}/users/by_role/?role=IU`), {
        'is status 200': (r) => r.status === 200,
    });


    sleep(1);
}

