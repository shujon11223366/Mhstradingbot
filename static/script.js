// AI Trading Bot Dashboard JavaScript

class TradingBotDashboard {
    constructor() {
        this.charts = {};
        this.refreshInterval = 30000; // 30 seconds
        this.refreshTimer = null;
        this.lastUpdateTime = null;
        
        this.init();
    }
    
    init() {
        console.log('🤖 Initializing Trading Bot Dashboard...');
        
        // Initialize components
        this.updateCurrentTime();
        this.setupEventListeners();
        this.initializeCharts();
        this.loadInitialData();
        this.startAutoRefresh();
        
        console.log('✅ Dashboard initialized successfully');
    }
    
    setupEventListeners() {
        // Button event listeners
        document.getElementById('generate-signal-btn')?.addEventListener('click', () => this.generateSignal());
        document.getElementById('refresh-data-btn')?.addEventListener('click', () => this.refreshData());
        document.getElementById('export-data-btn')?.addEventListener('click', () => this.exportData());
        document.getElementById('health-check-btn')?.addEventListener('click', () => this.performHealthCheck());
        
        // Filter buttons for signals table
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.addEventListener('click', (e) => this.filterSignals(e.target.dataset.filter));
        });
        
        // Signal row click handler
        document.addEventListener('click', (e) => {
            if (e.target.closest('#signals-tbody tr')) {
                this.showSignalDetails(e.target.closest('tr'));
            }
        });
        
        // Update time every second
        setInterval(() => this.updateCurrentTime(), 1000);
    }
    
    async loadInitialData() {
        this.showLoading(true);
        
        try {
            await Promise.all([
                this.loadStats(),
                this.loadRecentSignals(),
                this.loadPerformanceByPairs(),
                this.loadMarketStatus(),
                this.loadSystemHealth()
            ]);
            
            console.log('📊 Initial data loaded successfully');
        } catch (error) {
            console.error('❌ Error loading initial data:', error);
            this.showAlert('Error loading dashboard data', 'danger');
        } finally {
            this.showLoading(false);
        }
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const result = await response.json();
            
            if (result.success) {
                this.updateStatsCards(result.data.performance);
                this.updateTradingSessionInfo(result.data.trading_session);
                this.lastUpdateTime = new Date();
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    async loadRecentSignals() {
        try {
            const response = await fetch('/api/signals/recent?limit=20');
            const result = await response.json();
            
            if (result.success) {
                this.updateSignalsTable(result.data);
                this.updatePerformanceChart(result.data);
            }
        } catch (error) {
            console.error('Error loading recent signals:', error);
        }
    }
    
    async loadPerformanceByPairs() {
        try {
            const response = await fetch('/api/performance/pairs');
            const result = await response.json();
            
            if (result.success) {
                this.updatePairsPerformance(result.data);
            }
        } catch (error) {
            console.error('Error loading performance by pairs:', error);
        }
    }
    
    async loadMarketStatus() {
        try {
            const response = await fetch('/api/market/status');
            const result = await response.json();
            
            if (result.success) {
                this.updateMarketSessions(result.data);
            }
        } catch (error) {
            console.error('Error loading market status:', error);
        }
    }
    
    async loadSystemHealth() {
        try {
            const response = await fetch('/api/health');
            const result = await response.json();
            
            if (result.success) {
                this.updateSystemHealth(result.components);
                this.updateStatusIndicator(result.healthy);
            }
        } catch (error) {
            console.error('Error loading system health:', error);
            this.updateStatusIndicator(false);
        }
    }
    
    updateStatsCards(stats) {
        document.getElementById('total-signals').textContent = stats.total_signals || 0;
        document.getElementById('success-rate').textContent = `${stats.win_rate || 0}%`;
        document.getElementById('today-signals').textContent = stats.signals_today || 0;
        document.getElementById('ai-confidence').textContent = `${stats.avg_confidence || 0}%`;
    }
    
    updateSignalsTable(signals) {
        const tbody = document.getElementById('signals-tbody');
        tbody.innerHTML = '';
        
        signals.forEach(signal => {
            const row = this.createSignalRow(signal);
            tbody.appendChild(row);
        });
    }
    
    createSignalRow(signal) {
        const row = document.createElement('tr');
        row.dataset.signalId = signal.signal_id;
        row.classList.add('fade-in');
        
        const time = new Date(signal.timestamp).toLocaleTimeString();
        const direction = signal.direction;
        const directionClass = direction === 'CALL' ? 'direction-call' : 'direction-put';
        const directionIcon = direction === 'CALL' ? '📈' : '📉';
        
        const status = signal.outcome || 'pending';
        const statusClass = status === 'win' ? 'win' : status === 'loss' ? 'loss' : 'pending';
        
        const riskClass = `risk-${signal.risk_level.toLowerCase()}`;
        
        row.innerHTML = `
            <td>${time}</td>
            <td><strong>${signal.pair}</strong></td>
            <td class="${directionClass}">${directionIcon} ${direction}</td>
            <td>$${parseFloat(signal.entry_price).toFixed(5)}</td>
            <td>
                ${signal.confidence}%
                <div class="confidence-bar">
                    <div class="confidence-fill ${this.getConfidenceLevel(signal.confidence)}" 
                         style="width: ${signal.confidence}%"></div>
                </div>
            </td>
            <td class="${riskClass}">${signal.risk_level}</td>
            <td><span class="signal-status ${statusClass}">${status}</span></td>
        `;
        
        return row;
    }
    
    getConfidenceLevel(confidence) {
        if (confidence >= 80) return 'high';
        if (confidence >= 65) return 'medium';
        return 'low';
    }
    
    updatePairsPerformance(pairsData) {
        const container = document.getElementById('pairs-performance');
        container.innerHTML = '';
        
        Object.entries(pairsData).slice(0, 8).forEach(([pair, stats]) => {
            const item = document.createElement('div');
            item.className = 'performance-item slide-in';
            
            const winRate = stats.win_rate;
            const rateClass = this.getPerformanceClass(winRate);
            
            item.innerHTML = `
                <div>
                    <strong>${pair}</strong>
                    <small class="text-muted d-block">${stats.total} signals</small>
                </div>
                <span class="performance-rate ${rateClass}">${winRate}%</span>
            `;
            
            container.appendChild(item);
        });
    }
    
    getPerformanceClass(winRate) {
        if (winRate >= 85) return 'excellent';
        if (winRate >= 75) return 'good';
        if (winRate >= 65) return 'average';
        return 'poor';
    }
    
    updateMarketSessions(marketData) {
        const container = document.getElementById('market-sessions');
        container.innerHTML = '';
        
        const sessions = [
            { name: 'Asian', timezone: 'Tokyo', active: marketData.active_sessions?.includes('asian') },
            { name: 'European', timezone: 'London', active: marketData.active_sessions?.includes('european') },
            { name: 'US', timezone: 'New York', active: marketData.active_sessions?.includes('us') }
        ];
        
        sessions.forEach(session => {
            const item = document.createElement('div');
            item.className = `session-indicator ${session.active ? 'active' : 'inactive'}`;
            
            item.innerHTML = `
                <div class="session-dot ${session.active ? 'active' : 'inactive'}"></div>
                <div class="flex-grow-1">
                    <strong>${session.name} Session</strong>
                    <small class="text-muted d-block">${session.timezone}</small>
                </div>
                <span class="badge ${session.active ? 'bg-success' : 'bg-secondary'}">
                    ${session.active ? 'ACTIVE' : 'CLOSED'}
                </span>
            `;
            
            container.appendChild(item);
        });
    }
    
    updateSystemHealth(healthData) {
        const container = document.getElementById('system-health');
        container.innerHTML = '';
        
        const components = [
            { name: 'Signal Generator', key: 'signal_generator' },
            { name: 'Market Data', key: 'market_data' },
            { name: 'Currency Pairs', key: 'currency_pairs' },
            { name: 'Signal History', key: 'signal_history' }
        ];
        
        components.forEach(component => {
            const healthy = healthData[component.key];
            const item = document.createElement('div');
            item.className = 'health-item';
            
            item.innerHTML = `
                <span>${component.name}</span>
                <span class="health-status ${healthy ? 'healthy' : 'unhealthy'}">
                    ${healthy ? '✅ HEALTHY' : '❌ UNHEALTHY'}
                </span>
            `;
            
            container.appendChild(item);
        });
    }
    
    updateStatusIndicator(isHealthy) {
        const statusElement = document.getElementById('status');
        const iconElement = statusElement.previousElementSibling;
        
        if (isHealthy) {
            statusElement.textContent = 'Online';
            iconElement.className = 'fas fa-circle text-success me-1';
        } else {
            statusElement.textContent = 'Issues Detected';
            iconElement.className = 'fas fa-circle text-warning me-1';
        }
    }
    
    updateTradingSessionInfo(sessionData) {
        const container = document.getElementById('market-sessions');
        if (!container) return;
        
        // This updates the quick info in the sidebar
        const activeSessions = sessionData.active_sessions || [];
        const sessionText = activeSessions.length > 0 
            ? `${activeSessions.length} active session${activeSessions.length > 1 ? 's' : ''}`
            : 'No active sessions';
        
        // You can add a small indicator here if needed
    }
    
    initializeCharts() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;
        
        this.charts.performance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Win Rate %',
                    data: [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Signals Count',
                    data: [],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Win Rate (%)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Signals Count'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }
    
    updatePerformanceChart(signals) {
        if (!this.charts.performance || !signals.length) return;
        
        // Group signals by hour for the chart
        const hourlyData = {};
        signals.forEach(signal => {
            const hour = new Date(signal.timestamp).getHours();
            const key = `${hour}:00`;
            
            if (!hourlyData[key]) {
                hourlyData[key] = { total: 0, wins: 0 };
            }
            
            hourlyData[key].total++;
            if (signal.outcome === 'win') {
                hourlyData[key].wins++;
            }
        });
        
        const labels = Object.keys(hourlyData).sort();
        const winRates = labels.map(label => {
            const data = hourlyData[label];
            return data.total > 0 ? (data.wins / data.total * 100) : 0;
        });
        const counts = labels.map(label => hourlyData[label].total);
        
        this.charts.performance.data.labels = labels;
        this.charts.performance.data.datasets[0].data = winRates;
        this.charts.performance.data.datasets[1].data = counts;
        this.charts.performance.update();
    }
    
    async generateSignal() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/signal/generate');
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('New signal generated successfully!', 'success');
                await this.refreshData();
            } else {
                this.showAlert(result.error || 'Failed to generate signal', 'danger');
            }
        } catch (error) {
            console.error('Error generating signal:', error);
            this.showAlert('Error generating signal', 'danger');
        } finally {
            this.showLoading(false);
        }
    }
    
    async refreshData() {
        console.log('🔄 Refreshing dashboard data...');
        await this.loadInitialData();
        this.showAlert('Data refreshed successfully!', 'info');
    }
    
    async exportData() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/export/signals?format=csv');
            const result = await response.json();
            
            if (result.success) {
                this.showAlert(`Data exported to ${result.filename}`, 'success');
            } else {
                this.showAlert(result.error || 'Failed to export data', 'danger');
            }
        } catch (error) {
            console.error('Error exporting data:', error);
            this.showAlert('Error exporting data', 'danger');
        } finally {
            this.showLoading(false);
        }
    }
    
    async performHealthCheck() {
        this.showLoading(true);
        
        try {
            await this.loadSystemHealth();
            this.showAlert('Health check completed!', 'info');
        } catch (error) {
            console.error('Error performing health check:', error);
            this.showAlert('Error performing health check', 'danger');
        } finally {
            this.showLoading(false);
        }
    }
    
    filterSignals(filter) {
        const rows = document.querySelectorAll('#signals-tbody tr');
        
        // Update active filter button
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
        
        // Filter rows
        rows.forEach(row => {
            const statusElement = row.querySelector('.signal-status');
            const status = statusElement ? statusElement.textContent.trim().toLowerCase() : '';
            
            if (filter === 'all' || status === filter) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    showSignalDetails(row) {
        const signalId = row.dataset.signalId;
        // Here you would fetch and show detailed signal information
        // For now, just show the modal
        const modal = new bootstrap.Modal(document.getElementById('signalModal'));
        
        document.getElementById('signal-details').innerHTML = `
            <div class="alert alert-info">
                <strong>Signal ID:</strong> ${signalId}<br>
                <em>Detailed signal analysis would be shown here...</em>
            </div>
        `;
        
        modal.show();
    }
    
    updateCurrentTime() {
        const now = new Date();
        const timeString = now.toLocaleString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            timeZoneName: 'short'
        });
        
        const timeElement = document.getElementById('current-time');
        if (timeElement) {
            timeElement.textContent = timeString;
        }
    }
    
    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            console.log('🔄 Auto-refreshing data...');
            this.loadStats();
            this.loadRecentSignals();
        }, this.refreshInterval);
    }
    
    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            if (show) {
                overlay.classList.add('show');
            } else {
                overlay.classList.remove('show');
            }
        }
    }
    
    showAlert(message, type = 'info') {
        // Create alert element
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 300px;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new TradingBotDashboard();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        window.dashboard?.stopAutoRefresh();
    } else {
        window.dashboard?.startAutoRefresh();
        window.dashboard?.refreshData();
    }
});
