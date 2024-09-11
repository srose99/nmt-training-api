from flask import Flask, request, jsonify, abort
from prometheus_client import Summary, Counter, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from pythonjsonlogger import jsonlogger
import time
import logging
app = Flask(__name__)

# A history of previous requests made, mainly for testing
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

#Prometheus Metrics
REQUEST_TIME = Summary('request_latency_seconds', 'Time spent processing request')
NUMBER_OF_REQUESTS = Counter('number_of_requests', 'Number of times an endpoint has been accessed', ['endpoint'])

#Assigning a logger file location, format, handler, and mode (In this case Debug)
logger = logging.getLogger(__name__)
logHandler = logging.FileHandler('MikesApi.log')

log_format = '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d %(threadName)s'
formatter = jsonlogger.JsonFormatter(log_format)

logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

@app.route("/")
@REQUEST_TIME.time() # Records latency of request
def getRequestHandler():
    NUMBER_OF_REQUESTS.labels(endpoint='/').inc() # Increment the prometheus counter metric
    requestHistory.append('GET')
    logger.info('Successful GET')
    return linuxFlavours

@app.route("/", methods=['POST'])
@REQUEST_TIME.time()
def addPostRequestData():
    NUMBER_OF_REQUESTS.labels(endpoint='/').inc()
    # If data of POST request is not in the JSON format throws a 400 error status
    if not request.is_json:
        logger.error('POST request data is not in JSON format')
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    # If data of POST doesnt contain correct key names throws the same 400 error status
    if 'name' not in data or 'supported_versions' not in data:
        logger.error('POST request data is missing required fields')
        return jsonify({"error": "Missing required fields: name or supported_versions"}), 400
    
    logger.info('Successful POST', extra={'request_data': data}) # Logs to log file on successful request
    linuxFlavours.append(data)
    return jsonify({"message": "Linux distribution added successfully"}), 201

@app.route("/flavours/<distro>")
@REQUEST_TIME.time()
def getFlavourData(distro):
    NUMBER_OF_REQUESTS.labels(endpoint='/flavours/' + distro).inc()
    distro = distro.capitalize()

    for flavour in linuxFlavours:
        if flavour["name"].lower() == distro.lower(): # Searches linuxFlavours for entries matching the name of the search parameter
            logger.info(f"Successful request for {distro}")
            
            supported_versions = ", ".join([version["version"] for version in flavour["supported_versions"]])
            end_dates = ", ".join([version["end_date"] for version in flavour["supported_versions"]])
            transformed_response = f"Distro Name: {flavour['name']}, Supported Versions: {supported_versions}, End Dates: {end_dates}" # Series of joins to transform the data to the correct format to become consumable for the user

            return transformed_response
        
    logger.error(f"Distribution {distro} not found")
    abort(404, description=f"Linux distribution '{distro}' not found") # If no Distro found matching search param abort with a 404 status code

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, { # Flask exporter for prometheus, enables the /metrics endpoint and displays metrics through the use of middleware
    '/metrics': make_wsgi_app()
})

if __name__ == "__main__":
    app.run(debug=True)
