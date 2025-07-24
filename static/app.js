// VNStock Dashboard - Client-side JavaScript
class VNStockDashboard {
    constructor() {
        this.socket = null;
        this.stocks = [];
        this.autoUpdateEnabled = true;
        this.charts = {};
        this.init();
    }
    
    init() {
        // Initialize Socket.IO connection
        this.initSocket();
        
        // Load initial data
        this.loadStocks();
        
        // Setup periodic updates
        this.setupPeriodicUpdates();
        
        // Setup event listeners
        this.setupEventListeners();
    }
    
    initSocket() {
        try {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('Connected to server');
                this.updateStatus('Connected - Real-time updates active', 'success');
            });
            
            this.socket.on('disconnect', () => {
                console.log('Disconnected from server');
                this.updateStatus('Disconnected - Manual updates only', 'warning');
            });
            
            this.socket.on('stock_updated', (data) => {
                this.updateStockCard(data);
                this.showNotification(`${data.symbol} updated successfully`, 'success');
            });
            
            this.socket.on('analysis_complete', (data) => {
                this.showNotification(`Analysis completed for ${data.symbol}`, 'success');
                this.refreshCharts(data.symbol);
            });
            
        } catch (error) {
            console.error('Socket initialization error:', error);
            this.updateStatus('Connection failed - Manual mode only', 'error');
        }
    }
    
    async loadStocks() {
        try {
            this.showLoading(true);
            const response = await fetch('/api/stocks');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.stocks = await response.json();
            this.renderStocks();
            this.showLoading(false);
            
        } catch (error) {
            console.error('Error loading stocks:', error);
            this.showNotification('Error loading stock data', 'error');
            this.showLoading(false);
        }
    }
    
    renderStocks() {
        const container = document.getElementById('stocksContainer');
        if (!container) return;
        
        if (this.stocks.length === 0) {
            container.innerHTML = `
                <div class="no-data">
                    <h3>No Stock Data Available</h3>
                    <p>Run the update command to fetch stock data</p>
                    <button class="btn btn-primary" onclick="dashboard.updateAllStocks()">
                        Update All Stocks
                    </button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.stocks.map(stock => this.createStockCard(stock)).join('');
    }
    
    createStockCard(stock) {
        const priceChange = this.calculatePriceChange(stock);
        const priceChangeClass = priceChange >= 0 ? 'positive' : 'negative';
        const priceChangeIcon = priceChange >= 0 ? '▲' : '▼';
        
        return `
            <div class="stock-card" id="stock-${stock.symbol}">
                <div class="stock-header">
                    <div class="stock-symbol">${stock.symbol}</div>
                    <div class="stock-status online"></div>
                </div>
                
                <div class="stock-price">
                    <span class="current-price">${this.formatNumber(stock.current_price)} VND</span>
                    <span class="price-change ${priceChangeClass}">
                        ${priceChangeIcon} ${Math.abs(priceChange).toFixed(2)}%
                    </span>
                </div>
                
                <div class="stock-metrics">
                    <div class="metric">
                        <span class="label">High</span>
                        <span class="value">${this.formatNumber(stock.high_price)}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Low</span>
                        <span class="value">${this.formatNumber(stock.low_price)}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Volume</span>
                        <span class="value">${this.formatVolume(stock.total_volume)}</span>
                    </div>
                </div>
                
                <div class="buy-sell-ratio">
                    <div class="ratio-bar">
                        <div class="buy-bar" style="width: ${stock.buy_ratio}%"></div>
                        <div class="sell-bar" style="width: ${stock.sell_ratio}%"></div>
                    </div>
                    <div class="ratio-labels">
                        <span class="buy-label">${stock.buy_ratio.toFixed(1)}% Buy</span>
                        <span class="sell-label">${stock.sell_ratio.toFixed(1)}% Sell</span>
                    </div>
                </div>
                
                <div class="stock-actions">
                    <button class="btn btn-sm btn-primary" onclick="dashboard.updateStock('${stock.symbol}')">
                        <i class="icon-refresh"></i> Update
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="dashboard.analyzeStock('${stock.symbol}')">
                        <i class="icon-chart"></i> Analyze
                    </button>
                    <a href="/stock/${stock.symbol}" class="btn btn-sm btn-info">
                        <i class="icon-eye"></i> View
                    </a>
                </div>
                
                <div class="last-updated">
                    Last updated: ${this.formatTime(stock.last_updated)}
                </div>
            </div>
        `;
    }
    
    updateStockCard(stockData) {
        const cardElement = document.getElementById(`stock-${stockData.symbol}`);
        if (cardElement) {
            // Find and update the stock in our array
            const stockIndex = this.stocks.findIndex(s => s.symbol === stockData.symbol);
            if (stockIndex !== -1) {
                this.stocks[stockIndex] = stockData;
            }
            
            // Replace the card with updated data
            cardElement.outerHTML = this.createStockCard(stockData);
            
            // Add update animation
            const newCard = document.getElementById(`stock-${stockData.symbol}`);
            if (newCard) {
                newCard.classList.add('updated');
                setTimeout(() => newCard.classList.remove('updated'), 2000);
            }
        }
    }
    
    async updateStock(symbol) {
        try {
            this.showActionLoading(symbol, 'Updating...');
            
            const response = await fetch(`/api/update/${symbol}`);
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`${symbol} updated successfully`, 'success');
            } else {
                this.showNotification(`Failed to update ${symbol}: ${result.message}`, 'error');
            }
            
        } catch (error) {
            console.error(`Error updating ${symbol}:`, error);
            this.showNotification(`Error updating ${symbol}`, 'error');
        } finally {
            this.hideActionLoading(symbol);
        }
    }
    
    async analyzeStock(symbol) {
        try {
            this.showActionLoading(symbol, 'Analyzing...');
            
            const response = await fetch(`/api/update/${symbol}/full`);
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`Full analysis completed for ${symbol}`, 'success');
            } else {
                this.showNotification(`Analysis failed for ${symbol}: ${result.message}`, 'error');
            }
            
        } catch (error) {
            console.error(`Error analyzing ${symbol}:`, error);
            this.showNotification(`Error analyzing ${symbol}`, 'error');
        } finally {
            this.hideActionLoading(symbol);
        }
    }
    
    async updateAllStocks() {
        if (this.stocks.length === 0) {
            this.showNotification('No stocks to update', 'warning');
            return;
        }
        
        this.showNotification('Updating all stocks...', 'info');
        
        for (const stock of this.stocks) {
            try {
                await this.updateStock(stock.symbol);
                // Small delay between updates
                await new Promise(resolve => setTimeout(resolve, 2000));
            } catch (error) {
                console.error(`Error updating ${stock.symbol}:`, error);
            }
        }
        
        this.showNotification('All stocks update completed', 'success');
    }
    
    async analyzeAllStocks() {
        if (this.stocks.length === 0) {
            this.showNotification('No stocks to analyze', 'warning');
            return;
        }
        
        this.showNotification('Running full analysis on all stocks...', 'info');
        
        for (const stock of this.stocks) {
            try {
                await this.analyzeStock(stock.symbol);
                // Longer delay between analyses
                await new Promise(resolve => setTimeout(resolve, 5000));
            } catch (error) {
                console.error(`Error analyzing ${stock.symbol}:`, error);
            }
        }
        
        this.showNotification('Full analysis completed for all stocks', 'success');
    }
    
    toggleAutoUpdate() {
        this.autoUpdateEnabled = !this.autoUpdateEnabled;
        const status = this.autoUpdateEnabled ? 'Auto-update enabled' : 'Auto-update disabled';
        this.updateStatus(status, this.autoUpdateEnabled ? 'success' : 'warning');
        this.showNotification(status, this.autoUpdateEnabled ? 'success' : 'warning');
        
        // Update UI elements
        const toggleBtn = document.getElementById('autoUpdateToggle');
        if (toggleBtn) {
            toggleBtn.textContent = this.autoUpdateEnabled ? 'Disable Auto-Update' : 'Enable Auto-Update';
            toggleBtn.className = `btn ${this.autoUpdateEnabled ? 'btn-warning' : 'btn-success'}`;
        }
    }
    
    setupPeriodicUpdates() {
        // Auto-refresh every 5 minutes if enabled
        setInterval(() => {
            if (this.autoUpdateEnabled) {
                console.log('Auto-refreshing stock data...');
                this.loadStocks();
            }
        }, 5 * 60 * 1000); // 5 minutes
        
        // Update time stamps every minute
        setInterval(() => {
            this.updateTimeStamps();
        }, 60 * 1000); // 1 minute
    }
    
    setupEventListeners() {
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'r':
                        e.preventDefault();
                        this.loadStocks();
                        break;
                    case 'u':
                        e.preventDefault();
                        this.updateAllStocks();
                        break;
                }
            }
        });
        
        // Handle visibility change (browser tab focus)
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.autoUpdateEnabled) {
                // Refresh when user returns to tab
                this.loadStocks();
            }
        });
    }
    
    // Utility methods
    calculatePriceChange(stock) {
        // This would need historical data to calculate actual change
        // For now, return a random change for demo purposes
        const range = stock.high_price - stock.low_price;
        const midPoint = (stock.high_price + stock.low_price) / 2;
        return ((stock.current_price - midPoint) / midPoint) * 100;
    }
    
    formatNumber(num) {
        if (!num) return '0';
        return num.toLocaleString('vi-VN', { 
            minimumFractionDigits: 0, 
            maximumFractionDigits: 2 
        });
    }
    
    formatVolume(volume) {
        if (volume >= 1000000) {
            return (volume / 1000000).toFixed(1) + 'M';
        } else if (volume >= 1000) {
            return (volume / 1000).toFixed(1) + 'K';
        }
        return volume.toString();
    }
    
    formatTime(timestamp) {
        if (!timestamp || timestamp === 'N/A') return 'N/A';
        try {
            return new Date(timestamp).toLocaleString('vi-VN');
        } catch {
            return timestamp;
        }
    }
    
    updateTimeStamps() {
        const timeElements = document.querySelectorAll('.last-updated');
        timeElements.forEach(element => {
            const stockCard = element.closest('.stock-card');
            if (stockCard) {
                const symbol = stockCard.id.replace('stock-', '');
                const stock = this.stocks.find(s => s.symbol === symbol);
                if (stock) {
                    element.textContent = `Last updated: ${this.formatTime(stock.last_updated)}`;
                }
            }
        });
    }
    
    showLoading(show) {
        const loadingElement = document.getElementById('loadingIndicator');
        const contentElement = document.getElementById('mainContent');
        
        if (loadingElement && contentElement) {
            loadingElement.style.display = show ? 'block' : 'none';
            contentElement.style.display = show ? 'none' : 'block';
        }
    }
    
    showActionLoading(symbol, message) {
        const card = document.getElementById(`stock-${symbol}`);
        if (card) {
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `<div class="loading-message">${message}</div>`;
            card.appendChild(overlay);
        }
    }
    
    hideActionLoading(symbol) {
        const card = document.getElementById(`stock-${symbol}`);
        if (card) {
            const overlay = card.querySelector('.loading-overlay');
            if (overlay) {
                overlay.remove();
            }
        }
    }
    
    updateStatus(message, type) {
        const statusElement = document.getElementById('systemStatus');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `system-status ${type}`;
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Add to notifications container
        let container = document.getElementById('notificationsContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notificationsContainer';
            container.className = 'notifications-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    refreshCharts(symbol) {
        // Refresh charts for a specific stock if on detail page
        if (window.location.pathname.includes(`/stock/${symbol}`)) {
            setTimeout(() => {
                location.reload();
            }, 2000);
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new VNStockDashboard();
});

// Global functions for HTML onclick handlers
function updateStock(symbol) {
    if (window.dashboard) {
        window.dashboard.updateStock(symbol);
    }
}

function analyzeStock(symbol) {
    if (window.dashboard) {
        window.dashboard.analyzeStock(symbol);
    }
}

function updateAllStocks() {
    if (window.dashboard) {
        window.dashboard.updateAllStocks();
    }
}

function analyzeAllStocks() {
    if (window.dashboard) {
        window.dashboard.analyzeAllStocks();
    }
}

function toggleAutoUpdate() {
    if (window.dashboard) {
        window.dashboard.toggleAutoUpdate();
    }
}