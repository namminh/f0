#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VNStock Local Server Launcher
Automated deployment script for local development
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path
import threading
import json

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing/updating required packages...")
    try:
        # Install web requirements
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements_web.txt'
        ], check=True, capture_output=True, text=True)
        print("✅ Web packages installed successfully")
        
        # Also install main requirements if exists
        if Path('requirements.txt').exists():
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], check=True, capture_output=True, text=True)
            print("✅ Core packages updated")
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        print("Error output:", e.stderr if e.stderr else e.stdout)
        return False

def check_directory_structure():
    """Verify required directory structure exists"""
    print("📁 Checking directory structure...")
    
    required_dirs = [
        'templates',
        'stock_analysis',
        'automation',
        'automation/config'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ Directory structure is valid")
    return True

def check_stock_data():
    """Check if we have some stock data available"""
    print("📊 Checking for stock data...")
    
    stock_analysis_dir = Path('stock_analysis')
    if not stock_analysis_dir.exists():
        print("❌ No stock_analysis directory found")
        return False
    
    # Look for any stock directories with data
    stock_dirs = [d for d in stock_analysis_dir.iterdir() if d.is_dir() and d.name.isupper()]
    
    if not stock_dirs:
        print("❌ No stock data directories found")
        print("💡 Run 'python quick_update.py [SYMBOL]' to get some data first")
        return False
    
    # Check if at least one has recent data
    for stock_dir in stock_dirs:
        data_file = stock_dir / 'data' / f'{stock_dir.name}_intraday_data.json'
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('data_points', 0) > 0:
                        print(f"✅ Found data for {stock_dir.name} ({data.get('data_points', 0)} points)")
                        return True
            except:
                continue
    
    print("⚠️ Stock data directories exist but no valid data found")
    print("💡 Run 'python quick_update.py [SYMBOL]' to refresh data")
    return True  # Still allow to run, just warn

def update_config():
    """Update stocks config with available stocks"""
    print("⚙️ Updating configuration...")
    
    try:
        stock_analysis_dir = Path('stock_analysis')
        available_stocks = [d.name for d in stock_analysis_dir.iterdir() 
                           if d.is_dir() and d.name.isupper()]
        
        if not available_stocks:
            available_stocks = ['VHM', 'VIX', 'DIG']  # Default fallback
        
        config_file = Path('automation/config/stocks_config.json')
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update active stocks
        config['active_stocks'] = available_stocks[:5]  # Limit to 5 for performance
        
        # Ensure required fields exist
        if 'update_frequency' not in config:
            config['update_frequency'] = {
                "quick_update": 300,
                "full_analysis": 1800,
                "daily_report": "15:30"
            }
        
        if 'market_hours' not in config:
            config['market_hours'] = {
                "start": "09:00",
                "end": "15:00",
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
            }
        
        # Create config directory if needed
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Configuration updated with stocks: {config['active_stocks']}")
        return True
        
    except Exception as e:
        print(f"⚠️ Warning: Could not update config: {e}")
        return True  # Don't fail deployment for this

def run_quick_demo_update():
    """Run a quick update on one stock for demo purposes"""
    print("🔄 Running quick demo update...")
    
    try:
        # Try to update one stock quickly
        demo_symbols = ['VHM', 'VIX', 'DIG', 'CTG', 'SHS']
        
        for symbol in demo_symbols:
            try:
                result = subprocess.run([
                    'python', 'quick_update.py', symbol
                ], timeout=30, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Demo data ready for {symbol}")
                    return True
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout updating {symbol}, trying next...")
                continue
            except:
                continue
        
        print("⚠️ Could not update demo data, but continuing with existing data")
        return True
        
    except Exception as e:
        print(f"⚠️ Demo update failed: {e}")
        return True

def open_browser_delayed():
    """Open browser after a short delay"""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 Browser opened at http://localhost:5000")
    except:
        print("💡 Please open http://localhost:5000 manually")

def main():
    """Main deployment function"""
    print("=" * 60)
    print("VNSTOCK LOCAL DEPLOYMENT")
    print("=" * 60)
    
    # Step 1: Check Python version
    if not check_python_version():
        return False
    
    # Step 2: Check directory structure
    if not check_directory_structure():
        print("💡 Make sure you're running this from the VNstock directory")
        return False
    
    # Step 3: Install requirements
    if not install_requirements():
        return False
    
    # Step 4: Update configuration
    update_config()
    
    # Step 5: Check/prepare stock data
    has_data = check_stock_data()
    if not has_data:
        print("🔄 No stock data found, running demo update...")
        run_quick_demo_update()
    
    print("\n" + "=" * 60)
    print("DEPLOYMENT READY!")
    print("=" * 60)
    
    print("Starting Flask web server...")
    print("Dashboard will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser in background
    browser_thread = threading.Thread(target=open_browser_delayed, daemon=True)
    browser_thread.start()
    
    # Run the Flask app
    try:
        # Import and run the app
        from app import app, socketio
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except ImportError as e:
        print(f"❌ Error importing app: {e}")
        print("💡 Make sure app.py exists and all dependencies are installed")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDeployment cancelled by user")
    except Exception as e:
        print(f"Deployment failed: {e}")
        import traceback
        traceback.print_exc()