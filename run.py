import os
import sys
import subprocess
import webbrowser
from threading import Timer

def open_browser():
    """Open browser after a delay"""
    webbrowser.open('http://127.0.0.1:5000/')

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['flask', 'numpy']
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        
        install = input("\nDo you want to install these packages now? (y/n): ")
        if install.lower() == 'y':
            for package in missing_packages:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("All required packages installed successfully.")
        else:
            print("Please install the required packages and try again.")
            return False
    
    return True

def create_directories():
    """Create necessary directories if they don't exist"""
    for directory in ['static', 'static/css', 'static/js', 'static/images', 'templates']:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def main():
    """Main function to run the web application"""
    print("="*50)
    print("FOOD SCARCITY PREDICTION SYSTEM")
    print("="*50)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Create necessary directories
    create_directories()
    
    # Check if simplified_app.py exists
    if not os.path.exists('simplified_app.py'):
        print("Error: simplified_app.py not found.")
        return
    
    print("\nStarting the web application...")
    print("The application will open in your default web browser.")
    print("Press Ctrl+C to stop the server.")
    
    # Open browser after a delay
    Timer(1.5, open_browser).start()
    
    # Run the Flask application
    os.environ['FLASK_APP'] = 'simplified_app.py'
    os.environ['FLASK_ENV'] = 'development'
    subprocess.run([sys.executable, 'simplified_app.py'])

if __name__ == "__main__":
    main()
