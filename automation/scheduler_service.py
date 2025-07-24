#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VNStock Automated Scheduler Service
Background service for automated stock updates and analysis
"""

import schedule
import time
import threading
import json
import subprocess
import logging
from datetime import datetime, time as dt_time
from pathlib import Path
import os
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VNStockScheduler:
    def __init__(self, config_file='automation/config/stocks_config.json'):
        self.config_file = Path(config_file)
        self.base_dir = Path(__file__).parent.parent
        self.load_config()
        self.running = False
        
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # Default configuration
                self.config = {
                    "active_stocks": ["VHM", "VIX", "DIG"],
                    "update_frequency": {
                        "quick_update": 300,  # 5 minutes
                        "full_analysis": 1800,  # 30 minutes
                        "daily_report": "15:30"
                    },
                    "market_hours": {
                        "start": "09:00",
                        "end": "15:00",
                        "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
                    }
                }
            
            logger.info(f"Configuration loaded: {len(self.config.get('active_stocks', []))} active stocks")
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = {"active_stocks": ["VHM"], "update_frequency": {"quick_update": 300}}
    
    def is_market_hours(self):
        """Check if current time is within market hours"""
        try:
            market_hours = self.config.get('market_hours', {})
            start_time = dt_time.fromisoformat(market_hours.get('start', '09:00'))
            end_time = dt_time.fromisoformat(market_hours.get('end', '15:00'))
            current_time = datetime.now().time()
            current_day = datetime.now().strftime('%A').lower()
            
            # Check if today is a trading day
            trading_days = market_hours.get('days', ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
            if current_day not in trading_days:
                return False
            
            # Check if within trading hours
            return start_time <= current_time <= end_time
            
        except Exception as e:
            logger.error(f"Error checking market hours: {e}")
            return False
    
    def run_command(self, command, timeout=60):
        """Run a system command with timeout"""
        try:
            logger.info(f"Running command: {command}")
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Command successful: {command}")
                return True
            else:
                logger.error(f"Command failed: {command}")
                logger.error(f"Error output: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {command}")
            return False
        except Exception as e:
            logger.error(f"Error running command: {command} - {e}")
            return False
    
    def update_single_stock(self, symbol):
        """Update data for a single stock"""
        command = f"python quick_update.py {symbol}"
        return self.run_command(command, timeout=90)
    
    def full_analysis_single_stock(self, symbol):
        """Run full analysis for a single stock"""
        commands = [
            f"python quick_update.py {symbol}",
            f"python stock_analysis/{symbol}/analysis/create_{symbol.lower()}_charts.py",
            f"python stock_analysis/{symbol}/analysis/create_enhanced_{symbol.lower()}_charts.py",
            f"python stock_analysis/{symbol}/analysis/create_financial_charts.py",
            f"python stock_analysis/{symbol}/analysis/create_additional_charts.py"
        ]
        
        success_count = 0
        for command in commands:
            if self.run_command(command, timeout=180):
                success_count += 1
            time.sleep(5)  # Wait between commands
        
        logger.info(f"Full analysis for {symbol}: {success_count}/{len(commands)} commands successful")
        return success_count > len(commands) // 2  # Success if more than half succeed
    
    def quick_update_all(self):
        """Quick update for all active stocks"""
        if not self.is_market_hours():
            logger.info("Outside market hours - skipping quick update")
            return
        
        logger.info("Starting quick update for all stocks")
        active_stocks = self.config.get('active_stocks', [])
        
        success_count = 0
        for symbol in active_stocks:
            try:
                if self.update_single_stock(symbol):
                    success_count += 1
                time.sleep(10)  # Wait 10 seconds between updates
            except Exception as e:
                logger.error(f"Error updating {symbol}: {e}")
        
        logger.info(f"Quick update completed: {success_count}/{len(active_stocks)} successful")
    
    def full_analysis_all(self):
        """Full analysis for all active stocks"""
        logger.info("Starting full analysis for all stocks")
        active_stocks = self.config.get('active_stocks', [])
        
        success_count = 0
        for symbol in active_stocks:
            try:
                logger.info(f"Starting full analysis for {symbol}")
                if self.full_analysis_single_stock(symbol):
                    success_count += 1
                    logger.info(f"Full analysis completed for {symbol}")
                else:
                    logger.warning(f"Full analysis partially failed for {symbol}")
                
                # Wait between stocks to prevent system overload
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in full analysis for {symbol}: {e}")
        
        logger.info(f"Full analysis completed: {success_count}/{len(active_stocks)} successful")
    
    def daily_report_generation(self):
        """Generate daily reports"""
        logger.info("Generating daily reports")
        try:
            # Run comprehensive analysis
            self.run_command("python automation/comprehensive_stock_analysis.py", timeout=300)
            
            # Generate portfolio report if available
            if Path("automation/portfolio_manager.py").exists():
                self.run_command("python automation/portfolio_manager.py --report", timeout=180)
            
            logger.info("Daily report generation completed")
            
        except Exception as e:
            logger.error(f"Error generating daily reports: {e}")
    
    def setup_schedule(self):
        """Setup the scheduled tasks"""
        logger.info("Setting up scheduled tasks")
        
        # Get update frequencies
        update_freq = self.config.get('update_frequency', {})
        quick_update_minutes = update_freq.get('quick_update', 300) // 60  # Convert to minutes
        full_analysis_minutes = update_freq.get('full_analysis', 1800) // 60
        daily_report_time = update_freq.get('daily_report', '15:30')
        
        # Schedule quick updates during market hours
        schedule.every(quick_update_minutes).minutes.do(self.quick_update_all)
        
        # Schedule full analysis less frequently
        schedule.every(full_analysis_minutes).minutes.do(self.full_analysis_all)
        
        # Schedule daily report generation
        schedule.every().day.at(daily_report_time).do(self.daily_report_generation)
        
        # Weekend maintenance (Saturday at 10:00)
        schedule.every().saturday.at("10:00").do(self.weekend_maintenance)
        
        logger.info(f"Scheduled tasks:")
        logger.info(f"- Quick updates: every {quick_update_minutes} minutes")
        logger.info(f"- Full analysis: every {full_analysis_minutes} minutes")
        logger.info(f"- Daily reports: at {daily_report_time}")
        logger.info(f"- Weekend maintenance: Saturday at 10:00")
    
    def weekend_maintenance(self):
        """Weekend maintenance tasks"""
        logger.info("Running weekend maintenance")
        try:
            # Clean old log files
            log_files = list(Path('.').glob('*.log'))
            for log_file in log_files:
                if log_file.stat().st_size > 10 * 1024 * 1024:  # > 10MB
                    log_file.rename(f"{log_file}.old")
                    logger.info(f"Archived large log file: {log_file}")
            
            # Update all stock data regardless of market hours
            logger.info("Weekend data refresh")
            active_stocks = self.config.get('active_stocks', [])
            for symbol in active_stocks:
                self.update_single_stock(symbol)
                time.sleep(5)
            
            logger.info("Weekend maintenance completed")
            
        except Exception as e:
            logger.error(f"Error in weekend maintenance: {e}")
    
    def start(self):
        """Start the scheduler service"""
        logger.info("Starting VNStock Scheduler Service")
        self.setup_schedule()
        self.running = True
        
        # Initial update
        logger.info("Running initial data update")
        self.quick_update_all()
        
        # Main scheduling loop
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
        finally:
            self.running = False
            logger.info("VNStock Scheduler Service stopped")
    
    def stop(self):
        """Stop the scheduler service"""
        self.running = False
        logger.info("Scheduler stop requested")

def run_as_service():
    """Run scheduler as a background service"""
    scheduler = VNStockScheduler()
    
    # Create a separate thread for the scheduler
    def scheduler_thread():
        scheduler.start()
    
    thread = threading.Thread(target=scheduler_thread, daemon=True)
    thread.start()
    
    logger.info("Scheduler service started in background")
    return scheduler, thread

if __name__ == "__main__":
    # Run scheduler directly
    scheduler = VNStockScheduler()
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler interrupted by user")
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
        import traceback
        traceback.print_exc()