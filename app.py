import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, flash

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


# Define years
years = list(range(2010, 2031))

# Define per capita consumption based on actual Indian consumption patterns
per_capita_consumption = {
    'Rice': 72,  # kg per person per year (actual Indian average)
    'Wheat': 55,  # Northern India consumes more wheat
    'Maize': 8,
    'Jowar (Sorghum)': 5,
    'Bajra (Pearl Millet)': 5,
    'Ragi (Finger Millet)': 3,
    'Pulses': 14,  # Important protein source in Indian diet
    'Gram': 5,
    'Tur (Pigeon Pea)': 3,
    'Moong (Green Gram)': 2,
    'Urad (Black Gram)': 2,
    'Groundnut': 4,
    'Rapeseed & Mustard': 3,
    'Soyabean': 2,
    'Potato': 20,
    'Onion': 12,
    'Tomato': 15,
    'Sugarcane': 20,  # processed as sugar
    'Cotton': 0,  # Non-food crop
    'Jute': 0,  # Non-food crop
    'Tea': 0.8,
    'Coffee': 0.2
}

# Default consumption for other crops
default_consumption = 5  # kg per person per year

# Function to generate realistic population data
def generate_population(region, year):
    # Base population by region (2011 census data in millions, updated with 2021 estimates)
    base_populations = {
        # Most populous states
        'Uttar Pradesh': 199.8,  # Most populous state
        'Maharashtra': 112.4,
        'Bihar': 104.1,
        'West Bengal': 91.3,
        'Madhya Pradesh': 72.6,
        'Tamil Nadu': 72.1,
        'Rajasthan': 68.5,
        'Karnataka': 61.1,
        'Gujarat': 60.4,
        'Andhra Pradesh': 49.6,  # Post-division

        # Medium population states
        'Odisha': 41.9,
        'Telangana': 35.2,  # Created in 2014
        'Kerala': 33.4,
        'Jharkhand': 33.0,
        'Assam': 31.2,
        'Punjab': 27.7,
        'Chhattisgarh': 25.5,
        'Haryana': 25.4,

        # Union Territories and smaller states
        'Delhi': 16.8,  # National Capital Territory
        'Jammu and Kashmir': 12.5,  # Pre-division
        'Uttarakhand': 10.1,
        'Himachal Pradesh': 6.9,
        'Tripura': 3.7,
        'Meghalaya': 3.0,
        'Manipur': 2.9,
        'Nagaland': 2.0,
        'Goa': 1.5,
        'Arunachal Pradesh': 1.4,
        'Puducherry': 1.2,
        'Mizoram': 1.1,
        'Chandigarh': 1.1,
        'Sikkim': 0.6,
        'Andaman and Nicobar Islands': 0.4,
        'Ladakh': 0.3,  # Created in 2019
        'Dadra and Nagar Haveli and Daman and Diu': 0.6,
        'Lakshadweep': 0.1
    }

    # For regions not in the dictionary, assign a small population
    base_pop = base_populations.get(region, np.random.uniform(0.5, 5))

    # Add yearly growth based on actual Indian population growth rates
    # India's growth rate has been declining: ~1.8% in 2000s to ~1% in 2020s
    if year <= 2015:
        growth_rate = np.random.uniform(0.015, 0.018)  # 1.5-1.8% for earlier years
    else:
        growth_rate = np.random.uniform(0.010, 0.015)  # 1.0-1.5% for recent years

    years_since_2011 = year - 2011
    population = base_pop * (1 + growth_rate) ** years_since_2011

    # Convert to actual population (millions to actual)
    return int(population * 1000000)

# Function to generate realistic crop production data
def generate_crop_production(region, crop, year, rainfall, temperature):
    # Base production capacity by crop (in tonnes for the region)
    # Based on actual Indian agricultural production data
    base_production = {
        # Major food grains
        'Rice': 110000000,  # India produces ~110 million tonnes of rice annually
        'Wheat': 100000000,  # ~100 million tonnes of wheat
        'Maize': 28000000,
        'Jowar (Sorghum)': 4500000,
        'Bajra (Pearl Millet)': 9000000,
        'Ragi (Finger Millet)': 2000000,

        # Pulses
        'Pulses': 23000000,  # Total pulses production
        'Gram': 11000000,
        'Tur (Pigeon Pea)': 4000000,
        'Moong (Green Gram)': 2000000,
        'Urad (Black Gram)': 2500000,

        # Oilseeds
        'Groundnut': 9000000,
        'Rapeseed & Mustard': 9500000,
        'Soyabean': 12000000,
        'Sunflower': 250000,
        'Safflower': 100000,
        'Castor': 1800000,

        # Commercial crops
        'Cotton': 6000000,  # Cotton lint
        'Jute': 2000000,
        'Sugarcane': 350000000,

        # Vegetables
        'Potato': 50000000,
        'Onion': 22000000,
        'Tomato': 20000000,
        'Cauliflower': 8500000,
        'Cabbage': 9000000,
        'Brinjal (Eggplant)': 12500000,
        'Okra': 6000000,
        'Peas': 5500000,

        # Fruits
        'Mango': 20000000,
        'Banana': 30000000,
        'Citrus': 12000000,
        'Guava': 4000000,
        'Papaya': 6000000,
        'Coconut': 15000000,

        # Others
        'Cashew': 700000,
        'Tea': 1300000,
        'Coffee': 350000
    }

    # Regional production factors based on actual agricultural patterns in India
    # These factors represent each state's share of national production
    regional_factors = {
        # Northern India - Major wheat and rice producers
        'Punjab': {'Wheat': 0.17, 'Rice': 0.11, 'Maize': 0.02, 'Sugarcane': 0.02, 'Cotton': 0.05},
        'Haryana': {'Wheat': 0.12, 'Rice': 0.04, 'Sugarcane': 0.02, 'Cotton': 0.07},
        'Uttar Pradesh': {'Wheat': 0.30, 'Rice': 0.12, 'Sugarcane': 0.38, 'Potato': 0.30, 'Pulses': 0.16},

        # Eastern India - Rice bowl
        'West Bengal': {'Rice': 0.15, 'Jute': 0.75, 'Potato': 0.25, 'Tea': 0.20},
        'Bihar': {'Rice': 0.05, 'Maize': 0.07, 'Pulses': 0.08, 'Wheat': 0.05},
        'Odisha': {'Rice': 0.07, 'Pulses': 0.03},
        'Assam': {'Rice': 0.05, 'Tea': 0.50, 'Banana': 0.03},

        # Southern India
        'Tamil Nadu': {'Rice': 0.07, 'Sugarcane': 0.09, 'Banana': 0.25, 'Coconut': 0.20},
        'Karnataka': {'Rice': 0.04, 'Ragi (Finger Millet)': 0.60, 'Coffee': 0.70, 'Sugarcane': 0.06, 'Silk': 0.65},
        'Kerala': {'Coconut': 0.45, 'Banana': 0.10, 'Rubber': 0.85, 'Spices': 0.40, 'Coffee': 0.20},
        'Andhra Pradesh': {'Rice': 0.12, 'Cotton': 0.10, 'Groundnut': 0.25, 'Chillies': 0.40, 'Tobacco': 0.45},
        'Telangana': {'Rice': 0.05, 'Cotton': 0.18, 'Maize': 0.12},

        # Western India
        'Maharashtra': {'Cotton': 0.25, 'Sugarcane': 0.23, 'Jowar (Sorghum)': 0.50, 'Onion': 0.30, 'Grapes': 0.80},
        'Gujarat': {'Groundnut': 0.40, 'Cotton': 0.30, 'Castor': 0.75, 'Tobacco': 0.45},
        'Rajasthan': {'Bajra (Pearl Millet)': 0.45, 'Pulses': 0.15, 'Wheat': 0.10, 'Mustard': 0.45},

        # Central India
        'Madhya Pradesh': {'Soyabean': 0.60, 'Wheat': 0.16, 'Pulses': 0.24, 'Cotton': 0.08, 'Gram': 0.30},
        'Chhattisgarh': {'Rice': 0.06, 'Pulses': 0.05}
    }

    # Get base production for the crop (national total)
    production = base_production.get(crop, np.random.uniform(1000000, 5000000))

    # Apply regional factor if available (convert from national share to regional production)
    if region in regional_factors and crop in regional_factors[region]:
        # The regional factor represents the state's share of national production
        production *= regional_factors[region][crop]
    else:
        # If no specific data for this region-crop combination, assign a small random share
        # Most states produce 1-5% of national production for crops not specifically listed
        production *= np.random.uniform(0.01, 0.05)

    # Apply random variation factor
    production *= np.random.uniform(0.8, 1.2)

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

    # Print debug information
    print(f"DEBUG: Population = {population}, Crop = {crop}")
    print(f"DEBUG: Consumption Rate = {consumption_rate} kg/person/year")
    print(f"DEBUG: Total Consumption Need = {total_consumption_need} tonnes")
    print(f"DEBUG: Production = {production} tonnes")
    print(f"DEBUG: Balance = {balance} tonnes")
    print(f"DEBUG: Percentage = {percentage}%")

    return balance, percentage, total_consumption_need

# Routes
@app.route('/')
def home():
    # Create necessary directories if they don't exist
    for directory in ['static/css', 'static/js', 'static/images']:
        if not os.path.exists(directory):
            os.makedirs(directory)

    return render_template('index.html',
                          regions=indian_regions,
                          crops=crops,
                          years=years)

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # Print all form data for debugging
            print("DEBUG: Form data received:")
            for key, value in request.form.items():
                print(f"DEBUG: {key} = {value}")

            # Get form data
            region = request.form['region']
            crop = request.form['crop']
            year = int(request.form['year'])

            # Get population data
            if request.form.get('use_avg_population') == 'on':
                population = generate_population(region, year)
                print(f"DEBUG: Using average population: {population}")
            else:
                population = float(request.form['population'])
                print(f"DEBUG: Using custom population: {population}")

            # Get rainfall data
            if request.form.get('use_avg_rainfall') == 'on':
                rainfall = np.random.uniform(500, 2500)  # Average rainfall
                print(f"DEBUG: Using average rainfall: {rainfall}")
            else:
                rainfall = float(request.form['rainfall'])
                print(f"DEBUG: Using custom rainfall: {rainfall}")

            # Get temperature data
            if request.form.get('use_avg_temperature') == 'on':
                temperature = np.random.uniform(20, 30)  # Average temperature
                print(f"DEBUG: Using average temperature: {temperature}")
            else:
                temperature = float(request.form['temperature'])
                print(f"DEBUG: Using custom temperature: {temperature}")

            # Get production data
            if request.form.get('use_avg_production') == 'on':
                production = generate_crop_production(region, crop, year, rainfall, temperature)
                print(f"DEBUG: Using calculated production: {production}")
            else:
                production = float(request.form['production'])
                print(f"DEBUG: Using custom production: {production}")

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
            plt.title(f'Food Scarcity Prediction for {crop} in {region} ({year})', fontsize=14)
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
