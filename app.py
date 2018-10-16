import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

from sqlalchemy.pool import StaticPool

engine = create_engine("sqlite:///Resources/hawaii.sqlite",
                connect_args={'check_same_thread':False},
                poolclass=StaticPool)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

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
    return (
        f"Welcome to the weather page. <br />Available Routes are:<br/><br/>"
        f"/api/v1.0/precipitation:<br/>"
        f"/api/v1.0/stations:<br/>"
        f"/api/v1.0/tobs:<br/>"
        f"/api/v1.0/start_date:<br/>"
        f"/api/v1.0/start_date/end_date:<br/>"        
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    results = session.query(Measurement.date, func.avg(Measurement.prcp)).\
                filter(Measurement.date >= '2017-02-28').\
                filter(Measurement.date <= '2017-03-05').\
                group_by(Measurement.date).\
                all()

    prcp_data = []
    for row in results:
        prcp_dict = {}
        prcp_dict['Date'] = row.date
        prcp_dict['Precipitation'] = row[1]

        prcp_data.append(prcp_dict)

    # Convert list of tuples into normal list
    #prcp_data = list(np.ravel(results))

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station, Station.name).distinct().all()
    station_list = list(np.ravel(results))

    print("Stations List:")
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    
    results = session.query(Measurement.date, func.avg(Measurement.tobs)).\
                filter(Measurement.date >= '2017-02-28').\
                filter(Measurement.date <= '2017-03-05').\
                group_by(Measurement.date).\
                all()
    tobs_list = []
    for row in results:
        tobs_dict = {}
        tobs_dict['Date'] = row.date
        tobs_dict['Tobs'] = row[1]

        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start_date>")
def start(start_date):
    results = session.query(Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        group_by(Measurement.date).all()

    start_data = list(np.ravel(results))
    start_dict = {}
    # start_dict['Min'] = results[0]
    # start_dict['Avg'] = results[1]
    # start_dict['Max'] = results[2]

    
    return jsonify(start_data)
    

@app.route("/api/v1.0/<start_date>/<end_date>")
def end(start_date, end_date):
    results = session.query(Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).\
        group_by(Measurement.date).\
        all()

    start_data = list(np.ravel(results))

    return jsonify(start_data)


if __name__ == '__main__':
    app.run(debug=True)
