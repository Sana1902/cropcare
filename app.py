from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import tensorflow as tf
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import requests
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['DETECTED_DISEASE_FOLDER'] = 'detected_diseases/'  # Folder to store detected disease names

# Load the pre-trained model (TensorFlow model)
model_path = 'Disease_img/saved_model_directory'  # Path to your SavedModel folder
loaded_model = tf.saved_model.load(model_path)

# Print the model's signature to identify output layer keys
predict_function = loaded_model.signatures['serving_default']
print("Model output structure:", predict_function.structured_outputs)

# Define the class names list globally
class_names = ['Brown_spot', 'Healthy', 'RedRot', 'RedRust', 'Yellow_Leaf']

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Custom function for prediction
def make_prediction(model_function, img):
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Add batch dimension
    predictions = model_function(tf.constant(img_array))  # Get model predictions
    
    output_key = list(predictions.keys())[0]  # Extract the first output key
    predicted_probs = predictions[output_key][0].numpy()  # Get the prediction probabilities for the first image
    
    # Get predicted class (the class with the highest probability)
    predicted_class = class_names[np.argmax(predicted_probs)]
    
    # Get confidence (maximum probability)
    confidence = 100 * np.max(predicted_probs)
    
    return predicted_class, confidence


# Function to save the detected disease in a text file
def save_detected_disease(disease_name, folder_path=app.config['DETECTED_DISEASE_FOLDER']):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    disease_file_path = os.path.join(folder_path, f"{disease_name}.txt")
    
    with open(disease_file_path, 'w') as file:
        file.write(disease_name)

    print(f"Disease '{disease_name}' has been saved at {disease_file_path}.")

# Function to fetch the most recent detected disease from the folder
def fetch_disease_from_folder(folder_path=app.config['DETECTED_DISEASE_FOLDER']):
    disease_files = os.listdir(folder_path)
    
    if not disease_files:
        print("No diseases detected.")
        return None
    
    latest_disease_file = max(disease_files, key=lambda x: os.path.getctime(os.path.join(folder_path, x)))
    print(f"Fetching the most recent disease file: {latest_disease_file}")
    
    with open(os.path.join(folder_path, latest_disease_file), 'r') as file:
        disease_name = file.read().strip()
    
    print(f"Detected disease from file: '{disease_name}'")
    return disease_name

# Function to provide recommendations based on the detected disease
def get_recommendations(disease_name):
    recommendations = {
        "Brown_spot": "Use fungicides like chlorothalonil or copper-based sprays.",
        "Healthy": "No treatment needed, continue regular care.",
        "RedRot": "Apply fungicides, and improve air circulation around plants.",
        "RedRust": "Use rust-resistant crop varieties, and apply suitable fungicides.",
        "Yellow_Leaf": "Check for nutrient deficiencies, especially nitrogen, and apply the appropriate fertilizer."
    }
    
    print(f"Looking up recommendations for: {disease_name}")
    
    recommendation = recommendations.get(disease_name, "No recommendations available for this disease.")
    
    return recommendation



def get_disease_details(disease_name):
    disease_details = {
        "Brown_spot": {
            "Symptoms": "At this phase, farmers may notice small, reddish-brown spots that appear on the undersides of sugarcane leaves. These spots are powdery and often feel rough to the touch. Over time, the affected leaves start turning yellow. Gradually, the leaves become dry and may start curling up from the edges, which hampers the photosynthesis process and weakens the plant.",
            "Precautions": "Avoid waterlogging and ensure proper field sanitation.",
            "Crop Management": "Apply preventive fungicides like Mancozeb at 2.5 g/L of water.",
            "Fertilizer Usage": "To keep the plants healthy and resistant to Brown Spot, apply a balanced NPK fertilizer mix. Use 40 kg of nitrogen, 20 kg of phosphorus, and 20 kg of potassium per hectare. The nitrogen boosts leaf growth, phosphorus helps in root and stem development, and potassium strengthens the plant’s defenses against diseases. Additionally, incorporating Azotobacter biofertilizer at a rate of 1 kg per acre enhances nitrogen fixation in the soil, which can naturally improve plant health and vigor."
        },
        "Healthy": {
            "Symptoms": "No visible symptoms. The crop is healthy and thriving.",
            "Precautions": "No treatment needed, continue regular care.",
            "Crop Management": "Maintain proper field hygiene and ensure timely irrigation and fertilization.",
            "Fertilizer Usage": "Apply a balanced NPK fertilizer to maintain healthy growth."
        },
        "RedRot": {
            "Symptoms": "Yellowing and wilting of leaves, rotting of the stalks at the base, and an overall decline in plant health.",
            "Precautions": "Ensure proper drainage, avoid over-watering, and remove infected plants.",
            "Crop Management": "Apply fungicides like Propiconazole and ensure proper air circulation around the plants.",
            "Fertilizer Usage": "Use a balanced fertilizer mix to enhance plant health and resistance. Apply compost to improve soil structure and moisture retention."
        },
        "RedRust": {
            "Symptoms": "Rust-colored pustules appear on the undersides of leaves, causing them to curl and eventually die.",
            "Precautions": "Use rust-resistant varieties, avoid over-crowding, and remove infected leaves.",
            "Crop Management": "Apply fungicides like Trifloxystrobin to prevent further spread.",
            "Fertilizer Usage": "Apply adequate nitrogen and potassium fertilizers to enhance resistance to rust."
        },
        "Yellow_Leaf": {
            "Symptoms": "Yellowing of the lower leaves, often a sign of nutrient deficiency or water stress.",
            "Precautions": "Check for nutrient deficiencies, especially nitrogen, and ensure proper irrigation.",
            "Crop Management": "Apply fertilizers rich in nitrogen and make sure the soil drains well.",
            "Fertilizer Usage": "Apply a nitrogen-rich fertilizer mix and ensure proper soil pH to correct deficiencies."
        }
    }

    print(f"Looking up details for: {disease_name}")
    
    details = disease_details.get(disease_name, {
        "Symptoms": "No symptoms found.",
        "Precautions": "No precautions available.",
        "Crop Management": "No crop management guidelines available.",
        "Fertilizer Usage": "No fertilizer recommendations available."
    })
    
    return details


# Function to fetch weather data using OpenWeatherMap API
def get_weather_data(city_name='Kolhapur'):
    api_key = 'e748a77ec17ab4d4ec436b27811af8d0'  # Replace with your OpenWeatherMap API key
    base_url = "https://api.openweathermap.org/data/2.5/weather?"

    complete_url = f"{base_url}q={city_name}&appid={api_key}&units=metric"  # 'units=metric' for temperature in Celsius

    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        
        if response.status_code == 200:
            data = response.json()
            main = data['main']
            weather = data['weather'][0]

            avg_temp = main['temp']
            avg_humidity = main['humidity']
            avg_pressure = main['pressure']
            avg_wind_speed = data['wind']['speed']
            total_rain = data.get('rain', {}).get('1h', 0)

            return avg_temp, avg_humidity, avg_pressure, avg_wind_speed, total_rain
        else:
            print("Weather data could not be fetched. Response code:", response.status_code)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching weather data: {e}")
        return None

# Function to classify disease phase based on weather data
def classify_phase(avg_temp, avg_humidity, avg_pressure, avg_wind_speed, total_rain, disease):
    if disease == 'Brown_spot':
        if (avg_temp < 22 and avg_humidity > 85 and total_rain > 5):
            return "Incubation"
        elif (22 <= avg_temp <= 30 and 60 < avg_humidity <= 85 and total_rain > 5 and avg_pressure > 1005):
            return "Development"
        elif (avg_temp > 30 and avg_humidity < 60 and avg_wind_speed > 10):
            return "Developed"
        else:
            return "Stable Phase"

    elif disease == 'RedRot':
        if (avg_temp < 20 and avg_humidity > 80 and total_rain > 10):
            return "Incubation"
        elif (20 <= avg_temp <= 28 and 70 < avg_humidity <= 90 and total_rain > 5 and avg_pressure > 1010):
            return "Development"
        elif (avg_temp > 28 and avg_humidity < 70 and avg_wind_speed > 12):
            return "Developed"
        else:
            return "Stable Phase"

    elif disease == 'RedRust':
        if (avg_temp < 18 and avg_humidity > 75 and total_rain > 3):
            return "Incubation"
        elif (18 <= avg_temp <= 25 and 65 < avg_humidity <= 80 and total_rain > 2 and avg_pressure > 1008):
            return "Development"
        elif (avg_temp > 25 and avg_humidity < 65 and avg_wind_speed > 8):
            return "Developed"
        else:
            return "Stable Phase"

    elif disease == 'Yellow_Leaf':
        if (avg_temp < 24 and avg_humidity > 80 and total_rain > 2):
            return "Incubation"
        elif (24 <= avg_temp <= 32 and 60 < avg_humidity <= 85 and total_rain > 1 and avg_pressure > 1006):
            return "Development"
        elif (avg_temp > 32 and avg_humidity < 60 and avg_wind_speed > 15):
            return "Developed"
        else:
            return "Stable Phase"

    else:
        return "Healthy Phase"

# Home page route
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_schemes')
def check_schemes():
    return render_template('check_schemes.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Prediction route
@app.route('/predict', methods=['POST'])
def predict_route():
    if 'crop-image' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['crop-image']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        image = Image.open(file_path).convert('RGB')
        image = image.resize((224, 224))

        predicted_class, confidence = make_prediction(predict_function, image)

        session['prediction'] = f"{predicted_class} ({confidence:.2f}% confidence)"
        
        save_detected_disease(predicted_class)

        return redirect(url_for('result'))

    flash('Invalid file type. Please upload a PNG, JPG, or JPEG image.')
    return redirect(url_for('index'))


@app.route('/result')
def result():
    prediction = session.get('prediction', None)
    
    if prediction is None:
        flash('No prediction made yet.')
        return redirect(url_for('index'))
    
    fetched_disease = fetch_disease_from_folder()
    
    if fetched_disease:
        recommendations = get_recommendations(fetched_disease)
        disease_details = get_disease_details(fetched_disease)
        print(f"Recommendations for '{fetched_disease}': {recommendations}")
        print(f"Detailed information for '{fetched_disease}': {disease_details}")
        
        weather_data = get_weather_data(city_name='Kolhapur')
        
        if weather_data:
            avg_temp, avg_humidity, avg_pressure, avg_wind_speed, total_rain = weather_data
            disease_phase = classify_phase(avg_temp, avg_humidity, avg_pressure, avg_wind_speed, total_rain, fetched_disease)
        else:
            disease_phase = "Weather data unavailable"
    else:
        recommendations = "No disease detected."
        disease_details = {
            "Symptoms": "No disease detected.",
            "Precautions": "No disease detected.",
            "Crop Management": "No disease detected.",
            "Fertilizer Usage": "No disease detected."
        }
        disease_phase = "No disease detected"
    
    return render_template('result.html', 
                           prediction=prediction, 
                           recommendations=recommendations, 
                           disease_details=disease_details, 
                           weather=weather_data, 
                           disease_phase=disease_phase)

if __name__ == '__main__':
    app.run(debug=True)
