// ===================================================================
// SAHIDAAM DASHBOARD ENGINE v2.3
// Complete Suite: Ticker + Weather + Gamification + Deals + Map + Alerts + Slip
// ===================================================================

// Global State
let activeLeaderboardPeriod = "weekly";
let activeCategory = "All";
let cachedPrices = [];
let cachedUserVillage = "";
let cachedVillageAverages = {};
let trendsChartInstance = null;
let mandiMapInstance = null;
let cachedUserId = null;
let currentLanguage = localStorage.getItem("sahidaam_lang") || "en";
let currentPhotoBase64 = null;
let recognition = null;
let isRecording = false;

// ===================================================================
// 1. INDIC MULTILINGUAL TRANSLATIONS DICTIONARY
// ===================================================================
const i18n = {
    en: {
        tagline: "Village Market Intelligence",
        refresh: "Refresh",
        logout: "Logout",
        marketDashboard: "Market Dashboard",
        dashboardDesc: "Real-time crowdsourced rates, AI price advisory, and community verification.",
        shareWhatsApp: "Share Today's Rates on WhatsApp",
        itemsTracked: "📦 Items Tracked",
        contributors: "👥 Contributors",
        submissions: "📝 Submissions",
        trustScore: "🛡️ Trust Score",
        aiAdvisor: "AI Price Advisor",
        aiAdvisorDesc: "Best time to sell & 7-day forecast",
        submitPrice: "Submit Price",
        submitPriceDesc: "Voice input 🎙️ & photo receipts",
        liveFeed: "Live Feed",
        liveFeedDesc: "Community verified crop prices",
        marketTrends: "Price Trends",
        marketTrendsDesc: "Mandi graphs & village comparison",
        aiAdvisorTitle: "AI Smart Market Advisor & Price Forecast",
        loadingAi: "Analyzing local mandi data and calculating recommendations...",
        submitCropPrice: "Submit Daily Crop Price",
        voiceInput: "Speak to Auto-Fill (Voice)",
        listening: "Listening:",
        cropName: "🌾 Crop Name",
        category: "📁 Category",
        catGrains: "🌾 Grains & Pulses",
        catVeg: "🍅 Vegetables",
        catFruits: "🍎 Fruits",
        catDairy: "🥛 Dairy & Poultry",
        catOthers: "📦 Others",
        pricePerKg: "💰 Price (₹ per kg / quintal)",
        locationMandi: "📍 Purchase Location / Mandi",
        attachPhoto: "📸 Attach Crop Photo or Mandi Slip (Optional — +10 Trust Score)",
        choosePhoto: "Choose Photo / Receipt",
        removePhoto: "✕ Remove Photo",
        remarks: "💬 Remarks / Quality Notes (Optional)",
        submitPriceBtn: "Submit Price Details →",
        liveFeedTitle: "Live Village Market Feed",
        allCrops: "All Crops",
        noPrices: "No prices submitted yet. Be the first to share today's rates!",
        marketIntelligence: "Market Analytics & Multi-Village Comparison",
        priceTrendsTitle: "Local Price Trends (Average Rates)",
        villageGridTitle: "Surrounding Village Price Grid",
        thCrop: "Crop",
        thVillage: "Village",
        thAvgPrice: "Avg Price",
        thVsYours: "vs. Yours",
        noCompData: "Submit crop prices to see comparisons!",
        trustedContributors: "Top Trusted Contributors",
        weekly: "Weekly",
        monthly: "Monthly",
        global: "Global",
        noContributors: "No contributions yet",
        perKg: "per kg/unit",
        shareRate: "📲 Share Rate",
        verified: "Verified",
        disputed: "Disputed",
        yourPost: "Your Post",
        pendingVerif: "Pending Verification"
    },
    hi: {
        tagline: "ग्रामीण बाज़ार मूल्य सूचना",
        refresh: "ताज़ा करें",
        logout: "लॉग आउट",
        marketDashboard: "मंडी डैशबोर्ड",
        dashboardDesc: "सटीक स्थानीय फसल भाव, एआई बाज़ार सलाह और सामुदायिक सत्यापन।",
        shareWhatsApp: "व्हाट्सएप पर आज के भाव साझा करें",
        itemsTracked: "📦 कुल फसलें",
        contributors: "👥 योगदानकर्ता",
        submissions: "📝 कुल भाव प्रविष्टियां",
        trustScore: "🛡️ विश्वास स्कोर",
        aiAdvisor: "एआई मूल्य सलाहकार",
        aiAdvisorDesc: "फसल बेचने का सही समय और 7-दिन का अनुमान",
        submitPrice: "भाव दर्ज करें",
        submitPriceDesc: "आवाज़ से भरें 🎙️ और रसीद फोटो जोड़ें",
        liveFeed: "लाइव मंडी भाव",
        liveFeedDesc: "सत्यापित फसल मूल्य सूची",
        marketTrends: "भाव रुझान",
        marketTrendsDesc: "मंडी चार्ट और पड़ोसी गांव तुलना",
        aiAdvisorTitle: "एआई बाज़ार सलाहकार एवं मूल्य पूर्वानुमान",
        loadingAi: "मंडी डेटा का विश्लेषण और अनुशंसाएं तैयार की जा रही हैं...",
        submitCropPrice: "आज का फसल भाव दर्ज करें",
        voiceInput: "बोलकर दर्ज करें (वॉइस)",
        listening: "सुन रहे हैं:",
        cropName: "🌾 फसल का नाम",
        category: "📁 श्रेणी",
        catGrains: "🌾 अनाज एवं दालें",
        catVeg: "🍅 सब्जियां",
        catFruits: "🍎 फल",
        catDairy: "🥛 डेयरी एवं पोल्ट्री",
        catOthers: "📦 अन्य",
        pricePerKg: "💰 भाव (₹ प्रति किलो / क्विंटल)",
        locationMandi: "📍 खरीद स्थान / मंडी",
        attachPhoto: "📸 फसल फोटो या मंडी पर्ची जोड़ें (वैकल्पिक — +10 विश्वास अंक)",
        choosePhoto: "फोटो / रसीद चुनें",
        removePhoto: "✕ फोटो हटाएं",
        remarks: "💬 विवरण / गुणवत्ता टिप्पणी",
        submitPriceBtn: "भाव विवरण सबमिट करें →",
        liveFeedTitle: "गाँव की लाइव मंडी फीड",
        allCrops: "सभी फसलें",
        noPrices: "अभी तक कोई भाव दर्ज नहीं है। आज का भाव सबसे पहले साझा करें!",
        marketIntelligence: "बाज़ार विश्लेषण एवं ग्रामीण तुलना",
        priceTrendsTitle: "स्थानीय मूल्य रुझान (औसत दरें)",
        villageGridTitle: "आस-पास के गांवों के भाव",
        thCrop: "फसल",
        thVillage: "गांव / मंडी",
        thAvgPrice: "औसत भाव",
        thVsYours: "तुलना",
        noCompData: "तुलना देखने के लिए फसल मूल्य दर्ज करें!",
        trustedContributors: "शीर्ष विश्वसनीय योगदानकर्ता",
        weekly: "साप्ताहिक",
        monthly: "मासिक",
        global: "वैश्विक",
        noContributors: "अभी कोई योगदानकर्ता नहीं है",
        perKg: "प्रति किलो",
        shareRate: "📲 भाव साझा करें",
        verified: "सत्यापित",
        disputed: "विवादित",
        yourPost: "आपकी पोस्ट",
        pendingVerif: "सत्यापन लंबित"
    },
    te: {
        tagline: "గ్రామీణ మార్కెట్ ధరల సమాచారం",
        refresh: "తాజాకరించు",
        logout: "లాగ్ అవుట్",
        marketDashboard: "మార్కెట్ డాష్‌బోర్డ్",
        dashboardDesc: "నిజ సమయ పంట ధరలు, AI సలహాలు మరియు గ్రామ కమ్యూనిటీ రేట్లు.",
        shareWhatsApp: "నేటి ధరలను వాట్సాప్‌లో పంపండి",
        itemsTracked: "📦 పంటలు",
        contributors: "👥 రైతులు",
        submissions: "📝 ధరల ఎంట్రీలు",
        trustScore: "🛡️ నమ్మక స్కోరు",
        aiAdvisor: "AI మార్కెట్ అడ్వైజర్",
        aiAdvisorDesc: "అమ్మేందుకు సరైన సమయం & 7 రోజుల అంచనా",
        submitPrice: "ధరను నమోదు చేయండి",
        submitPriceDesc: "వాయిస్ ఇన్పుట్ 🎙️ & రసీదు ఫోటో",
        liveFeed: "లైవ్ ధరలు",
        liveFeedDesc: "ధృవీకరించబడిన గ్రామ మార్కెట్ రేట్లు",
        marketTrends: "ధరల ట్రెండ్స్",
        marketTrendsDesc: "మార్కెట్ గ్రాఫ్‌లు & గ్రామ పోలిక",
        aiAdvisorTitle: "AI స్మార్ట్ మార్కెట్ సలహా & ధరల అంచనా",
        loadingAi: "మార్కెట్ డేటాను విశ్లేషిస్తోంది...",
        submitCropPrice: "నేటి పంట ధరను నమోదు చేయండి",
        voiceInput: "మాట్లాడి నమోదు చేయండి (Voice)",
        listening: "వింటోంది:",
        cropName: "🌾 పంట పేరు",
        category: "📁 వర్గం",
        catGrains: "🌾 ధాన్యాలు & పప్పులు",
        catVeg: "🍅 కూరగాయలు",
        catFruits: "🍎 పండ్లు",
        catDairy: "🥛 డైరీ & పౌల్ట్రీ",
        catOthers: "📦 ఇతరాలు",
        pricePerKg: "💰 ధర (₹ కిలోకి / క్వింటాల్‌కు)",
        locationMandi: "📍 కొనుగోలు ప్రదేశం / మార్కెట్",
        attachPhoto: "📸 పంట ఫోటో లేదా మార్కెట్ రసీదు (ఐచ్ఛికం — +10 స్కోర్)",
        choosePhoto: "ఫోటో / రసీదును ఎంచుకోండి",
        removePhoto: "✕ ఫోటో తీసివేయండి",
        remarks: "💬 నాణ్యత గమనికలు",
        submitPriceBtn: "ధర వివరాలను సమర్పించండి →",
        liveFeedTitle: "లైవ్ విలేజ్ మార్కెట్ ఫీడ్",
        allCrops: "అన్ని పంటలు",
        noPrices: "ఇంకా ధరలు నమోదు కాలేదు. నేటి ధరను మొదటగా నమోదు చేయండి!",
        marketIntelligence: "మార్కెట్ విశ్లేషణ & గ్రామాల పోలిక",
        priceTrendsTitle: "స్థానిక ధరల సరళి (సగటు రేట్లు)",
        villageGridTitle: "చుట్టుపక్కల గ్రామాల ధరల పట్టిక",
        thCrop: "పంట",
        thVillage: "గ్రామం / మండీ",
        thAvgPrice: "సగటు ధర",
        thVsYours: "పోలిక",
        noCompData: "పోలిక చూడటానికి పంట ధరలను సమర్పించండి!",
        trustedContributors: "టాప్ విశ్వసనీయ రైతులు",
        weekly: "వారపు",
        monthly: "నెలవారీ",
        global: "మొత్తం",
        noContributors: "ఇంకా ఎంట్రీలు లేవు",
        perKg: "కిలోకి",
        shareRate: "📲 ధర షేర్ చేయండి",
        verified: "ధృవీకరించబడింది",
        disputed: "వివాదాస్పదం",
        yourPost: "మీ పోస్ట్",
        pendingVerif: "ధృవీకరణ పెండింగ్‌లో ఉంది"
    }
};

function changeLanguage(lang) {
    if (!i18n[lang]) lang = "en";
    currentLanguage = lang;
    localStorage.setItem("sahidaam_lang", lang);

    const select = document.getElementById("langSelect");
    if (select) select.value = lang;

    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (i18n[lang][key]) {
            el.textContent = i18n[lang][key];
        }
    });

    renderPricesList();
    loadAiAdvisory();
}

// ===================================================================
// 2. DASHBOARD INITIALIZATION
// ===================================================================
document.addEventListener("DOMContentLoaded", () => {
    console.log("🌾 SahiDaam v2.3 Engine Initialized");
    applySavedTheme();
    changeLanguage(currentLanguage);

    loadMarketTicker();
    loadWeatherWidget();
    loadGamification();
    loadDashboardData();
    loadDeals();
    loadLivePrices();
    loadAiAdvisory();
    loadMandiMap();
    loadAlerts();
    loadLeaderboard(activeLeaderboardPeriod);
    loadAnalytics();

    const priceForm = document.getElementById("priceForm");
    if (priceForm) {
        priceForm.removeEventListener("submit", submitPrice);
        priceForm.addEventListener("submit", submitPrice);
    }
});

// ===================================================================
// 3. LIVE MARKET TICKER
// ===================================================================
async function loadMarketTicker() {
    try {
        const res = await fetch("/api/market-ticker");
        if (!res.ok) return;
        const data = await res.json();
        const tickerItems = data.ticker || [];

        if (tickerItems.length === 0) return;

        const track = document.getElementById("tickerTrack");
        if (!track) return;

        const html = tickerItems.map(t => {
            const pillClass = t.is_up ? "ticker-pill-up" : "ticker-pill-down";
            const sign = t.is_up ? `▲ +${t.change}%` : `▼ ${t.change}%`;
            return `
                <div class="ticker-item">
                    <span>🌾 ${t.crop}: ₹${t.price.toFixed(2)}/kg</span>
                    <span class="${pillClass}">${sign}</span>
                    <span style="color:var(--text-3);font-size:0.75rem;">(${t.village})</span>
                </div>
            `;
        }).join("");

        // Double track for continuous smooth marquee
        track.innerHTML = html + html;
    } catch (e) {
        console.log("Ticker load notice:", e);
    }
}

// ===================================================================
// 4. HYPERLOCAL WEATHER WIDGET
// ===================================================================
async function loadWeatherWidget() {
    try {
        const res = await fetch("/api/weather", { credentials: "include" });
        if (!res.ok) return;
        const w = await res.json();

        setText("weatherTemp", w.temperature);
        setText("weatherCond", w.condition);
        setText("weatherVillage", w.village);
        setText("weatherHumidity", w.humidity);
        setText("weatherWind", w.wind);

        const advisoryEl = document.getElementById("weatherAdvisory");
        if (advisoryEl) {
            advisoryEl.innerHTML = `🌾 <strong>Agri-Advisory (${w.village}):</strong> ${w.advisory}`;
        }
    } catch (e) {
        console.log("Weather notice:", e);
    }
}

// ===================================================================
// 5. GAMIFICATION & XP PROGRESS
// ===================================================================
async function loadGamification() {
    try {
        const res = await fetch("/api/user-gamification", { credentials: "include" });
        if (!res.ok) return;
        const g = await res.json();

        const titleEl = document.getElementById("farmerLevelTitle");
        if (titleEl) titleEl.textContent = `Level ${g.level} · ${g.title}`;

        const xpTotalEl = document.getElementById("farmerXpTotal");
        if (xpTotalEl) xpTotalEl.textContent = `${g.xp} Total XP`;

        const xpProgressText = document.getElementById("xpProgressText");
        if (xpProgressText) xpProgressText.textContent = `${g.xp_in_level} / ${g.next_level_xp} XP to Level ${g.level + 1}`;

        const xpBarFill = document.getElementById("xpBarFill");
        if (xpBarFill) xpBarFill.style.width = `${Math.min(100, g.progress_pct)}%`;

        const badgesRow = document.getElementById("farmerBadgesRow");
        if (badgesRow && g.badges) {
            badgesRow.innerHTML = g.badges.map(b => `
                <span class="badge-pill ${b.unlocked ? 'active' : ''}" title="${b.desc}">
                    ${b.icon} ${b.name}
                </span>
            `).join("");
        }
    } catch (e) {
        console.log("Gamification notice:", e);
    }
}

// ===================================================================
// 6. KISAN DEAL BOARD (MARKETPLACE)
// ===================================================================
async function loadDeals() {
    const container = document.getElementById("dealsContainer");
    if (!container) return;

    try {
        const res = await fetch("/api/deals", { credentials: "include" });
        if (!res.ok) return;
        const data = await res.json();
        const deals = data.deals || [];

        if (deals.length === 0) {
            container.innerHTML = `<p class="empty-msg">No active harvest listings yet. Be the first farmer to list your harvest!</p>`;
            return;
        }

        container.innerHTML = deals.map(d => {
            const rawPhone = (d.whatsapp_number || d.contact_phone || "8639682415").replace(/\D/g, '');
            const cleanPhone = rawPhone.length === 10 ? `91${rawPhone}` : (rawPhone.length > 10 ? rawPhone : USER_WHATSAPP_NUMBER);
            const waMsg = encodeURIComponent(`Hello ${d.seller_name}, I saw your listing for ${d.quantity} of ${d.crop_name} on SahiDaam Kisan Deal Board. Is this lot still available?`);
            const waUrl = `https://api.whatsapp.com/send?phone=${cleanPhone}&text=${waMsg}`;
            const callUrl = `tel:${d.contact_phone || '8639682415'}`;

            return `
                <div class="deal-card">
                    <div>
                        <div class="deal-header">
                            <span class="deal-crop">${d.crop_name}</span>
                            <span class="deal-qty-badge">${d.quantity}</span>
                        </div>
                        <div class="deal-price-val">₹${d.price_per_unit.toFixed(2)}</div>
                        <div class="deal-seller-info">
                            👤 <strong>${d.seller_name}</strong> (🛡️ ${d.seller_trust}% Trust) · 📍 ${d.village}
                            ${d.location_details ? `<br><small>🚩 ${d.location_details}</small>` : ''}
                        </div>
                        ${d.description ? `<p style="font-size:0.8rem;color:var(--text-2);margin-bottom:8px;">"${d.description}"</p>` : ''}
                    </div>
                    <div class="deal-actions">
                        <a href="${waUrl}" target="_blank" class="btn-whatsapp-deal">
                            <span>💬</span> <span>WhatsApp</span>
                        </a>
                        <a href="${callUrl}" class="btn-call-deal">
                            <span>📞</span> <span>Call</span>
                        </a>
                    </div>
                </div>
            `;
        }).join("");
    } catch (e) {
        console.log("Deals load error:", e);
    }
}

function openCreateDealModal() {
    document.getElementById("createDealModal").classList.add("active");
}
function closeCreateDealModal() {
    document.getElementById("createDealModal").classList.remove("active");
}

async function handleCreateDealSubmit(e) {
    e.preventDefault();
    const crop_name = document.getElementById("dealCrop").value.trim();
    const quantity = document.getElementById("dealQuantity").value.trim();
    const price_per_unit = document.getElementById("dealPrice").value;
    const contact_phone = document.getElementById("dealPhone").value.trim();
    const location_details = document.getElementById("dealLocation").value.trim();

    try {
        const res = await fetch("/api/deals/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ crop_name, quantity, price_per_unit, contact_phone, location_details })
        });
        const data = await res.json();

        if (!res.ok) {
            showError(data.error || "Failed to post harvest deal");
            return;
        }

        showSuccess("🎉 Harvest lot listed on Kisan Deal Board!");
        closeCreateDealModal();
        document.getElementById("createDealForm").reset();
        loadDeals();
        loadGamification();
    } catch (err) {
        showError("Network error listing deal");
    }
}

// ===================================================================
// 7. INTERACTIVE MANDI GPS MAP (LEAFLET)
// ===================================================================
async function loadMandiMap() {
    const mapContainer = document.getElementById("mandiMap");
    if (!mapContainer || !window.L) return;

    try {
        const res = await fetch("/api/mandi-map", { credentials: "include" });
        if (!res.ok) return;
        const data = await res.json();
        const mandis = data.mandis || [];

        if (mandiMapInstance) {
            mandiMapInstance.remove();
        }

        const centerLat = data.center_lat || 17.485;
        const centerLng = data.center_lng || 78.490;

        mandiMapInstance = L.map('mandiMap').setView([centerLat, centerLng], 10);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(mandiMapInstance);

        mandis.forEach(m => {
            const isOur = m.is_current;
            const markerColor = isOur ? '#00c896' : (m.avg_price > 35 ? '#34d399' : '#3b82f6');
            
            const customIcon = L.divIcon({
                className: 'custom-mandi-pin',
                html: `<div style="background:${markerColor};color:#fff;padding:4px 8px;border-radius:12px;font-weight:800;font-size:11px;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.4);white-space:nowrap;">🌾 ₹${m.avg_price}</div>`,
                iconSize: [60, 24],
                iconAnchor: [30, 12]
            });

            const marker = L.marker([m.lat, m.lng], { icon: customIcon }).addTo(mandiMapInstance);
            
            const popupContent = `
                <div style="font-family:'Plus Jakarta Sans',sans-serif;padding:4px;">
                    <strong style="font-size:14px;color:#0f172a;">📍 ${m.name}</strong><br>
                    <span style="font-size:12px;color:#475569;">Distance: <strong>${m.distance_km} km</strong></span><br>
                    <span style="font-size:12px;color:#059669;font-weight:700;">Avg Crop Rate: ₹${m.avg_price}/kg</span><br>
                    <small style="color:#64748b;">${m.reports_count} verified price reports</small>
                </div>
            `;
            marker.bindPopup(popupContent);
        });

    } catch (e) {
        console.log("Mandi map notice:", e);
    }
}

// ===================================================================
// 8. SMART PRICE ALERTS
// ===================================================================
async function loadAlerts() {
    const container = document.getElementById("alertsContainer");
    if (!container) return;

    try {
        const res = await fetch("/api/alerts", { credentials: "include" });
        if (!res.ok) return;
        const data = await res.json();
        const alerts = data.alerts || [];

        if (alerts.length === 0) {
            container.innerHTML = `<p class="empty-msg">No active price alerts set. Click 'Set Price Alert' to watch a crop.</p>`;
            return;
        }

        container.innerHTML = alerts.map(a => `
            <div class="alert-item-card">
                <div>
                    <strong>🌾 ${a.crop_name}</strong>
                    <span style="font-size:0.82rem;color:var(--text-3);margin-left:8px;">
                        Trigger when price is <strong>${a.condition.toUpperCase()}</strong> <span style="color:var(--emerald);font-weight:800;">₹${a.target_price.toFixed(2)}</span>
                    </span>
                </div>
                <button type="button" class="btn-text" onclick="deleteAlert(${a.id})" style="color:var(--danger);font-size:0.8rem;">
                    ✕ Remove
                </button>
            </div>
        `).join("");
    } catch (e) {
        console.log("Alerts load error:", e);
    }
}

function openCreateAlertModal() {
    document.getElementById("createAlertModal").classList.add("active");
}
function closeCreateAlertModal() {
    document.getElementById("createAlertModal").classList.remove("active");
}

async function handleCreateAlertSubmit(e) {
    e.preventDefault();
    const crop_name = document.getElementById("alertCrop").value.trim();
    const target_price = document.getElementById("alertPrice").value;
    const condition = document.getElementById("alertCondition").value;

    try {
        const res = await fetch("/api/alerts/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ crop_name, target_price, condition })
        });
        const data = await res.json();

        if (!res.ok) {
            showError(data.error || "Failed to set alert");
            return;
        }

        showSuccess(data.message || "Price alert activated!");
        closeCreateAlertModal();
        document.getElementById("createAlertForm").reset();
        loadAlerts();
    } catch (err) {
        showError("Network error creating alert");
    }
}

async function deleteAlert(alertId) {
    try {
        await fetch(`/api/alerts/delete/${alertId}`, { method: "POST", credentials: "include" });
        showSuccess("Alert removed");
        loadAlerts();
    } catch (e) {
        showError("Failed to remove alert");
    }
}

// ===================================================================
// 9. OFFICIAL MANDI PRICE SLIP GENERATOR
// ===================================================================
function openMandiSlipModal() {
    const modal = document.getElementById("mandiSlipModal");
    const villageNameEl = document.getElementById("slipVillageName");
    const dateEl = document.getElementById("slipDateStr");
    const tableBody = document.getElementById("slipTableBody");

    const todayStr = new Date().toLocaleDateString([], { day: 'numeric', month: 'long', year: 'numeric' });
    if (villageNameEl) villageNameEl.textContent = `${(cachedUserVillage || 'LOCAL').toUpperCase()} AGRICULTURE MARKET YARD`;
    if (dateEl) dateEl.textContent = `Date: ${todayStr}`;

    if (tableBody && cachedPrices.length > 0) {
        tableBody.innerHTML = cachedPrices.slice(0, 8).map(p => `
            <tr>
                <td><strong>${p.item}</strong></td>
                <td>${p.category || 'General'}</td>
                <td style="font-weight:700;color:#047857;">₹${p.price.toFixed(2)}/kg</td>
                <td>${p.upvotes > 0 ? 'Verified ✓' : 'Recorded'}</td>
            </tr>
        `).join("");
    }

    modal.classList.add("active");
}

function closeMandiSlipModal() {
    document.getElementById("mandiSlipModal").classList.remove("active");
}

// ===================================================================
// 10. AI MARKET ADVISORY & 7-DAY FORECAST
// ===================================================================
async function loadAiAdvisory() {
    const container = document.getElementById("aiAdvisoryContainer");
    if (!container) return;

    try {
        const res = await fetch("/api/ai-advisory", { credentials: "include" });
        if (!res.ok) return;

        const data = await res.json();
        const advisories = data.advisories || [];

        if (advisories.length === 0) {
            container.innerHTML = `
                <div class="ai-card" style="grid-column: 1 / -1; text-align:center; padding: 28px;">
                    <p style="color:var(--text-2);font-size:0.95rem;">
                        🌾 <strong>AI Advisory Ready:</strong> Submit your village's first crop prices below to activate live sell/hold predictions & neighboring mandi comparisons!
                    </p>
                </div>
            `;
            return;
        }

        container.innerHTML = advisories.map(adv => {
            let badgeClass = "ai-badge-neutral";
            let badgeIcon = "ℹ️";
            if (adv.action_code === "sell") {
                badgeClass = "ai-badge-sell";
                badgeIcon = "📈 SELL NOW";
            } else if (adv.action_code === "hold") {
                badgeClass = "ai-badge-hold";
                badgeIcon = "⏳ HOLD / STORE";
            } else {
                badgeIcon = "⚖️ STABLE";
            }

            const trendSign = adv.trend_pct >= 0 ? `+${adv.trend_pct}%` : `${adv.trend_pct}%`;
            const trendColor = adv.trend_pct >= 0 ? "var(--emerald)" : "var(--danger)";

            return `
                <div class="ai-card">
                    <div class="ai-card-header">
                        <span class="ai-crop-name">${adv.crop}</span>
                        <span class="ai-badge ${badgeClass}">${badgeIcon}</span>
                    </div>
                    <div class="ai-stat-row">
                        <span class="ai-stat-label">Current Rate:</span>
                        <span class="ai-stat-val" style="color:var(--emerald);font-size:1.1rem;">₹${adv.current_price.toFixed(2)}</span>
                    </div>
                    <div class="ai-stat-row">
                        <span class="ai-stat-label">7-Day Momentum:</span>
                        <span class="ai-stat-val" style="color:${trendColor};">${trendSign}</span>
                    </div>
                    <div class="ai-stat-row">
                        <span class="ai-stat-label">Expected Range (7d):</span>
                        <span class="ai-stat-val">${adv.forecast_7d}</span>
                    </div>
                    <div class="ai-stat-row">
                        <span class="ai-stat-label">Top Mandi:</span>
                        <span class="ai-stat-val" style="color:var(--amber);">📍 ${adv.best_mandi} (₹${adv.best_mandi_price})</span>
                    </div>
                    <div class="ai-tip-box">
                        💡 ${adv.tip}
                    </div>
                </div>
            `;
        }).join("");

    } catch (err) {
        console.error("AI Advisory error:", err);
    }
}

// ===================================================================
// 11. SPEECH-TO-TEXT VOICE INPUT
// ===================================================================
function toggleVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Voice recognition is not supported on this browser. Please use Google Chrome, Edge, or Android browser.");
        return;
    }

    const voiceBtn = document.getElementById("voiceBtn");
    const voiceText = document.getElementById("voiceBtnText");
    const transcriptBanner = document.getElementById("voiceTranscript");
    const transcriptText = document.getElementById("transcriptText");

    if (isRecording) {
        if (recognition) recognition.stop();
        isRecording = false;
        voiceBtn.classList.remove("listening");
        voiceText.textContent = "Speak to Auto-Fill (Voice)";
        transcriptBanner.style.display = "none";
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;

    if (currentLanguage === "hi") recognition.lang = "hi-IN";
    else if (currentLanguage === "te") recognition.lang = "te-IN";
    else recognition.lang = "en-IN";

    recognition.onstart = () => {
        isRecording = true;
        voiceBtn.classList.add("listening");
        voiceText.textContent = "Listening... Speak now";
        transcriptBanner.style.display = "block";
        transcriptText.textContent = "Speak crop name, price, and mandi (e.g. 'Tomato 30 rupees Rampur')...";
    };

    recognition.onresult = (event) => {
        const text = Array.from(event.results).map(r => r[0].transcript).join(" ");
        transcriptText.textContent = `"${text}"`;
        parseVoiceInput(text);
    };

    recognition.onerror = (event) => {
        console.warn("Voice error:", event.error);
        voiceBtn.classList.remove("listening");
        voiceText.textContent = "Speak to Auto-Fill (Voice)";
        isRecording = false;
        transcriptBanner.style.display = "none";
    };

    recognition.onend = () => {
        voiceBtn.classList.remove("listening");
        voiceText.textContent = "Speak to Auto-Fill (Voice)";
        isRecording = false;
        setTimeout(() => { transcriptBanner.style.display = "none"; }, 3000);
    };

    recognition.start();
}

function parseVoiceInput(spokenText) {
    const text = spokenText.toLowerCase();

    const priceMatch = text.match(/(\d+(\.\d+)?)/);
    if (priceMatch) {
        const priceInput = document.getElementById("priceInput");
        if (priceInput) priceInput.value = priceMatch[1];
    }

    const cropDict = {
        "Tomato": ["tomato", "टमाटर", "టమాట", "tamatar", "tamato"],
        "Rice": ["rice", "चावल", "వరి", "dhan", "chawal", "paddy", "biyyam"],
        "Wheat": ["wheat", "गेहूं", "గోధుమలు", "gehu", "godhumalu"],
        "Onion": ["onion", "प्याज", "ఉల్లిపాయ", "pyaz", "kanda", "ullipaya"],
        "Potato": ["potato", "आलू", "బంగాళాదుంప", "aaloo", "aloo", "bangaladumpa"],
        "Cotton": ["cotton", "कपास", "పత్తి", "kapas", "patti"],
        "Chilli": ["chilli", "chili", "मिर्च", "మిర్చి", "mirch", "mirchi"],
        "Corn / Maize": ["corn", "maize", "मक्का", "మొక్కజొన్న", "makka", "mokkajonna"],
        "Milk": ["milk", "दूध", "పాలు", "doodh", "dudh", "paalu"],
        "Mango": ["mango", "आम", "మామిడి", "aam", "mamidi"]
    };

    let detectedCrop = "";
    for (const [canonical, aliases] of Object.entries(cropDict)) {
        if (aliases.some(alias => text.includes(alias))) {
            detectedCrop = canonical;
            break;
        }
    }

    if (detectedCrop) {
        const itemInput = document.getElementById("itemInput");
        if (itemInput) itemInput.value = detectedCrop;

        const catSelect = document.getElementById("categoryInput");
        if (catSelect) {
            if (["Tomato", "Onion", "Potato", "Chilli"].includes(detectedCrop)) catSelect.value = "Vegetables";
            else if (["Rice", "Wheat", "Corn / Maize"].includes(detectedCrop)) catSelect.value = "Grains";
            else if (["Mango"].includes(detectedCrop)) catSelect.value = "Fruits";
            else if (["Milk"].includes(detectedCrop)) catSelect.value = "Dairy";
        }
    }

    if (text.includes("mandi") || text.includes("मंडी") || text.includes("మార్కెట్")) {
        const locationInput = document.getElementById("locationInput");
        if (locationInput && !locationInput.value) {
            locationInput.value = cachedUserVillage ? `${cachedUserVillage} Mandi` : "Local Mandi";
        }
    }
}

// ===================================================================
// 12. CROP PHOTO UPLOAD
// ===================================================================
function handlePhotoSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
        showError("Photo size must be under 5MB");
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        currentPhotoBase64 = e.target.result;
        const preview = document.getElementById("photoPreview");
        const clearBtn = document.getElementById("clearPhotoBtn");
        const labelText = document.getElementById("uploadLabelText");

        preview.src = currentPhotoBase64;
        preview.style.display = "block";
        clearBtn.style.display = "inline-block";
        labelText.textContent = "Photo Attached ✓";
    };
    reader.readAsDataURL(file);
}

function clearPhoto() {
    currentPhotoBase64 = null;
    document.getElementById("photoInput").value = "";
    document.getElementById("photoPreview").style.display = "none";
    document.getElementById("clearPhotoBtn").style.display = "none";
    document.getElementById("uploadLabelText").textContent = "Choose Photo / Receipt";
}

function openPhotoModal(imgSrc) {
    const modal = document.getElementById("photoModal");
    const modalImg = document.getElementById("photoModalImg");
    modalImg.src = imgSrc;
    modal.classList.add("active");
}

function closePhotoModal() {
    document.getElementById("photoModal").classList.remove("active");
}

// ===================================================================
// 13. WHATSAPP REDIRECT & SHARING (Target: 8639682415)
// ===================================================================
const USER_WHATSAPP_NUMBER = "918639682415";

function shareMarketSummaryWhatsApp() {
    if (cachedPrices.length === 0) {
        alert("No market prices to share yet. Submit a price first!");
        return;
    }

    const todayStr = new Date().toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' });
    let text = `🌾 *SahiDaam — Daily Market Rates*\n📍 *Village/Mandi:* ${cachedUserVillage || 'Local Mandi'}\n📅 *Date:* ${todayStr}\n\n`;

    const topPrices = cachedPrices.slice(0, 6);
    topPrices.forEach(p => {
        text += `• *${p.item}:* ₹${p.price.toFixed(2)}/kg ${p.purchase_location ? `(📍 ${p.purchase_location})` : ''}\n`;
    });

    text += `\n🔍 *Check live village prices & verify rates:* \n${window.location.origin}/dashboard\n\n_Empowering farmers with transparent prices._`;

    const whatsappUrl = `https://api.whatsapp.com/send?phone=${USER_WHATSAPP_NUMBER}&text=${encodeURIComponent(text)}`;
    window.open(whatsappUrl, '_blank');
}

function shareIndividualRateWhatsApp(item, price, mandi, submitter) {
    const todayStr = new Date().toLocaleDateString([], { day: 'numeric', month: 'short' });
    const text = `🌾 *SahiDaam Verified Rate*\n\n🌾 *Crop:* ${item}\n💰 *Price:* ₹${price.toFixed(2)} per kg/unit\n📍 *Mandi:* ${mandi || cachedUserVillage}\n👤 *Reported by:* ${submitter} on ${todayStr}\n\nCheck live rates: ${window.location.origin}/dashboard`;
    const whatsappUrl = `https://api.whatsapp.com/send?phone=${USER_WHATSAPP_NUMBER}&text=${encodeURIComponent(text)}`;
    window.open(whatsappUrl, '_blank');
}

// ===================================================================
// 14. LOAD LIVE PRICES & SUBMIT
// ===================================================================
async function loadDashboardData() {
    try {
        const res = await fetch("/api/dashboard-data", { credentials: "include" });
        if (!res.ok) {
            window.location.href = "/login";
            return;
        }

        const data = await res.json();
        setText("itemsCount", data.items);
        setText("contributorsCount", data.contributors);
        setText("submissionsCount", data.submissions);
        setText("scoreValue", data.score);

        if (data.user) {
            cachedUserId = data.user.id;
            cachedUserVillage = data.user.village;
            const welcomeMsg = document.getElementById("welcomeMsg");
            if (welcomeMsg) {
                const greeting = currentLanguage === 'hi' ? 'नमस्ते' : (currentLanguage === 'te' ? 'నమస్కారం' : 'Welcome');
                welcomeMsg.innerHTML = `${greeting} <strong>${data.user.name}</strong>! 🌾 <strong>${data.user.village}</strong>`;
            }
            renderPricesList();
        }
    } catch (err) {
        console.error("Dashboard stats error:", err);
    }
}

async function loadLivePrices() {
    try {
        const res = await fetch("/api/live-prices", { credentials: "include" });
        if (!res.ok) return;

        const data = await res.json();
        cachedPrices = data.prices || [];

        cachedVillageAverages = {};
        const sums = {};
        const counts = {};
        cachedPrices.forEach(p => {
            const crop = p.item.toLowerCase();
            sums[crop] = (sums[crop] || 0) + p.price;
            counts[crop] = (counts[crop] || 0) + 1;
        });
        Object.keys(sums).forEach(crop => {
            cachedVillageAverages[crop] = sums[crop] / counts[crop];
        });

        renderPricesList();
    } catch (err) {
        console.error("Live prices load error:", err);
    }
}

function renderPricesList() {
    const container = document.getElementById("pricesContainer");
    if (!container) return;

    let filtered = cachedPrices;
    if (activeCategory !== "All") {
        filtered = cachedPrices.filter(p => p.category === activeCategory);
    }

    if (filtered.length === 0) {
        const noPricesText = i18n[currentLanguage]?.noPrices || "No submissions found in this category";
        container.innerHTML = `<p class="empty-msg">${noPricesText}</p>`;
        return;
    }

    const t = i18n[currentLanguage] || i18n.en;

    container.innerHTML = filtered.map(p => {
        const date = new Date(p.created_at);
        const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const dateStr = date.toLocaleDateString([], { day: 'numeric', month: 'short' });

        const votesDiff = p.upvotes - p.downvotes;
        const isOwnSubmission = p.user_id === cachedUserId;

        let voteText = t.pendingVerif;
        let voteClass = "vote-neutral";
        if (votesDiff > 0) { voteText = `✅ ${t.verified} (+${votesDiff})`; voteClass = "vote-positive"; }
        else if (votesDiff < 0) { voteText = `⚠️ ${t.disputed} (${votesDiff})`; voteClass = "vote-negative"; }
        if (isOwnSubmission) voteText += ` · ${t.yourPost}`;

        const trustPercent = p.trust_score || 0;
        let trustColor = "comp-neutral";
        let trustLabel = "Contributor";
        if (trustPercent >= 85) { trustColor = "vote-positive"; trustLabel = "Highly Trusted"; }
        else if (trustPercent >= 60) { trustColor = ""; trustLabel = "Trusted"; }

        const locationTag = p.purchase_location
            ? `<span class="meta-tag">📍 ${p.purchase_location}</span>` : "";
        const categoryTag = p.category
            ? `<span class="meta-tag">${p.category}</span>` : "";
        const commentHtml = p.comment
            ? `<div class="price-comment">💬 "${p.comment}"</div>` : "";

        const photoThumbHtml = p.image_url
            ? `<img src="${p.image_url}" class="price-card-photo-thumb" onclick="openPhotoModal('${p.image_url}')" title="Click to view full photo" alt="Proof">`
            : "";

        const photoBadge = p.image_url
            ? `<span class="meta-tag" style="background:rgba(0,200,150,0.15);color:var(--emerald-bright);border-color:var(--emerald);">📸 Photo Verified</span>`
            : "";

        const upBtn = isOwnSubmission
            ? `<button class="vote-btn" disabled title="Cannot vote on own post">👍 ${p.upvotes}</button>`
            : `<button class="vote-btn" onclick="votePrice(${p.id}, 'upvote')" title="Verify accurate">👍 ${p.upvotes}</button>`;
        const downBtn = isOwnSubmission
            ? `<button class="vote-btn down" disabled title="Cannot vote on own post">👎 ${p.downvotes}</button>`
            : `<button class="vote-btn down" onclick="votePrice(${p.id}, 'downvote')" title="Dispute incorrect">👎 ${p.downvotes}</button>`;

        const whatsappBtn = `<button class="btn-whatsapp" onclick="shareIndividualRateWhatsApp('${p.item}', ${p.price}, '${p.purchase_location || ''}', '${p.name}')">${t.shareRate}</button>`;

        return `
        <div class="price-card">
            <div class="price-card-header">
                <div class="price-item-info">
                    <div class="price-item-name">${p.item}</div>
                    <div class="price-item-category">By <strong>${p.name}</strong> @${p.username} · ${dateStr} ${timeStr}</div>
                </div>
                <div style="display:flex;align-items:center;gap:12px;">
                    ${photoThumbHtml}
                    <div>
                        <div class="price-amount">₹${p.price.toFixed(2)}</div>
                        <div class="price-unit">${t.perKg}</div>
                    </div>
                </div>
            </div>
            <div class="price-card-meta">
                ${categoryTag}${locationTag}${photoBadge}
                <span class="meta-tag trust-badge" style="color:${trustPercent>=85?'#34d399':'#94a3b8'}">🛡️ ${trustPercent}% ${trustLabel}</span>
            </div>
            ${commentHtml}
            <div class="price-card-footer">
                <span class="vote-status ${voteClass}">${voteText}</span>
                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                    ${whatsappBtn}
                    <div class="vote-actions">${upBtn}${downBtn}</div>
                </div>
            </div>
        </div>`;
    }).join("");
}

function filterPrices(category) {
    activeCategory = category;
    const filterButtons = document.querySelectorAll(".filter-btn");
    filterButtons.forEach(btn => {
        if (btn.textContent.includes(category) || (category === "All" && btn.getAttribute("data-i18n") === "allCrops")) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });
    renderPricesList();
}

async function submitPrice(e) {
    e.preventDefault();

    const itemInput = document.getElementById("itemInput");
    const categoryInput = document.getElementById("categoryInput");
    const priceInput = document.getElementById("priceInput");
    const locationInput = document.getElementById("locationInput");
    const commentInput = document.getElementById("commentInput");
    const submitBtn = document.getElementById("submitBtn");

    const item = itemInput.value.trim();
    const category = categoryInput.value;
    const price = parseFloat(priceInput.value);
    const purchase_location = locationInput ? locationInput.value.trim() : "";
    const comment = commentInput ? commentInput.value.trim() : "";

    if (!item || isNaN(price) || price <= 0) {
        showError("Please enter a valid crop name and price");
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";

    try {
        const res = await fetch("/api/submit-price", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({
                item,
                price,
                category,
                purchase_location,
                comment,
                image_data: currentPhotoBase64
            })
        });

        const data = await res.json();

        if (!res.ok) {
            showError(data.error || "Failed to submit price details");
            submitBtn.disabled = false;
            submitBtn.textContent = "Submit Price Details →";
            return;
        }

        showSuccess("✅ Crop price & proof submitted successfully! Trust score updated.");
        itemInput.value = "";
        priceInput.value = "";
        if (locationInput) locationInput.value = "";
        if (commentInput) commentInput.value = "";
        clearPhoto();

        submitBtn.disabled = false;
        submitBtn.textContent = "Submit Price Details →";

        loadDashboardData();
        loadLivePrices();
        loadAiAdvisory();
        loadGamification();
        loadMarketTicker();
        loadLeaderboard(activeLeaderboardPeriod);
        loadAnalytics();

    } catch (err) {
        console.error("Price submit error:", err);
        showError("Network error submitting price");
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit Price Details →";
    }
}

async function votePrice(entryId, action) {
    try {
        const res = await fetch(`/api/verify-price/${entryId}/${action}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include"
        });
        const data = await res.json();

        if (!res.ok) {
            showError(data.error || "Failed to record vote");
            return;
        }

        showSuccess(`Verification vote recorded! (${action === 'upvote' ? '👍 Accurate' : '👎 Disputed'})`);
        loadLivePrices();
        loadDashboardData();
        loadGamification();
        loadAnalytics();
    } catch (err) {
        showError("Network error recording verification vote");
    }
}

// ===================================================================
// 15. ANALYTICS & CHARTS
// ===================================================================
async function loadAnalytics() {
    loadTrendsChart();
    loadVillageComparison();
}

async function loadTrendsChart() {
    try {
        const res = await fetch("/api/price-trends", { credentials: "include" });
        if (!res.ok) return;

        const data = await res.json();
        const trends = data.trends || [];

        const ctx = document.getElementById("trendsChart");
        if (!ctx) return;

        const labels = trends.map(t => t.item);
        const values = trends.map(t => t.avg_price);

        if (trendsChartInstance) {
            trendsChartInstance.destroy();
        }

        const isLight = document.body.classList.contains("light");
        const textColor = isLight ? "#1e293b" : "#f0f4f8";
        const gridColor = isLight ? "rgba(0,0,0,0.06)" : "rgba(255,255,255,0.06)";

        trendsChartInstance = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels.length ? labels : ["No Data"],
                datasets: [{
                    label: "Average Price (₹)",
                    data: values.length ? values : [0],
                    backgroundColor: "rgba(0, 200, 150, 0.65)",
                    borderColor: "#00c896",
                    borderWidth: 2,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: '600' } } }
                },
                scales: {
                    x: { ticks: { color: textColor }, grid: { color: gridColor } },
                    y: { ticks: { color: textColor }, grid: { color: gridColor } }
                }
            }
        });
    } catch (err) {
        console.error("Trends error:", err);
    }
}

async function loadVillageComparison() {
    try {
        const res = await fetch("/api/village-comparison", { credentials: "include" });
        if (!res.ok) return;

        const data = await res.json();
        const comp = data.comparison || {};
        const tbody = document.getElementById("comparisonTableBody");
        if (!tbody) return;

        const rows = [];
        for (const [crop, villageList] of Object.entries(comp)) {
            const ourAvg = cachedVillageAverages[crop.toLowerCase()];

            villageList.forEach(v => {
                let badgeClass = "comp-neutral";
                let diffText = "—";

                if (ourAvg && !v.is_current) {
                    const diff = v.avg_price - ourAvg;
                    if (diff > 0.5) {
                        diffText = `+₹${diff.toFixed(2)} (Higher)`;
                        badgeClass = "comp-higher";
                    } else if (diff < -0.5) {
                        diffText = `-₹${Math.abs(diff).toFixed(2)} (Cheaper)`;
                        badgeClass = "comp-lower";
                    } else {
                        diffText = `≈ Equal`;
                        badgeClass = "comp-equal";
                    }
                } else if (v.is_current) {
                    diffText = "Your Village";
                    badgeClass = "comp-equal";
                }

                rows.push(`
                    <tr>
                        <td><strong>${crop}</strong></td>
                        <td>${v.village} ${v.is_current ? '📍' : ''}</td>
                        <td>₹${v.avg_price.toFixed(2)}</td>
                        <td><span class="comp-badge-table ${badgeClass}">${diffText}</span></td>
                    </tr>
                `);
            });
        }

        if (rows.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="empty-msg">Submit crop prices to see comparisons!</td></tr>`;
        } else {
            tbody.innerHTML = rows.join("");
        }

    } catch (err) {
        console.error("Comparison error:", err);
    }
}

// ===================================================================
// 16. LEADERBOARD & THEME
// ===================================================================
async function loadLeaderboard(period = "weekly") {
    try {
        const url = period === "global" ? "/api/leaderboard/global" : `/api/leaderboard/${period}`;
        const res = await fetch(url, { credentials: "include" });
        if (!res.ok) return;

        const data = await res.json();
        const list = Array.isArray(data) ? data : (data.users || data.leaderboard || []);
        const container = document.getElementById("leaderboardContainer");
        if (!container) return;

        if (list.length === 0) {
            container.innerHTML = `<p class="empty-msg">No contributions yet in this period</p>`;
            return;
        }

        container.innerHTML = list.map((u, i) => {
            const rankClass = i === 0 ? "rank-1" : (i === 1 ? "rank-2" : (i === 2 ? "rank-3" : ""));
            const rankEmoji = i === 0 ? "🥇" : (i === 1 ? "🥈" : (i === 2 ? "🥉" : `${i+1}`));

            return `
                <div class="leaderboard-item">
                    <div class="leaderboard-rank ${rankClass}">${rankEmoji}</div>
                    <div class="leaderboard-info">
                        <div class="leaderboard-name">${u.name || u.username}</div>
                        <div class="leaderboard-username">@${u.username} · ${u.village || 'Village'}</div>
                    </div>
                    <div class="leaderboard-score">🛡️ ${Math.round(u.trust_score ?? u.score ?? 50)}%</div>
                </div>
            `;
        }).join("");
    } catch (err) {
        console.error("Leaderboard error:", err);
    }
}

function switchLeaderboardTab(period) {
    activeLeaderboardPeriod = period;
    document.querySelectorAll(".leaderboard-tabs .tab-btn").forEach(btn => {
        if (btn.getAttribute("onclick")?.includes(period)) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });
    loadLeaderboard(period);
}

function toggleTheme() {
    const isDark = document.body.classList.toggle("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");
    const themeBtn = document.getElementById("themeBtn");
    if (themeBtn) themeBtn.textContent = isDark ? "☀️ Farm Day" : "🌙 Forest Night";
    loadTrendsChart();
}

function applySavedTheme() {
    const t = localStorage.getItem("theme") || "light"; // Sunlit Farm Day default
    document.body.classList.toggle("dark", t === "dark");
    const themeBtn = document.getElementById("themeBtn");
    if (themeBtn) themeBtn.textContent = t === "dark" ? "☀️ Farm Day" : "🌙 Forest Night";
}

function refreshData() {
    showSuccess("Refreshing all live mandi data...");
    loadMarketTicker();
    loadWeatherWidget();
    loadGamification();
    loadDashboardData();
    loadDeals();
    loadLivePrices();
    loadAiAdvisory();
    loadMandiMap();
    loadAlerts();
    loadLeaderboard(activeLeaderboardPeriod);
    loadAnalytics();
}

async function logout() {
    try {
        await fetch("/api/logout", { method: "POST", credentials: "include" });
    } finally {
        window.location.href = "/login";
    }
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? 0;
}

function showError(msg) {
    const errorBox = document.getElementById("errorMessage");
    if (errorBox) {
        errorBox.textContent = msg;
        errorBox.style.display = "block";
        errorBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        setTimeout(() => errorBox.style.display = "none", 5000);
    } else {
        alert(msg);
    }
}

function showSuccess(msg) {
    const successBox = document.getElementById("successMessage");
    if (successBox) {
        successBox.textContent = msg;
        successBox.style.display = "block";
        setTimeout(() => successBox.style.display = "none", 4000);
    }
}
