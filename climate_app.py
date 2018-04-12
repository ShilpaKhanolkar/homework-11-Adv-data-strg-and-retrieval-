import datetime as datetime
import numpy as np 
import pandas as pd 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func 

from flask import Flask, jsonify 

########################################
#Database setup
########################################

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save a reference to the measurements table as `Measurement`
Measurement = Base.classes.measurements

# Save a reference to the stations table as `Station`
Station = Base.classes.stations

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    # List all available api routes
    return (
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query for the dates and precipitation observations 
    # from the last year.
    # Retrieving the data from 12 months before 8/23/2017 
    # (assuming current date is 8/23/2017) 
    prec_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016-08-23').all()

    # Dictionary using `date` as the key and `prcp` as the value
    prec_dict = {date: prcp for date, prcp in prec_data}  
    return jsonify(prec_dict)  

@app.route("/api/v1.0/stations")
def station():
    # Retrieve the names of all the active stations from Station
    # and count of observations
    active_stations = session.query(Measurement.station, \
        func.count(Measurement.tobs)).\
        group_by(Measurement.station).all()
    
    # Convert into normal list
    stations_list = list(np.ravel(active_stations))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Return a json list of Temperature Observations (tobs) 
    # for the previous year
    # Retrieving the data from 12 months before 8/23/2017 
    # (assuming current date is 8/23/2017)
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.station == "USC00519281").all()

    # Dictionary using `date` as the key and `prcp` as the value
    tobs_dict = {date: tobs for date, tobs in tobs_data}  
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start_date>")
@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps(start_date=None, end_date=None):
    if not end_date:
        results = session.query(func.min(Measurement.tobs), \
                    func.avg(Measurement.tobs), \
                    func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start_date).all()
        return jsonify(list(np.ravel(results)))
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
                     func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start_date).\
                    filter(Measurement.date <= end_date).all()
        return jsonify(list(np.ravel(results)))

#trip_temp_min, trip_temp_avg, trip_temp_max = calc_temps(str(input("Enter a Start Date (yyyy-mm-dd): ")), \
                                                         #str(input("Enter an End Date (yyyy-mm-dd): ")))[0]
#print(trip_temp_min, trip_temp_avg, trip_temp_max)
#print("Minimum Temperature: {}".format(trip_temp_min))
#print("Average Temperature: {}".format(trip_temp_avg))
#print("Maximum Temperature: {}".format(trip_temp_max))    

if __name__ == '__main__':
    app.run(debug=True)