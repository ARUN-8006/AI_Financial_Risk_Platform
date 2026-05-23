// Loan Approval Chart
new Chart(document.getElementById("loanChart"), {
    type: "doughnut",
    data: {
        labels: ["Approved", "Rejected", "Manual Review"],
        datasets: [{
            data: [842, 280, 126],
            backgroundColor: ["#00ff99", "#ff4d4d", "#ffcc00"]
        }]
    }
});

// Fraud Risk Chart
new Chart(document.getElementById("fraudChart"), {
    type: "bar",
    data: {
        labels: ["Low", "Medium", "High", "Critical"],
        datasets: [{
            label: "Transactions",
            data: [760, 320, 95, 37],
            backgroundColor: ["#00eaff", "#ffcc00", "#ff7b00", "#ff4d4d"]
        }]
    }
});

// Risk Trend Chart
new Chart(document.getElementById("riskTrendChart"), {
    type: "line",
    data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        datasets: [{
            label: "Risk Alerts",
            data: [21, 34, 28, 45, 37, 52],
            borderColor: "#00eaff",
            backgroundColor: "rgba(0,234,255,0.2)",
            tension: 0.4,
            fill: true
        }]
    }
});

// Credit Score Chart
new Chart(document.getElementById("creditChart"), {
    type: "polarArea",
    data: {
        labels: ["Excellent", "Good", "Average", "Poor"],
        datasets: [{
            data: [220, 430, 390, 208],
            backgroundColor: ["#00ff99", "#00eaff", "#ffcc00", "#ff4d4d"]
        }]
    }
});