# Make sure to be in the /FlaskApp directory when running or logging will not work correctly

### For running in Docker locally (In /FlaskApp):
    docker build --tag python-docker .
    docker run -d -p 5000:5000 python-docker