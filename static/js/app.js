const form = document.getElementById("analysis-form");
const saveButton = document.getElementById("save-btn");
const resetButton = document.getElementById("reset-btn");

let pendingPayload = null;
let categoryChart = null;
let balanceChart = null;

const currency = (value) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(value || 0);

const setText = (id, value) => {
    document.getElementById(id).textContent = value;
};

const renderList = (id, items, emptyText) => {
    const container = document.getElementById(id);
    container.innerHTML = "";
    const values = items && items.length ? items : [emptyText];
    values.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        container.appendChild(li);
    });
};

const riskPill = (level) => {
    const lower = level.toLowerCase();
    return `<span class="risk-pill ${lower}">${level}</span>`;
};

const renderHistory = (transactions) => {
    const body = document.getElementById("history-body");
    body.innerHTML = "";

    if (!transactions.length) {
        body.innerHTML = '<tr><td colspan="6">No saved transactions yet.</td></tr>';
        return;
    }

    transactions.forEach((tx) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${new Date(tx.created_at).toLocaleString()}</td>
            <td>${tx.category}</td>
            <td>${tx.expense_type}</td>
            <td>${currency(tx.expense_amount)}</td>
            <td>${riskPill(tx.risk_level)}</td>
            <td>${tx.message}</td>
        `;
        body.appendChild(row);
    });
};

const renderCategoryChart = (items) => {
    const context = document.getElementById("category-chart");
    if (categoryChart) categoryChart.destroy();
    categoryChart = new Chart(context, {
        type: "bar",
        data: {
            labels: items.map((item) => item.category),
            datasets: [{ data: items.map((item) => item.amount), backgroundColor: "#38bdf8", borderRadius: 12 }],
        },
        options: {
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: "#cbd5e1" }, grid: { color: "rgba(148,163,184,0.08)" } },
                y: { ticks: { color: "#cbd5e1" }, grid: { color: "rgba(148,163,184,0.08)" } },
            },
        },
    });
};

const renderBalanceChart = (items) => {
    const context = document.getElementById("balance-chart");
    if (balanceChart) balanceChart.destroy();
    balanceChart = new Chart(context, {
        type: "line",
        data: {
            labels: items.map((item) => item.label),
            datasets: [
                {
                    data: items.map((item) => item.balance),
                    borderColor: "#22c55e",
                    backgroundColor: "rgba(34,197,94,0.12)",
                    fill: true,
                    tension: 0.35,
                },
            ],
        },
        options: {
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: "#cbd5e1" }, grid: { color: "rgba(148,163,184,0.08)" } },
                y: { ticks: { color: "#cbd5e1" }, grid: { color: "rgba(148,163,184,0.08)" } },
            },
        },
    });
};

const fetchDashboard = async () => {
    const response = await fetch("/api/dashboard");
    const dashboard = await response.json();
    setText("total-spending", currency(dashboard.total_spending));
    setText("average-expense", currency(dashboard.average_expense));
    setText("risky-share", `${dashboard.risky_share.toFixed(0)}%`);
    setText("top-category", dashboard.top_category);
    renderHistory(dashboard.recent_transactions);
    renderCategoryChart(dashboard.category_breakdown);
    renderBalanceChart(dashboard.balance_timeline);
};

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    pendingPayload = Object.fromEntries(formData.entries());

    Object.keys(pendingPayload).forEach((key) => {
        if (["balance", "expense_amount", "monthly_needs", "savings_goal"].includes(key)) {
            pendingPayload[key] = Number(pendingPayload[key]);
        }
    });

    const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pendingPayload),
    });

    const data = await response.json();
    if (!response.ok) {
        setText("main-message", data.detail || "Unable to analyze transaction.");
        return;
    }

    saveButton.disabled = false;
    setText("risk-level", data.risk_level);
    setText("risk-score", `${data.risk_score}/100`);
    setText("remaining-balance", currency(data.remaining_balance));
    setText("main-message", data.message);
    setText("live-risk-badge", `${data.risk_level} risk · ${data.risk_score}/100`);
    setText("live-recommendation", data.recommendation);
    renderList("alerts-list", data.alerts, "No additional smart alerts.");
    renderList("impact-list", data.impact_messages, "No impact messages.");
});

saveButton.addEventListener("click", async () => {
    if (!pendingPayload) return;
    const response = await fetch("/api/transactions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pendingPayload),
    });
    if (response.ok) {
        saveButton.disabled = true;
        await fetchDashboard();
    }
});

resetButton.addEventListener("click", async () => {
    const response = await fetch("/api/transactions", { method: "DELETE" });
    if (response.ok) {
        pendingPayload = null;
        saveButton.disabled = true;
        setText("risk-level", "-");
        setText("risk-score", "-");
        setText("remaining-balance", "-");
        setText("main-message", "History reset. Run a fresh analysis.");
        setText("live-risk-badge", "Waiting for analysis");
        setText("live-recommendation", "Add a transaction to begin.");
        renderList("alerts-list", [], "No additional smart alerts.");
        renderList("impact-list", [], "No impact messages.");
        await fetchDashboard();
    }
});

fetchDashboard();
