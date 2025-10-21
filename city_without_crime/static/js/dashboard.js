// Dashboard specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeDashboardCharts();
    }

    // Real-time updates for dashboard
    initializeRealTimeUpdates();

    // Search functionality
    initializeSearch();
});

function initializeDashboardCharts() {
    // Grievance status chart
    const statusCtx = document.getElementById('grievanceStatusChart');
    if (statusCtx) {
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'Under Review', 'In Progress', 'Resolved', 'Rejected'],
                datasets: [{
                    data: [12, 19, 3, 5, 2],
                    backgroundColor: [
                        '#ffc107',
                        '#0dcaf0',
                        '#fd7e14',
                        '#198754',
                        '#dc3545'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Monthly trends chart
    const trendsCtx = document.getElementById('monthlyTrendsChart');
    if (trendsCtx) {
        new Chart(trendsCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Grievances Submitted',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: '#0d6efd',
                    tension: 0.1
                }, {
                    label: 'Grievances Resolved',
                    data: [8, 15, 2, 4, 1, 2],
                    borderColor: '#198754',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

function initializeRealTimeUpdates() {
    // Simulate real-time updates (replace with actual WebSocket/SSE in production)
    setInterval(() => {
        updateDashboardStats();
    }, 30000); // Update every 30 seconds
}

async function updateDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats/');
        const data = await response.json();
        
        // Update stat cards
        document.querySelectorAll('.stat-card').forEach(card => {
            const statType = card.dataset.statType;
            if (data[statType] !== undefined) {
                const numberElement = card.querySelector('.stat-number');
                if (numberElement) {
                    numberElement.textContent = data[statType];
                }
            }
        });
    } catch (error) {
        console.error('Failed to update dashboard stats:', error);
    }
}

function initializeSearch() {
    const searchInput = document.getElementById('dashboardSearch');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const searchTerm = e.target.value.toLowerCase();
            filterDashboardItems(searchTerm);
        }, 300));
    }
}

function filterDashboardItems(searchTerm) {
    const items = document.querySelectorAll('.activity-item, .grievance-item');
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for use in other modules
window.Dashboard = {
    initializeDashboardCharts,
    updateDashboardStats,
    showAlert: window.showAlert // Reuse from main.js
};