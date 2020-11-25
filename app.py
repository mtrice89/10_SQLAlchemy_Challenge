import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
base.classes.keys()

# Save references to each table
Measurement = base.classes.measurement
Station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)


# Flask Routes

@app.route("/")
def home_page():
    return(
        f"Climate APP<br/>"
        f"All Routes Available<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Start Session
    session = Session(engine)

    # Getting the latest date in the Measurement class
    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # Calculate the date 1 year ago from the last data point in the database
    query_date = dt.datetime.strptime(date , '%Y-%m-%d') - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_score = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).all()

    # End Session
    session.close()
    #Create a dictionary
    precip = {date: prcp for date, prcp in precipitation_score}
    return jsonify(precip)



@app.route("/api/v1.0/stations")
def stations():
    # Start Session
    session = Session(engine)

    #Return a JSON list of stations from the dataset
    station = session.query((Station.station)).all()

    # End Session
    session.close()

    # Convert list of tuples into normal list
    stations = list(np.ravel(station))

    return jsonify(stations=stations)



@app.route("/api/v1.0/tobs")
def temp():

    # Start Session
    session = Session(engine)

    # Getting the latest date in the Measurement class
    date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # Calculate the date 1 year ago from the last data point in the database
    query_date = dt.datetime.strptime(date , '%Y-%m-%d') - dt.timedelta(days=365)

    # Choose the station with the highest number of temperature observations.
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    data = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= query_date).all()

    # End Session
    session.close()

    # Convert list of tuples into normal list
    temp = list(np.ravel(data))

    return jsonify(temp=temp)


@app.route("/api/v1.0/temp/<start>/<end>")
def startend(start=None, end=None):

    # Start Session & set dates
    session = Session(engine)

    start = dt.date(2017, 6, 20)
    end = dt.date(2017, 8, 27)


    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # TMIN, TAVG, TMAX within the start and end date
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # End Session
    session.close()
    
    # Convert list of tuples into normal list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)



if __name__ == '__main__':
    app.run(debug=True)

