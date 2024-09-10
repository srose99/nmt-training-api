from flask import Flask, request, jsonify, abort
from prometheus_client import Summary, Counter, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from pythonjsonlogger import jsonlogger
import time
import logging
app = Flask(__name__)

requestHistory = ['Start']

linuxFlavours = [
    {
        "name": "Ubuntu",
        "supported_versions": [
            {
                "version": "24.04 Noble Numbat (LTS)",
                "release_date": "25/04/24",
                "end_date": "25/04/29"
            },
            {
                "version": "22.04 Jammy Jellyfish (LTS)",
                "release_date": "21/04/22",
                "end_date": "01/04/27"
            },
        ]
    },
    {
        "name": "Kali Linux",
        "supported_versions": [
            {
                "version": "Kali 2024.2",
                "release_date": "05/06/24",
                "end_date": "05/06/29"
            },
            {
                "version": "Kali 2023.4",
                "release_date": "05/12/23",
                "end_date": "05/12/26"
            }
        ]
    },
    {
        "name": "CentOS",
        "supported_versions": [
            {
                "version": "8",
                "release_date": "24/09/19",
                "end_date": "31/12/21"
            },
            {
                "version": "7",
                "release_date": "07/07/14",
                "end_date": "06/08/20"
            }
        ]
    },
]

REQUEST_TIME = Summary('request_latency_seconds', 'Time spent processing request')
NUMBER_OF_REQUESTS = Counter('number_of_requests', 'Number of times an endpoint has been accessed', ['endpoint'])

logger = logging.getLogger(__name__)
logHandler = logging.FileHandler('MikesApi.log')

log_format = '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d %(threadName)s'
formatter = jsonlogger.JsonFormatter(log_format)

logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

@app.route("/")
@REQUEST_TIME.time()
def getRequestHistory():
    NUMBER_OF_REQUESTS.labels(endpoint='/').inc()
    requestHistory.append('GET')
    logger.info('Successful GET')
    return linuxFlavours

@app.route("/", methods=['POST'])
@REQUEST_TIME.time()
def addPostRequestData():
    NUMBER_OF_REQUESTS.labels(endpoint='/').inc()
    data = request.data.decode('utf-8')
    logger.info('Successful POST', extra={'request_data': data})
    requestHistory.append(data)
    return '', 204

@app.route("/flavours/<distro>")
@REQUEST_TIME.time()
def getFlavourData(distro):
    NUMBER_OF_REQUESTS.labels(endpoint='/flavours/' + distro).inc()
    distro = distro.capitalize()

    for flavour in linuxFlavours:
        if flavour["name"].lower() == distro.lower():
            logger.info(f"Successful request for {distro}")
            return jsonify({
                "distro": flavour["name"],
                "supported versions": flavour["supported_versions"]
            })
    logger.error(f"Distribution {distro} not found")
    abort(404, description=f"Linux distribution '{distro}' not found")

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == "__main__":
    app.run(debug=True)
