from flask import Flask, render_template, request, jsonify
import xgboost as xgb
import joblib
import numpy as np
from flask_cors import CORS  
import requests
import os
import psycopg2
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from police_api import PoliceAPI
from sklearn.preprocessing import StandardScaler
# import torch
# from model import Model  


# Load environment variables from .env file 
load_dotenv()
app = Flask(__name__)
CORS(app) 

# connects to postgreSQL database
def get_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", 5432)
        )
        return connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

    
#retrieves school performance statistics from database, responds in JSON
@app.route("/get_school_stats", methods=["GET"]) 
def get_school_stats():
    # Get the LSOA and school types from the request
    lsoa = request.args.get('lsoa')
    if not lsoa:
        return jsonify({"error": "No LSOA provided"})
    schoolTypes = request.args.getlist('schoolTypes[]') 
    if not schoolTypes:
        return jsonify({"error": "No school type provided"})
    conn = get_connection()
    cursor = conn.cursor()
    results={}
    # Loop through each school type and retrieve the statistics.
    for school in schoolTypes:
        #uses LSOA and LADNM table to get the correct school LAD name and region 
        cursor.execute("""SELECT s.* from {}_school s join "LADNM" la on s.region_local_authority = la.school_la join "LSOA" ls on la.ladnm = ls.ladnm WHERE ls.lsoa11cd = %s""".format(school), (lsoa,))
        schoolStatsLadnm = cursor.fetchone()
        cursor.execute("""SELECT s.* from {}_school s join "LADNM" la on s.region_local_authority = la."Region" join "LSOA" ls on la.ladnm = ls.ladnm WHERE ls.lsoa11cd = %s""".format(school), (lsoa,))
        schoolStatsRegion  = cursor.fetchone()
        results[school] = { 
                "ladnmSchoolStats": schoolStatsLadnm if schoolStatsLadnm else "No data found",
                "regionSchoolStats": schoolStatsRegion if schoolStatsRegion else "No data found"
            }
    cursor.close()
    conn.close() 
    if not results:
        return jsonify({"error": "No data found"})
    else:

        return jsonify(results)
    
# retrieves AI statistics form database, responds in JSON
@app.route("/get_AI_stats", methods=["GET"]) 
def get_AI_stats():
    lsoa = request.args.get('lsoa')
    transportType = request.args.get('transportType')
    timings = request.args.getlist('timings[]') 
    if not transportType:
        return jsonify({"error": "No transport type provided"})
    if not timings:
        return jsonify({"error": "No timings provided"})
    
    amenities=['gp_practices','hospitals','primary_schools','secondary_schools','supermarkets']
    columns = ['nearest_parks','nearest_main_bua']
    lsoaColumns=columns.copy()
    for amenity in amenities:
        for timing in timings:
            lsoaColumns.append(f'{amenity}_{timing}')
    lsoaColumns_s = ", ".join(lsoaColumns)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""SELECT {lsoaColumns_s} from {transportType}_ai WHERE lsoa = %s""", (lsoa,))
    AIstatsLsoa = cursor.fetchone()

    cursor.execute("""SELECT ladnm from "LSOA" where lsoa11cd = %s""", (lsoa,))
    ladnm = cursor.fetchone()[0]
    ladnmColumns=[]
    for amenity in amenities:
        for timing in timings:
            ladnmColumns.append(f'AVG({amenity}_{timing}) as {amenity}_{timing}_avg')
    ladnmColumns_s = ", ".join(ladnmColumns) 
    cursor.execute(f"""SELECT {ladnmColumns_s} FROM {transportType}_ai ai JOIN "LSOA" ls ON ai.lsoa = ls.lsoa11cd WHERE ls.ladnm = %s GROUP BY ls.ladnm""", (ladnm,))
    AIstatsLadnm = cursor.fetchone()
    cursor.close()
    conn.close() 
    if not AIstatsLsoa:
        return jsonify({"error": "No data found"})
    else:
        AIstatsLsoaResult = {}
        AIstatsLsoaResult['nearest_parks'] = AIstatsLsoa[0] 
        AIstatsLsoaResult['nearest_main_bua'] = AIstatsLsoa[1]
        for i, column in enumerate(lsoaColumns[2:]):

            amenity, timing = column.rsplit('_', 1)
            if amenity not in AIstatsLsoaResult:
                AIstatsLsoaResult[amenity] = {}
            AIstatsLsoaResult[amenity][timing] = AIstatsLsoa[i + 2]
       
        AIstatsLadnmResult = {}
        for i, column in enumerate(ladnmColumns):
            columnName= column.split(" as ")[-1]
            amenity, timing = columnName.rsplit('_', 1)
            
    
            if amenity not in AIstatsLadnmResult:
                AIstatsLadnmResult[amenity] = {}

         
            AIstatsLadnmResult[amenity][timing] = AIstatsLadnm[i]

        return jsonify({"lsoaAIStats":AIstatsLsoaResult,"ladnmAIStats":AIstatsLadnmResult})

# retrieves locational data from postcodes.io, responds in JSON
@app.route("/get_location", methods=["GET"])
def get_location():
    postcode = request.args.get("postcode")
    if not postcode:
        return jsonify({"error": "No postcode provided"}), 404
    response = requests.get(f"https://api.postcodes.io/postcodes/{postcode}")
    if response.status_code == 200:
        data = response.json()
        location = {
            "postcode": data["result"]["postcode"],
            "latitude": data["result"]["latitude"],
            "longitude": data["result"]["longitude"],
            "lsoa": data["result"]["codes"]["lsoa"],
            "lsoa_name": data["result"]["lsoa"],
            "parliamentary_constituency": data['result']['parliamentary_constituency'],
            "ladnm": data["result"]["admin_district"]
        }
        return jsonify(location)
    else:
        return {"error": f"Error fetching data: {response.status_code}"},404
    
# retrieves crime type and outcome statistics from data.police.uk, responds in JSON
@app.route('/get_crime_stats', methods=['GET'])
def get_crime_stats():
    latitude = float(request.args.get('latitude'))
    longitude = float(request.args.get('longitude'))

    api = PoliceAPI()
    latestMonth = api.get_latest_date()
    latestMonth = datetime.strptime(latestMonth, "%Y-%m")
    sixMonthsCrime = []
    attributes = ["category", "outcome_status"]

    for i in range(6):
        month = (latestMonth - relativedelta(months=i)).strftime("%Y-%m")
        url = f"https://data.police.uk/api/crimes-street/all-crime?date={month}&lat={latitude}&lng={longitude}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] Fetching crime data failed: {e}")
            continue
        
        crimes = response.json()
        for crime in crimes:
            filtered_crime = {key: crime[key] for key in attributes if key in crime}
            sixMonthsCrime.append(filtered_crime)

    if not sixMonthsCrime:
        return jsonify({"error": "No crime data found or API failed"}), 404

    df = pd.DataFrame(sixMonthsCrime)
    
    # Map categories to condense into fewer categories
    categoryMappings = {
        'other-theft': 'theft',
        'bicycle-theft': 'theft',
        'theft-from-the-person': 'theft',
        'public-order': 'anti social behaviour',
        'possession-of-weapons': 'possession of drugs/weapons',
        'drugs': 'possession of drugs/weapons',
        'shoplifting': 'other crime',
        'robbery': 'robbery/burglary',
        'burglary': 'robbery/burglary'
    }
    df['category_mapped'] = df['category'].replace(categoryMappings)
    df['category_mapped'] = df['category_mapped'].str.replace('-', ' ').str.strip()
    categoryCounts = df['category_mapped'].value_counts().reset_index()
    categoryCounts.columns = ['category', 'count']

    # Outcomes mapping
    df["outcome_category"] = df["outcome_status"].apply(lambda x: x["category"] if isinstance(x, dict) else "Unknown")
    outcomeMappings = {
        'Offender given a drugs possession warning': 'Offender given a caution',
        'Offender given absolute discharge': 'Offender given a discharge',
        'Offender given partial discharge': 'Offender given a discharge',
        'Status update unavailable': 'Unknown',
        'Offender fined': 'Fines/Compensation/Property deprivation',
        'Offender ordered to pay compensation': 'Financial Penalty',
        'Offender given penalty notice': 'Financial Penalty',
        'Offender deprived of property': 'Financial Penalty',
        'Awaiting court outcome': 'Court outcomes',
        'Defendant sent to Crown Court': 'Court outcomes',
        'Court result unavailable': 'Court outcomes',
        'Further action is not in the public interest': 'Case dropped',
        'Further investigation is not in the public interest': 'Case dropped',
        'Formal action is not in the public interest': 'Case dropped',
        'Court case unable to proceed': 'Case dropped',
        'Unable to prosecute suspect': 'Case dropped',
        'Suspect charged': 'Charged and Sentenced',
        'Suspect charged as part of another case': 'Charged and Sentenced',
        'Offender given community sentence': 'Charged and Sentenced',
        'Offender sent to prison': 'Charged and Sentenced',
        'Offender given suspended prison sentence': 'Charged and Sentenced',
        'Offender otherwise dealt with': 'Charged and Sentenced',
        'Action to be taken by another organisation': 'Under investigation',
        'Investigation complete; no suspect identified': 'No suspect identified'
    }
    df['outcomes_mapped'] = df['outcome_category'].replace(outcomeMappings)

    outcomeCounts = df['outcomes_mapped'].value_counts().reset_index()
    outcomeCounts.columns = ['outcome', 'count']

    # Calculate resolution rate
    unResolved = ['No suspect identified', 'Case dropped']
    resolved_count = df.shape[0] - df[df['outcomes_mapped'].isin(unResolved)].shape[0]
    resolved_percentage = resolved_count / df.shape[0]

    return jsonify({
        "categoryCounts": categoryCounts.to_dict(orient="records"),
        "outcomeCounts": outcomeCounts.to_dict(orient="records"),
        "resolvedPercentage": resolved_percentage
    })



# takes user selections, make a table of features,loads scaler, model, applies data transformations, makes predictions and returns in JSON format
@app.route('/get_price_prediction', methods=['GET'])
def get_prediction():
    postcode,latitude, longitude, lsoa  = request.args.get('postcode'),float(request.args.get('latitude')), float(request.args.get('longitude')), request.args.get('lsoa')
    postcode = postcode.replace(" ", "")
    lat_long = latitude * longitude
    num_bedrooms, num_bathrooms_Log, num_receptions_Log = int(request.args.get('propertySelections[bedrooms]')), np.log1p(int(request.args.get('propertySelections[bathrooms]'))), np.log1p(int(request.args.get('propertySelections[receptions]')))
    AIs =['gp_practices_30','hospitals_30','primary_schools_30','secondary_schools_30','supermarkets_30','nearest_parks','nearest_main_bua']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""SELECT {','.join(AIs)} FROM pt_ai WHERE lsoa = %s""", (lsoa,))
    amenities_data = cursor.fetchone()
    gps_Log, hospitals_Log,primary_schools_Log , secondary_schools_Log, supermarkets_Log, parks_Log, main_bua= np.log1p(amenities_data[0]), np.log1p(amenities_data[1]), np.log1p(amenities_data[2]), np.log1p(amenities_data[3]), np.log1p(amenities_data[4]), np.log1p(amenities_data[5]), (amenities_data[6])
    cursor.execute(f"""SELECT smoothed_pcu, smoothed_lad22cd FROM smoothedmappings WHERE postcode = %s""", (postcode,))

    smoothed_data = cursor.fetchone()
    if None in smoothed_data:
        return jsonify({"error": "Error: insufficient data for postcode"}), 400
    else:
        smoothed_pcuLog, smoothed_lad22cdLog = np.log1p(smoothed_data[0]), np.log1p(smoothed_data[1])

    columns = {'num_bedrooms': num_bedrooms, 'latitude':latitude, 'longitude':longitude, 'property_type_Bungalow':0, 
           'property_type_Detached bungalow':0, 'property_type_Detached house':0, 
           'property_type_Flat':0, 'property_type_Maisonette':0, 'property_type_Terraced house':0, 
           'Off street parking':0, 'Driveway':0, 'Conservatory':0, 'Garage':0,'Swimming pool':0,'nearest_main_bua':main_bua,
           'end_date_numeric':0, 'num_bathroomsLog':num_bathrooms_Log, 'num_receptsLog': num_receptions_Log,  
           'gp_practices_30Log': gps_Log, 'hospitals_30Log': hospitals_Log, 'primary_schools_30Log': primary_schools_Log, 
           'secondary_schools_30Log':secondary_schools_Log, 'supermarkets_30Log':supermarkets_Log, 'nearest_parksLog':parks_Log, 
           'smoothed_lad22cdLog':smoothed_lad22cdLog,'smoothed_pcuLog': smoothed_pcuLog, 'lat_long': lat_long,'year':0,'month':0,'year_month':0}
    
    amenities = ['Off street parking', 'Driveway', 'Conservatory', 'Garage', 'Swimming pool']
    amenities_selected = [ value for key, value in request.args.items()
    if key.startswith('propertySelections[amenities]')]
    for amenity in amenities:
        if amenity in amenities_selected:
            columns[amenity] = 1
    type_selected = request.args.get('propertySelections[type]')
    property_column = f'property_type_{type_selected}'
    columns[property_column] = 1

    pd.set_option('display.max_columns', None)

    X=[]
    dateSelected = pd.to_datetime(request.args.get('date'))
    dates = []
    for i in range(-3,4,1):  
        date = dateSelected + pd.DateOffset(months=i)
        dates.append(date)
        year = date.year
        month_sin = np.sin(2 * np.pi * date.month / 12)
        month_cos = np.cos(2 * np.pi * date.month / 12)
        month_sin_cos = month_sin * month_cos
        date_timestamp = int(date.timestamp())*1000
        X_row = columns.copy()  
        X_row['end_date_numeric'] = date_timestamp
        X_row['year']=year
        X_row['month']=month_sin_cos
        X_row['year_month'] = X_row['year'] * X_row['month']

        X.append(X_row)


    X = pd.DataFrame(X)
    # model, scaler are loaded
    model = xgb.XGBRegressor()
    model.load_model('xgboost3-4_model.json')
    scaler, columns_to_standardise = joblib.load('SC4.pkl')
    X[columns_to_standardise] = scaler.transform(X[columns_to_standardise])
    y_pred = np.expm1(model.predict(X)) 

    results = [
    {"date": date, "predicted_price": float(prediction)}
    for date, prediction in zip(dates, y_pred)
]
    results_df = pd.DataFrame(results)
    print(results_df)
    return jsonify({"predictions": results})

    

if __name__ == "__main__":
    app.run(debug=True)
