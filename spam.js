const http = require('http');

let requestsSent = 0;

function sendRequest(url) {
    const options = {
        headers: {
            'Referer': 'https://whathow.neocities.org'
        }
    };

    http.get(url, options, (res) => {
        console.log(`Request to ${url} - Status code: ${res.statusCode}`);
        requestsSent++;
        console.log(`${requestsSent} requests sent so far.`);
    }).on('error', (err) => {
        console.error(`Error sending request: ${err.message}`);
    });
}

function continuousRequests(url) {
    setInterval(() => {
        for (let i = 0; i < 50; i++) {
            sendRequest(url);
        }
    }, 100);
}

const url = "https://counter11.freecounterstat.com/private/counter.php?c=pdz4dufhlf9qlk4krksnw7twxbhlez2e&init=1711161297330&init_freecounterstat=0&library=library_counters&coef=0.75&type=193&lenght=9&pv=0";
continuousRequests(url);
