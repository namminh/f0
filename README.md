# 📈 VNStock - Automated Stock Analysis System

🤖 **AI-Powered Vietnamese Stock Analysis Platform with Real-time Data Processing**

---

## 🎯 **Overview**

VNStock is an automated stock analysis system designed for Vietnamese stock market with integrated AI analysis capabilities. The system provides real-time data collection, automated chart generation, comprehensive reporting, and a mobile-first web interface for F0 (beginner) investors.

### ✨ **Key Features**

- 🔄 **Automated Data Collection**: Real-time intraday data for Vietnamese stocks
- 📊 **AI Analysis**: Intelligent stock analysis with DOMINUS agent integration
- 📱 **F0-Website**: Mobile-first web interface for beginner investors
- 🚦 **Traffic Light Signals**: Simple MUA/GIỮ/TRÁNH recommendations
- 📈 **23 Chart Types**: Comprehensive technical and financial analysis charts
- 🔧 **Windows Automation**: Scheduled updates via Windows Task Scheduler
- 🌐 **Multi-Stock Support**: Portfolio-level analysis and monitoring

---

## 🏗️ **System Architecture**

```
VNStock/
├── 🤖 DOMINUS Agent Integration
├── 📱 F0-Website (FastAPI + Mobile UI)
├── 📊 Stock Analysis Engine
├── 🔄 Automation System
└── 📈 Multi-Stock Portfolio Management
```

### **🔧 Core Components**

1. **📊 Analysis Engine**: Python-based stock data processing
2. **🤖 DOMINUS Agent**: AI-powered analysis and decision making
3. **📱 F0-Website**: FastAPI web application with mobile-first design
4. **🔄 Automation**: Windows scheduler integration for regular updates
5. **📈 Portfolio Management**: Multi-stock monitoring and reporting

---

## 🚀 **Quick Start**

### **📋 Prerequisites**
- Python 3.8+ with pip
- Node.js (for F0-website frontend assets)
- Windows OS (for automation features)

### **⚡ Installation**
```bash
# 1. Clone and setup environment
git clone <repository>
cd VNstock
pip install -r requirements.txt

# 2. Run F0-Website (Recommended for beginners)
cd f0-website
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Access web interface
# Open: http://127.0.0.1:8000
```

### **🎯 For F0 Users (Beginners)**
1. **Navigate to**: http://127.0.0.1:8000
2. **Enter stock symbol**: VHM, VIC, TCB, etc.
3. **Get instant analysis**: 🟢 MUA, 🟡 GIỮ, 🔴 TRÁNH
4. **View detailed reports**: Click "Báo cáo chi tiết"

---

## 📊 **Usage Examples**

### **🔥 Quick Analysis (30 seconds)**
```bash
# Analyze single stock with instant results
python quick_analyze.py VHM

# Output: Real-time analysis with charts and HTML report
# Location: stock_analysis/VHM/reports/VHM_enhanced_report.html
```

### **📈 Comprehensive Analysis (5-8 minutes)**
```bash
# Full analysis with 23 charts and detailed reports
python automation/enhanced_stock_analyzer.py VHM

# Output: Complete analysis package
# - 23 technical analysis charts
# - Financial health dashboard
# - Risk assessment report
# - Trading recommendations
```

### **🔄 Portfolio Updates**
```bash
# Update all stocks in portfolio
python batch_update.py

# Update specific stocks
python quick_update.py VHM VIC TCB
```

---

## 🌐 **F0-Website Interface**

### **📱 Mobile-First Design**
- **🎯 Target**: F0 (beginner) investors
- **🚦 Simple Signals**: Traffic light system for decisions
- **📊 Instant Analysis**: 30-second quick analysis
- **📈 Detailed Reports**: Comprehensive analysis on demand
- **🔗 Direct Integration**: Real-time connection to DOMINUS agent

### **🔧 API Endpoints**
- `POST /api/analyze` - Instant stock analysis
- `POST /api/comprehensive-analysis` - Full analysis with charts
- `GET /api/reports/{symbol}` - Available reports
- `GET /stock/{symbol}` - Stock detail page

---

## 🤖 **DOMINUS Agent Integration**

### **🧠 AI-Powered Analysis**
The DOMINUS agent provides intelligent stock analysis using:

- **📈 Technical Indicators**: RSI, MACD, Bollinger Bands
- **💰 Financial Metrics**: P/E, ROE, Debt ratios
- **📊 Market Sentiment**: Volume analysis, price trends
- **🎯 Risk Assessment**: Volatility and correlation analysis

### **⚡ Agent Commands**
```bash
# Core analysis workflow
python quick_analyze.py [SYMBOL]      # Fast analysis
python batch_update.py                # Update all stocks
python automation/enhanced_stock_analyzer.py [SYMBOL]  # Deep analysis
```

---

## 📁 **Project Structure**

### **🏗️ Main Directories**
```
VNstock/
├── 📱 f0-website/              # FastAPI web application
│   ├── app/                    # Application code
│   ├── templates/              # HTML templates
│   └── static/                 # CSS, JS assets
├── 📊 stock_analysis/          # Generated analysis data
│   └── [SYMBOL]/              # Per-stock analysis
│       ├── data/              # JSON data files
│       ├── charts/            # Generated PNG charts
│       └── reports/           # HTML reports
├── 🔄 automation/             # Automation scripts
│   ├── config/               # Configuration files
│   └── *.py                  # Analysis scripts
├── 📚 docs/                   # Documentation
│   ├── archive/              # Historical docs
│   └── troubleshooting/      # Issue resolution guides
└── 🤖 CLAUDE.md              # Agent instructions
```

### **📊 Generated Content Structure**
```
stock_analysis/[SYMBOL]/
├── data/
│   ├── [SYMBOL]_intraday_data.json     # Real-time data
│   ├── [SYMBOL]_financial_ratios.json  # Financial metrics
│   └── [SYMBOL]_historical_3years.json # Historical prices
├── charts/
│   ├── key_charts/                     # 3 main charts
│   ├── technical_analysis/             # 5 technical charts
│   ├── financial_analysis/             # 5 financial charts
│   └── additional_analysis/            # 10 specialized charts
└── reports/
    ├── [SYMBOL]_enhanced_report.html   # Main report
    └── [SYMBOL]_comprehensive_report.html # Full analysis
```

---

## 🔄 **Automation & Scheduling**

### **⏰ Windows Task Scheduler Integration**
```bash
# Setup automated analysis (runs 2x daily: 11:00 AM & 3:00 PM)
python automation/setup_windows_scheduler.bat

# Manual scheduler commands
automation/run_11h_update.bat     # 11 AM update
automation/run_15h_update.bat     # 3 PM update
```

### **🔧 Configuration**
```json
// automation/config/stocks_config.json
{
  "active_stocks": ["VHM", "VIC", "TCB", "VCB", "GAS"],
  "update_frequency": {
    "intraday": 300,
    "full_analysis": 3600
  },
  "market_hours": {
    "start": "09:00",
    "end": "15:00"
  }
}
```

---

## 📊 **Supported Stock Symbols**

### **🏢 Currently Configured**
- **VHM** - Vinhomes (Real Estate)
- **VIC** - Vingroup (Conglomerate)
- **TCB** - Techcombank (Banking)
- **VCB** - Vietcombank (Banking)
- **CTG** - VietinBank (Banking)
- **GAS** - PetroVietnam Gas (Energy)
- **VRE** - Vincom Retail (Real Estate)
- **DIG** - DIC Corporation (Real Estate)

### **➕ Adding New Stocks**
```bash
# Add new stock to system
python automation/portfolio_manager.py --add [SYMBOL]
python get_data_for_stock.py [SYMBOL]

# Verify addition
python quick_update.py [SYMBOL]
```

---

## 🚨 **Troubleshooting**

### **📋 Common Issues**

#### **🔌 F0-Website Not Loading**
```bash
# Check if server is running
curl http://127.0.0.1:8000/health

# Restart server
cd f0-website
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### **📊 Reports Not Found**
```bash
# Verify report paths
ls stock_analysis/[SYMBOL]/reports/

# Regenerate reports
python quick_analyze.py [SYMBOL]
```

#### **📈 Data Update Failures**
```bash
# Test data collection
python stock_data_collector.py

# Check configuration
python -c "from automation.config import *; print(load_config())"
```

### **📚 Additional Help**
- **🔧 Troubleshooting Guide**: `docs/troubleshooting/REPORT_LOADING_FIX.md`
- **🤖 Agent Instructions**: `CLAUDE.md`
- **📱 F0-Website Documentation**: `f0-website/README.md`

---

## 🎯 **Performance Metrics**

### **⚡ Analysis Speed**
- **Quick Analysis**: ~30 seconds
- **Comprehensive Analysis**: 5-8 minutes
- **Portfolio Update**: 2-3 minutes per stock
- **F0-Website Response**: <2 seconds

### **📊 Output Quality**
- **📈 Charts Generated**: 23 per comprehensive analysis
- **📋 Report Format**: HTML with embedded charts
- **🎯 Accuracy**: Based on real-time market data
- **📱 Mobile Optimization**: 100% responsive design

---

## 🤝 **Contributing**

### **📋 Development Guidelines**
1. **Follow Python PEP 8** for code style
2. **Update CLAUDE.md** for new agent instructions
3. **Test F0-website functionality** before commits
4. **Document new stock additions** in configuration

### **🔄 Development Workflow**
```bash
# 1. Test new features
python quick_analyze.py [SYMBOL]

# 2. Verify F0-website integration
cd f0-website && python -m uvicorn app.main:app --reload

# 3. Update documentation
# Edit CLAUDE.md and relevant README files
```

---

## 📄 **License & Disclaimer**

### **⚖️ License**
This project is for educational and research purposes. 

### **⚠️ Investment Disclaimer**
- **Not Financial Advice**: All analysis is for informational purposes only
- **Do Your Research**: Always conduct your own due diligence
- **Risk Warning**: Stock investments carry inherent risks
- **F0 Guidance**: Designed to help beginners learn, not replace professional advice

---

## 📞 **Support**

### **🛠️ Technical Support**
- **📖 Documentation**: Check `docs/` directory
- **🤖 Agent Instructions**: See `CLAUDE.md`
- **🔧 Issue Resolution**: See `docs/troubleshooting/`

### **🎯 F0-Website Support**
- **📱 User Guide**: Built-in help in web interface
- **🔗 Quick Access**: http://127.0.0.1:8000
- **🚦 Signal Explanation**: Traffic light system built-in

---

**🚀 Happy Trading & Analysis! 📈**

*Last Updated: July 2025 | Version: 2.0 | F0-Website Ready*