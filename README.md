# Food Scarcity Prediction System for India

A web application that predicts food scarcity or surplus in different regions of India based on crop selection and population data.

## Features

- Predicts food scarcity/surplus for a selected region in India and crop type
- Considers population data, rainfall, temperature, and production capacity
- Generates realistic data based on Indian agricultural patterns
- Provides detailed recommendations based on prediction results
- Simple and intuitive user interface

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/food-scarcity-prediction.git
   cd food-scarcity-prediction
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python run.py
   ```

4. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## How to Use

1. Select a region in India from the dropdown menu
2. Select a crop from the dropdown menu
3. Select a year for prediction
4. Optionally customize population, rainfall, temperature, and production values
5. Click "Predict Food Scarcity" to get your results
6. View the detailed prediction results and recommendations

## Project Structure

- `app.py`: Main Flask application with prediction logic
- `run.py`: Helper script to start the application
- `templates/`: HTML templates for the web interface
- `static/`: CSS, JavaScript, and image files
- `requirements.txt`: List of required Python packages
- `food_scarcity_dataset.csv`: Generated dataset (50,000 data points)
- `plots/`: Directory containing EDA visualizations
- `models/`: Directory containing trained machine learning models
- `predictions/`: Directory containing prediction visualizations

## Requirements

- Python 3.6+
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn
- xgboost
- joblib

## How to Use

1. Run the main script:
   ```
   python main.py
   ```

2. The script will:
   - Check for required packages and install if needed
   - Generate the dataset if it doesn't exist
   - Run exploratory data analysis
   - Train machine learning models
   - Launch the prediction interface

3. In the prediction interface:
   - Select a region in India
   - Select a crop
   - Select a season
   - Enter a year
   - Optionally modify population, rainfall, temperature, and production values
   - View the prediction results and visualizations

## Dataset Information

The synthetic dataset includes the following features:
- Region: 36 Indian states and union territories
- Crop: 37 major crops grown in India
- Season: Kharif, Rabi, or Zaid
- Year: 2010-2023
- Population: Based on realistic population data for each region
- Rainfall: Annual rainfall in mm
- Temperature: Average temperature in degrees Celsius
- Production: Crop production in tonnes
- Consumption Need: Calculated based on population and per capita consumption
- Balance: Difference between production and consumption
- Balance Percentage: Percentage surplus or deficit
- Scarcity Level: Categorized as Severe Scarcity, Moderate Scarcity, Mild Scarcity, Balanced, Mild Surplus, Moderate Surplus, or Large Surplus

## Model Information

The system trains and compares multiple regression models:
- Linear Regression
- Random Forest
- Gradient Boosting
- XGBoost

The best-performing model is selected based on RMSE (Root Mean Square Error) and used for predictions.

## Limitations

- The dataset is synthetic and based on approximations
- Real-world food scarcity depends on many additional factors not included in this model
- The model does not account for imports/exports, storage, distribution issues, or economic factors

## Future Improvements

- Incorporate real data from government sources
- Add more features like soil quality, irrigation facilities, etc.
- Include economic factors like food prices and income levels
- Implement time series forecasting for future predictions
- Create a web-based interface for easier access
