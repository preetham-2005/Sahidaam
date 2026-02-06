// ================================
// Dashboard Initialization
// ================================
document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ Dashboard loaded");
    loadDashboardData();
    loadLivePrices();
    applySavedTheme();

    const priceForm = document.getElementById("priceForm");
    if (priceForm) {
        priceForm.addEventListener("submit", submitPrice);
    }
});

// ================================
// Load Dashboard Stats
// ================================
async function loadDashboardData() {
    try {
        const res = await fetch("/api/dashboard-data", {
            credentials: "include"
        });

        if (!res.ok) {
            window.location.href = "/login";
            return;
        }

        const data = await res.json();

        setText("itemsCount", data.items);
        setText("contributorsCount", data.contributors);
        setText("submissionsCount", data.submissions);
        setText("scoreValue", data.score);

        console.log("📊 Dashboard stats loaded", data);

    } catch (err) {
        console.error("Dashboard error:", err);
    }
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? 0;
}

// ================================
// Load Live Prices (FIXED ISSUE)
// ================================
async function loadLivePrices() {
    try {
        const res = await fetch("/api/live-prices", {
            credentials: "include"
        });

        if (!res.ok) return;

        const data = await res.json();
        const container = document.getElementById("pricesContainer");

        if (!container) return;

        if (!data.prices || data.prices.length === 0) {
            container.innerHTML =
                `<p class="empty-msg">No prices submitted yet for your village</p>`;
            return;
        }

        container.innerHTML = data.prices.map(p => `
            <div class="price-item">
                <strong>${p.item}</strong>
                <span>₹${p.price}</span>
                <small>Submitted just now</small>
            </div>
        `).join("");

        console.log("📊 Live prices loaded", data.prices);

    } catch (err) {
        console.error("Live prices error:", err);
    }
}

// ================================
// Submit Price
// ================================
async function submitPrice(e) {
    e.preventDefault();

    const itemInput = document.getElementById("itemInput");
    const priceInput = document.getElementById("priceInput");

    const item = itemInput.value.trim();
    const price = parseFloat(priceInput.value);

    if (!item || !price || price <= 0) {
        alert("Enter valid item and price");
        return;
    }

    try {
        const res = await fetch("/api/submit-price", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ item, price })
        });

        const data = await res.json();

        if (!res.ok) {
            alert(data.error || "Failed to submit price");
            return;
        }

        itemInput.value = "";
        priceInput.value = "";

        // Refresh dashboard + prices
        loadDashboardData();
        loadLivePrices();

    } catch (err) {
        console.error("Submit error:", err);
        alert("Network error");
    }
}

// ================================
// Logout
// ================================
async function logout() {
    try {
        await fetch("/api/logout", {
            method: "POST",
            credentials: "include"
        });
    } catch (e) {
        console.warn("Logout error:", e);
    } finally {
        window.location.href = "/login";
    }
}

// ================================
// Refresh Button
// ================================
function refreshData() {
    loadDashboardData();
    loadLivePrices();
}

// ================================
// Dark Mode
// ================================
function toggleTheme() {
    const isDark = document.body.classList.toggle("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");
}

function applySavedTheme() {
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark");
    }
}
