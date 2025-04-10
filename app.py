import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify, url_for, redirect, flash

app = Flask(__name__)
app.secret_key = 'food_scarcity_prediction_key'

# Custom template filters
@app.template_filter('number_format')
def number_format(value):
    return '{:,}'.format(int(value))

# Define Indian states and union territories
indian_regions = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 
    'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 
    'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 
    'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 
    'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh', 
    'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Jammu and Kashmir', 
    'Ladakh', 'Lakshadweep', 'Puducherry'
]

# Define major crops grown in India
crops = [
    'Rice', 'Wheat', 'Maize', 'Jowar (Sorghum)', 'Bajra (Pearl Millet)', 'Ragi (Finger Millet)',
    'Pulses', 'Gram', 'Tur (Pigeon Pea)', 'Moong (Green Gram)', 'Urad (Black Gram)',
    'Groundnut', 'Rapeseed & Mustard', 'Soyabean', 'Sunflower', 'Safflower', 'Castor',
    'Cotton', 'Jute', 'Sugarcane', 'Potato', 'Onion', 'Tomato', 'Cauliflower', 'Cabbage',
    'Brinjal (Eggplant)', 'Okra', 'Peas', 'Mango', 'Banana', 'Citrus', 'Guava', 'Papaya',
    'Coconut', 'Cashew', 'Tea', 'Coffee'
]

# Define seasons
seasons = ['Kharif', 'Rabi', 'Zaid']

# Define years
years = list(range(2010, 2031))

# Define per capita consumption
per_capita_consumption = {
    'Rice': 80,  # kg per person per year
    'Wheat': 65,
    'Maize': 15,
    'Jowar (Sorghum)': 10,
    'Bajra (Pearl Millet)': 10,
    'Pulses': 18,
    'Potato': 25,
    'Onion': 15,
    'Tomato': 20,
    'Sugarcane': 30,  # processed as sugar
}

# Default consumption for other crops
default_consumption = 10  # kg per person per year

# Function to generate realistic population data
def generate_population(region, year):
    # Base population by region (approximate 2011 census data in millions)
    base_populations = {
        'Uttar Pradesh': 200, 'Maharashtra': 112, 'Bihar': 104, 'West Bengal': 91,
        'Madhya Pradesh': 72, 'Tamil Nadu': 72, 'Rajasthan': 68, 'Karnataka': 61,
        'Gujarat': 60, 'Andhra Pradesh': 49, 'Odisha': 42, 'Telangana': 35,
        'Kerala': 33, 'Jharkhand': 33, 'Assam': 31, 'Punjab': 28, 'Chhattisgarh': 25,
        'Haryana': 25, 'Delhi': 17, 'Jammu and Kashmir': 12, 'Uttarakhand': 10,
        'Himachal Pradesh': 7, 'Tripura': 4, 'Meghalaya': 3, 'Manipur': 3,
        'Nagaland': 2, 'Goa': 1.5, 'Arunachal Pradesh': 1.4, 'Puducherry': 1.2,
        'Mizoram': 1.1, 'Chandigarh': 1.0, 'Sikkim': 0.6, 'Andaman and Nicobar Islands': 0.4,
        'Ladakh': 0.3, 'Dadra and Nagar Haveli and Daman and Diu': 0.6, 'Lakshadweep': 0.1
    }
    
    # For regions not in the dictionary, assign a random value
    base_pop = base_populations.get(region, np.random.uniform(1, 10))
    
    # Add yearly growth (approximately 1-2% per year)
    growth_rate = np.random.uniform(0.01, 0.02)
    years_since_2011 = year - 2011
    population = base_pop * (1 + growth_rate) ** years_since_2011
    
    # Convert to actual population (millions to actual)
    return int(population * 1000000)

# Function to generate realistic crop production data
def generate_crop_production(region, crop, season, year, rainfall, temperature):
    # Base production capacity by crop (in thousand tonnes per 1000 hectares)
    base_production = {
        'Rice': np.random.uniform(2000, 4000),
        'Wheat': np.random.uniform(2500, 4500),
        'Maize': np.random.uniform(1500, 3000),
        'Jowar (Sorghum)': np.random.uniform(800, 1500),
        'Bajra (Pearl Millet)': np.random.uniform(800, 1500),
        'Ragi (Finger Millet)': np.random.uniform(600, 1200),
        'Pulses': np.random.uniform(500, 1000),
        'Gram': np.random.uniform(700, 1400),
        'Tur (Pigeon Pea)': np.random.uniform(600, 1200),
        'Moong (Green Gram)': np.random.uniform(400, 800),
        'Urad (Black Gram)': np.random.uniform(400, 800),
        'Groundnut': np.random.uniform(1000, 2000),
        'Rapeseed & Mustard': np.random.uniform(900, 1800),
        'Soyabean': np.random.uniform(1200, 2400),
        'Sunflower': np.random.uniform(500, 1000),
        'Safflower': np.random.uniform(400, 800),
        'Castor': np.random.uniform(600, 1200),
        'Cotton': np.random.uniform(300, 600),
        'Jute': np.random.uniform(1500, 3000),
        'Sugarcane': np.random.uniform(50000, 80000),
        'Potato': np.random.uniform(20000, 40000),
        'Onion': np.random.uniform(15000, 30000),
        'Tomato': np.random.uniform(20000, 40000),
        'Cauliflower': np.random.uniform(15000, 30000),
        'Cabbage': np.random.uniform(20000, 40000),
        'Brinjal (Eggplant)': np.random.uniform(15000, 30000),
        'Okra': np.random.uniform(10000, 20000),
        'Peas': np.random.uniform(8000, 16000),
        'Mango': np.random.uniform(8000, 16000),
        'Banana': np.random.uniform(30000, 60000),
        'Citrus': np.random.uniform(10000, 20000),
        'Guava': np.random.uniform(8000, 16000),
        'Papaya': np.random.uniform(40000, 80000),
        'Coconut': np.random.uniform(10000, 20000),
        'Cashew': np.random.uniform(500, 1000),
        'Tea': np.random.uniform(1500, 3000),
        'Coffee': np.random.uniform(800, 1600)
    }
    
    # Regional production factors (some regions are better for certain crops)
    regional_factors = {
        'Punjab': {'Wheat': 1.5, 'Rice': 1.4},
        'Haryana': {'Wheat': 1.4, 'Rice': 1.3},
        'Uttar Pradesh': {'Sugarcane': 1.5, 'Wheat': 1.3},
        'West Bengal': {'Rice': 1.4, 'Jute': 1.6},
        'Tamil Nadu': {'Rice': 1.3, 'Sugarcane': 1.4},
        'Karnataka': {'Coffee': 1.7, 'Ragi (Finger Millet)': 1.5},
        'Kerala': {'Coconut': 1.8, 'Rubber': 1.7, 'Spices': 1.6},
        'Andhra Pradesh': {'Rice': 1.4, 'Cotton': 1.3},
        'Maharashtra': {'Cotton': 1.4, 'Sugarcane': 1.3, 'Jowar (Sorghum)': 1.5},
        'Madhya Pradesh': {'Soyabean': 1.6, 'Wheat': 1.3},
        'Gujarat': {'Groundnut': 1.5, 'Cotton': 1.4},
        'Rajasthan': {'Bajra (Pearl Millet)': 1.5, 'Pulses': 1.3},
        'Assam': {'Tea': 1.8, 'Rice': 1.2},
        'Bihar': {'Maize': 1.4, 'Pulses': 1.3}
    }
    
    # Seasonal factors
    seasonal_factors = {
        'Rice': {'Kharif': 1.3, 'Rabi': 0.9, 'Zaid': 0.7},
        'Wheat': {'Kharif': 0.5, 'Rabi': 1.5, 'Zaid': 0.8},
        'Maize': {'Kharif': 1.2, 'Rabi': 1.0, 'Zaid': 0.9},
        'Cotton': {'Kharif': 1.4, 'Rabi': 0.6, 'Zaid': 0.4},
        'Sugarcane': {'Kharif': 1.1, 'Rabi': 1.1, 'Zaid': 1.0}
    }
    
    # Get base production for the crop
    production = base_production.get(crop, np.random.uniform(1000, 5000))
    
    # Apply regional factor if available
    if region in regional_factors and crop in regional_factors[region]:
        production *= regional_factors[region][crop]
    
    # Apply seasonal factor if available
    if crop in seasonal_factors and season in seasonal_factors[crop]:
        production *= seasonal_factors[crop][season]
    else:
        # Default seasonal variations
        if season == 'Kharif':
            production *= np.random.uniform(0.9, 1.3)
        elif season == 'Rabi':
            production *= np.random.uniform(0.8, 1.2)
        else:  # Zaid
            production *= np.random.uniform(0.7, 1.1)
    
    # Apply rainfall factor (optimal rainfall varies by crop)
    rainfall_factor = 1.0
    if rainfall < 500:  # Low rainfall
        rainfall_factor = np.random.uniform(0.6, 0.9)
    elif rainfall > 2000:  # High rainfall
        rainfall_factor = np.random.uniform(0.8, 1.1)
    else:  # Optimal rainfall
        rainfall_factor = np.random.uniform(0.9, 1.2)
    
    production *= rainfall_factor
    
    # Apply temperature factor
    temp_factor = 1.0
    if temperature < 15:  # Too cold for most crops
        temp_factor = np.random.uniform(0.5, 0.8)
    elif temperature > 35:  # Too hot for most crops
        temp_factor = np.random.uniform(0.6, 0.9)
    else:  # Optimal temperature
        temp_factor = np.random.uniform(0.9, 1.2)
    
    production *= temp_factor
    
    # Apply yearly trend (slight increase due to technology improvements)
    tech_improvement = 1 + (year - 2010) * 0.01
    production *= tech_improvement
    
    # Add some random variation
    production *= np.random.uniform(0.8, 1.2)
    
    return int(production)

# Function to calculate food scarcity/surplus
def calculate_food_balance(population, production, crop):
    # Get consumption rate for the crop
    consumption_rate = per_capita_consumption.get(crop, default_consumption)
    
    # Calculate total consumption need (in tonnes)
    total_consumption_need = (population * consumption_rate) / 1000
    
    # Calculate surplus/deficit (production is already in tonnes)
    balance = production - total_consumption_need
    
    # Calculate percentage surplus/deficit
    if total_consumption_need > 0:
        percentage = (balance / total_consumption_need) * 100
    else:
        percentage = 0
    
    return balance, percentage, total_consumption_need

# Routes
@app.route('/')
def home():
    # Create necessary directories if they don't exist
    for directory in ['static/css', 'static/js', 'static/images']:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    return render_template('prediction.html', 
                          regions=indian_regions, 
                          crops=crops, 
                          seasons=seasons, 
                          years=years)

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # Get form data
            region = request.form['region']
            crop = request.form['crop']
            season = request.form['season']
            year = int(request.form['year'])
            
            # Get population data
            if request.form.get('use_avg_population') == 'on':
                population = generate_population(region, year)
            else:
                population = float(request.form['population'])
            
            # Get rainfall data
            if request.form.get('use_avg_rainfall') == 'on':
                rainfall = np.random.uniform(500, 2500)  # Average rainfall
            else:
                rainfall = float(request.form['rainfall'])
            
            # Get temperature data
            if request.form.get('use_avg_temperature') == 'on':
                temperature = np.random.uniform(20, 30)  # Average temperature
            else:
                temperature = float(request.form['temperature'])
            
            # Get production data
            if request.form.get('use_avg_production') == 'on':
                production = generate_crop_production(region, crop, season, year, rainfall, temperature)
            else:
                production = float(request.form['production'])
            
            # Calculate food balance
            balance, percentage, consumption_need = calculate_food_balance(population, production, crop)
            
            # Determine scarcity level based on prediction
            if percentage <= -20:
                scarcity_level = "Severe Scarcity"
                color = "darkred"
            elif percentage <= -10:
                scarcity_level = "Moderate Scarcity"
                color = "red"
            elif percentage <= -5:
                scarcity_level = "Mild Scarcity"
                color = "orange"
            elif percentage <= 5:
                scarcity_level = "Balanced"
                color = "gray"
            elif percentage <= 15:
                scarcity_level = "Mild Surplus"
                color = "lightgreen"
            elif percentage <= 30:
                scarcity_level = "Moderate Surplus"
                color = "green"
            else:
                scarcity_level = "Large Surplus"
                color = "darkgreen"
            
            # Create a gauge-like visualization
            plt.figure(figsize=(10, 6))
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            plt.barh(0, percentage, color=color, height=0.5)
            
            # Add markers for scarcity levels
            for level, value in [("Severe Scarcity", -20), ("Moderate Scarcity", -10), 
                                ("Mild Scarcity", -5), ("Balanced", 0), 
                                ("Mild Surplus", 5), ("Moderate Surplus", 15), 
                                ("Large Surplus", 30)]:
                plt.axvline(x=value, color='gray', linestyle='--', alpha=0.5)
                plt.text(value, 0.7, level, rotation=90, ha='center', fontsize=8)
            
            # Set plot limits and labels
            plt.xlim(-30, 40)
            plt.ylim(-0.5, 1)
            plt.title(f'Food Scarcity Prediction for {crop} in {region} ({season} {year})', fontsize=14)
            plt.xlabel('Balance Percentage (%)', fontsize=12)
            plt.yticks([])
            
            # Add a text annotation for the prediction
            plt.text(percentage, 0, f"{percentage:.2f}%", 
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
            
            # Save plot to a base64 string
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            gauge_plot = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            # Prepare results
            results = {
                'region': region,
                'crop': crop,
                'season': season,
                'year': year,
                'population': int(population),
                'rainfall': rainfall,
                'temperature': temperature,
                'production': int(production),
                'consumption_need': int(consumption_need),
                'balance_tonnes': int(balance),
                'balance_percentage': percentage,
                'scarcity_level': scarcity_level,
                'color': color,
                'gauge_plot': gauge_plot,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return render_template('results.html', results=results)
            
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for('home'))
    
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
