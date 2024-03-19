# Import the dependencies.

import datetime as dt
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last 12 months."""
    one_year = dt.date.today() - dt.timedelta(days=365)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date >= one_year).all()
    
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    stations = session.query(Station.station).all()
    station_list = list(np.ravel(stations))

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations for the most active station for the last 12 months."""
    one_year = dt.date.today() - dt.timedelta(days=365)
    
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
                        filter(Measurement.date >= one_year).\
                        filter(Measurement.station == most_active_station_id).all()
    
    temperature_list = [{"Date": date, "Temperature": tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)


@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return TMIN, TAVG, and TMAX for all dates greater than or equal to the start date."""
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).all()
    
    temperature_stats_list = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in temperature_stats]

    return jsonify(temperature_stats_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return TMIN, TAVG, and TMAX for dates between the start and end dates (inclusive)."""
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        filter(Measurement.date <= end).all()
    
    temperature_stats_list = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in temperature_stats]

    return jsonify(temperature_stats_list)

if __name__ == "__main__":
    app.run(debug=True)