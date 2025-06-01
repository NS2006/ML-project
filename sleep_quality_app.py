from datetime import datetime
from flask import Flask, json, render_template, request, make_response
import pickle
import pandas as pd
from xhtml2pdf import pisa  #pip install reportlab xhtml2pdf
from io import BytesIO

app = Flask(__name__)

# Load the trained model
model = pickle.load(open("model.pkl", "rb"))

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/sleep-insights')
def sleep_insights():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form values
        gender = request.form['Gender']
        age = int(request.form['Age'])
        occupation = request.form['Occupation']
        bmi_category = request.form['BMI Category']

        sleep_duration = float(request.form['Sleep Duration'])
        sleep_disorder = request.form['Sleep Disorder']
        blood_pressure_systolic = request.form['Blood Pressure-systolic']
        blood_pressure_diastolic = request.form['Blood Pressure-diastolic']
        blood_pressure = blood_pressure_systolic + '/' + blood_pressure_diastolic

        physical_activity = int(request.form['Physical Activity Level'])
        stress_level = int(request.form['Stress Level'])
        heart_rate = int(request.form['Heart Rate'])
        daily_steps = int(request.form['Daily Steps'])


        features = [gender, age, occupation, sleep_duration,
                   physical_activity, stress_level, bmi_category,
                   blood_pressure, heart_rate, daily_steps, sleep_disorder]

        columns = [
            'Gender', 'Age', 'Occupation', 'Sleep Duration',
            'Physical Activity Level', 'Stress Level', 'BMI Category',
            'Blood Pressure', 'Heart Rate', 'Daily Steps', 'Sleep Disorder'
        ]

        # Create a list of tuples (column_name, value)
        feature_pairs = list(zip(columns, features))
        
        # Create a dictionary version for JSON serialization
        features_dict = dict(zip(columns, features))
        
        # Convert to DataFrame for prediction
        final_input = pd.DataFrame([features], columns=columns)
        prediction = model.predict(final_input)[0]

        recommendations = getRecommendations(feature_pairs, prediction)

        return render_template(
            'result.html', 
            prediction=prediction,
            features=feature_pairs,
            recommendations=recommendations,
            features_json=json.dumps(features_dict)
        )

    except Exception as e:
        return render_template('result.html', prediction=f"Error: {str(e)}")

@app.route('/download-report')
def download_report():
    try:
        prediction = request.args.get('prediction')
        features_json = request.args.get('features')
        
        if not features_json:
            return "No features data provided", 400
            
        features = json.loads(features_json)
        
        # Convert back to the pairs format if needed
        feature_pairs = list(features.items())

        recommendations = getRecommendations(feature_pairs, prediction)
        
        html = render_template(
            'report.html',
            prediction=prediction,
            features=feature_pairs,
            recommendations=recommendations,
            now=datetime.now()
        )
        
        pdf = BytesIO()
        pisa.CreatePDF(
            html,
            dest=pdf,
            encoding='UTF-8'
        )
        
        response = make_response(pdf.getvalue())
        response.headers['Content-Te'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=Slipipi_Sleep_Report.pdf'
        return response
        
    except Exception as e:
        return f"Error generating report: {str(e)}", 500

def getRecommendations(feature_pairs, prediction):
    rec_db = pd.read_csv('sleep_recommendations.csv') 
    
    recommendations = []
    
    # Get base recommendations (where feature and condition are empty)
    base_recs = rec_db[
        (rec_db['prediction_level'] == prediction) &
        (rec_db['feature'].isna()) &
        (rec_db['condition'].isna())
    ]
    recommendations.extend(base_recs['recommendation'].tolist())
    
    # Get feature-specific recommendations
    for col, val in feature_pairs:
        # Get rows for this feature that have conditions
        feature_rows = rec_db[
            (rec_db['feature'] == col) & 
            (rec_db['condition'].notna())
        ]
        
        # Evaluate each condition
        for _, row in feature_rows.iterrows():
            try:
                if eval(row['condition'], {'val': val}):
                    recommendations.append(row['recommendation'])
            except:
                continue
    
    # max 10
    return list(set(recommendations))[:10]

if __name__ == '__main__':
    app.run(debug=True)