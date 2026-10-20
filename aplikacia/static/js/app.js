/**
 * app.js — Interaktívna funkcionalita pre Zbierku & Vinted Snajpera
 * Apple-style jednoduché ovládanie, rýchle prechody, automatické dopĺňanie z API
 * a jedno-klikové pridávanie inzerátov do databázy s okamžitým prepočtom hodnoty.
 */

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initSearchAndFilters();
  initModals();
  initApiAutocomplete();
  initVintedFeed();
  initChart();
});

// ── 1. Apple Segmented Control (Záložky) ────────────────────────────────────
function initTabs() {
  const buttons = document.querySelectorAll(".seg-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      buttons.forEach(b => b.classList.remove("active"));
      tabContents.forEach(tc => tc.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetEl = document.getElementById(targetId);
      if (targetEl) {
        targetEl.classList.add("active");
      }

      if (targetId === "tab-trends") {
        renderTrendsChart();
      }
      if (targetId === "tab-vinted") {
        loadVintedListings();
      }
    });
  });
}

// ── 2. Toast Notifikácie (Apple Style) ──────────────────────────────────────
function showToast(message, isSuccess = true) {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `<span>${isSuccess ? "✓" : "ℹ"}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(15px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3800);
}

// ── 3. Aktualizácia súhrnných metrík (Summary Stats) ────────────────────────
function updateSummaryStats(summary) {
  const valEl = document.getElementById("stat-total-value");
  const purEl = document.getElementById("stat-total-purchase");
  const countEl = document.getElementById("stat-total-count");
  const roiEl = document.getElementById("stat-roi-badge");

  if (valEl) valEl.textContent = `${summary.total_value.toFixed(2).replace('.', ',')} €`;
  if (purEl) purEl.textContent = `${summary.total_purchase.toFixed(2).replace('.', ',')} €`;
  if (countEl) countEl.textContent = `${summary.total_items} ks`;
  if (roiEl) {
    const sign = summary.total_profit >= 0 ? "+" : "";
    roiEl.textContent = `${sign}${summary.total_profit.toFixed(2).replace('.', ',')} € (${sign}${summary.roi_pct.toFixed(1)} %)`;
  }
}

// ── 4. Filtrovanie a hľadanie v zbierke ─────────────────────────────────────
function initSearchAndFilters() {
  const searchInput = document.getElementById("collection-search");
  const pills = document.querySelectorAll(".filter-pill");

  let currentCategory = "all";

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      fetchFilteredCollection(searchInput.value, currentCategory);
    });
  }

  pills.forEach(pill => {
    pill.addEventListener("click", () => {
      pills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      currentCategory = pill.getAttribute("data-category");
      fetchFilteredCollection(searchInput ? searchInput.value : "", currentCategory);
    });
  });
}

async function fetchFilteredCollection(search, category) {
  try {
    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (category && category !== "all") params.append("category", category);

    const res = await fetch(`/api/portfolio?${params.toString()}`);
    const data = await res.json();
    renderCollectionGrid(data.items);
    updateSummaryStats(data.summary);
  } catch (err) {
    console.error("Chyba načítania zbierky:", err);
  }
}

function renderCollectionGrid(items) {
  const grid = document.getElementById("collection-grid");
  if (!grid) return;

  if (items.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--apple-secondary);">
        <p style="font-size: 36px; margin-bottom: 10px;">📦</p>
        <p style="font-size: 16px; font-weight: 500;">Nenašli sa žiadne položky</p>
        <p style="font-size: 13px;">Skúste zmeniť filter alebo pridajte nový predmet.</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = items.map(item => {
    const profit = (item.estimated_value - item.purchase_price).toFixed(2).replace('.', ',');
    const isProfit = (item.estimated_value - item.purchase_price) >= 0;
    const photo = item.photo_url || "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80";

    return `
      <div class="item-card" data-id="${item.id}">
        <div class="card-img-wrapper">
          <img src="${photo}" alt="${item.name}" class="card-img" onerror="this.src='https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80'">
          <span class="card-badge">${item.category}</span>
          ${item.source === 'Vinted Snajper' ? '<span class="card-source-badge">⚡ Vinted</span>' : ''}
        </div>
        <div class="card-body">
          <h3 class="card-title" title="${item.name}">${item.name}</h3>
          <p class="card-notes">${item.notes || 'Stav: ' + item.condition}</p>
          <div class="card-footer">
            <div class="price-col">
              <span class="price-sub">Kúpna cena</span>
              <span class="price-val">${item.purchase_price.toFixed(2).replace('.', ',')} €</span>
            </div>
            <div class="price-col" style="text-align: right;">
              <span class="price-sub">Trhová hodnota</span>
              <span class="price-val ${isProfit ? 'profit' : ''}">${item.estimated_value.toFixed(2).replace('.', ',')} €</span>
            </div>
            <button class="btn-card-del" onclick="deleteItem(${item.id})" title="Zmazať položku">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
            </button>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

async function deleteItem(id) {
  if (!confirm("Naozaj si želáte vymazať túto položku zo svojej zbierky?")) return;
  try {
    const res = await fetch(`/api/items/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (data.success) {
      showToast(data.message);
      updateSummaryStats(data.summary);
      const card = document.querySelector(`.item-card[data-id="${id}"]`);
      if (card) card.remove();
    }
  } catch (err) {
    console.error("Chyba mazania:", err);
  }
}

// ── 5. Vinted Snajper Feed & KĽÚČOVÉ AUTOMATICKÉ PRIDÁVANIE ────────────────
function initVintedFeed() {
  const vintedFilter = document.getElementById("vinted-search-filter");
  if (vintedFilter) {
    vintedFilter.addEventListener("change", () => {
      loadVintedListings(vintedFilter.value);
    });
  }
}

async function loadVintedListings(searchName = "all") {
  const grid = document.getElementById("vinted-grid");
  if (!grid) return;

  grid.innerHTML = `
    <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--apple-secondary);">
      <p>⚡ Načítavam najnovšie ponuky z Vinted Snajpera...</p>
    </div>
  `;

  try {
    const res = await fetch(`/api/vinted/listings?search_name=${encodeURIComponent(searchName)}`);
    const listings = await res.json();

    if (listings.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--apple-secondary);">
          <p style="font-size: 32px; margin-bottom: 10px;">🔍</p>
          <p style="font-size: 16px; font-weight: 500;">Zatiaľ žiadne inzeráty pre túto kategóriu</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = listings.map(item => {
      const photo = item.image_url || "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80";
      const isAdded = item.already_added;

      return `
        <div class="item-card vinted-card" id="vinted-card-${item.item_id}">
          <div class="card-img-wrapper">
            <img src="${photo}" alt="${item.title}" class="card-img" onerror="this.src='https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80'">
            <span class="card-badge">⚡ ${item.search_name}</span>
          </div>
          <div class="card-body">
            <h3 class="card-title" title="${item.title}">${item.title}</h3>
            <div style="margin-bottom: 12px; font-size: 12px; color: var(--apple-secondary);">
              Zverejnené: ${item.added_at ? item.added_at.substring(0, 16) : 'Nedávno'}
            </div>
            <div class="card-footer">
              <div class="price-col">
                <span class="price-sub">Cena na Vinted</span>
                <span class="price-val" style="color: var(--vinted-dark);">${item.price}</span>
              </div>
              <div style="display: flex; gap: 8px;">
                <a href="${item.url}" target="_blank" class="btn-card-del" title="Otvoriť na Vinted" style="display: flex; align-items: center;">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                </a>
                <button 
                  class="btn-quick-add ${isAdded ? 'added' : ''}" 
                  id="btn-add-${item.item_id}"
                  onclick='handleQuickAdd(${JSON.stringify(item).replace(/'/g, "&#39;")})'
                >
                  ${isAdded ? '✓ V zbierke' : '★ Pridať'}
                </button>
              </div>
            </div>
          </div>
        </div>
      `;
    }).join("");
  } catch (err) {
    console.error("Chyba načítania inzerátov:", err);
  }
}

// KĽÚČOVÁ FUNKCIA: Automatické pridanie jedným klikom z inzerátu do zbierky
async function handleQuickAdd(item) {
  const btn = document.getElementById(`btn-add-${item.item_id}`);
  if (btn && btn.classList.contains("added")) return;

  if (btn) {
    btn.textContent = "Pridávam...";
    btn.style.opacity = "0.7";
  }

  try {
    const payload = {
      title: item.title,
      price: item.numeric_price,
      estimated_value: item.estimated_market_value,
      url: item.url,
      photo_url: item.image_url,
      item_id: item.item_id,
      search_name: item.search_name
    };

    const res = await fetch("/api/vinted/quick-add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data.success) {
      if (btn) {
        btn.textContent = "✓ V zbierke";
        btn.classList.add("added");
        btn.style.opacity = "1";
      }

      // Okamžitý prepočet v hornej lište
      updateSummaryStats(data.summary);
      showToast(data.message);

      // Znovu načítame zbierku na pozadí
      const searchInput = document.getElementById("collection-search");
      fetchFilteredCollection(searchInput ? searchInput.value : "", "all");
    } else {
      if (btn) {
        btn.textContent = "★ Pridať";
        btn.style.opacity = "1";
      }
      showToast(data.error || "Chyba pri ukladaní", false);
    }
  } catch (err) {
    console.error("Chyba Quick Add:", err);
    if (btn) {
      btn.textContent = "★ Pridať";
      btn.style.opacity = "1";
    }
  }
}

// ── 6. Modálne okná & Automatické dopĺňanie cez Verejné API ────────────────
function initModals() {
  const modalAdd = document.getElementById("modal-add-item");
  const btnOpenAdd = document.getElementById("btn-open-add-modal");
  const btnCloseAdd = document.getElementById("btn-close-add-modal");
  const formAdd = document.getElementById("form-add-item");

  if (btnOpenAdd && modalAdd) {
    btnOpenAdd.addEventListener("click", () => modalAdd.classList.add("active"));
  }
  if (btnCloseAdd && modalAdd) {
    btnCloseAdd.addEventListener("click", () => modalAdd.classList.remove("active"));
  }

  // Zatvorenie kliknutím na pozadie
  window.addEventListener("click", (e) => {
    if (e.target === modalAdd) modalAdd.classList.remove("active");
  });

  if (formAdd) {
    formAdd.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(formAdd);
      const payload = Object.fromEntries(formData.entries());

      try {
        const res = await fetch("/api/items", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
          showToast(data.message);
          updateSummaryStats(data.summary);
          formAdd.reset();
          modalAdd.classList.remove("active");
          const searchInput = document.getElementById("collection-search");
          fetchFilteredCollection(searchInput ? searchInput.value : "", "all");
        } else {
          showToast(data.error || "Chyba pridania", false);
        }
      } catch (err) {
        console.error("Chyba odoslania formulára:", err);
      }
    });
  }
}

// Automatické dopĺňanie z API (Autosuggest)
function initApiAutocomplete() {
  const nameInput = document.getElementById("item-name-input");
  const suggestBox = document.getElementById("api-suggest-box");
  const suggestList = document.getElementById("api-suggest-list");

  let debounceTimer = null;

  if (!nameInput || !suggestBox || !suggestList) return;

  nameInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    const query = nameInput.value.trim();

    if (query.length < 2) {
      suggestBox.style.display = "none";
      return;
    }

    debounceTimer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/catalog/search?q=${encodeURIComponent(query)}`);
        const matches = await res.json();

        if (matches && matches.length > 0) {
          suggestList.innerHTML = matches.slice(0, 4).map(item => `
            <div class="api-suggest-item" onclick='applyApiSuggestion(${JSON.stringify(item).replace(/'/g, "&#39;")})'>
              <img src="${item.photo_url}" class="api-suggest-thumb" onerror="this.src='https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80'">
              <div style="flex: 1;">
                <div style="font-size: 13.5px; font-weight: 600; color: var(--apple-text);">${item.name}</div>
                <div style="font-size: 12px; color: var(--apple-secondary);">${item.category} · ${item.brand || ''} · Trh: ~${item.estimated_value} €</div>
              </div>
              <span style="font-size: 12px; font-weight: 600; color: var(--vinted-teal);">Použiť metadáta →</span>
            </div>
          `).join("");
          suggestBox.style.display = "block";
        } else {
          suggestBox.style.display = "none";
        }
      } catch (err) {
        console.error("Chyba API hľadania:", err);
      }
    }, 200);
  });
}

function applyApiSuggestion(item) {
  document.getElementById("item-name-input").value = item.name;
  document.getElementById("item-category-input").value = item.category || "Ostatné";
  document.getElementById("item-condition-input").value = item.default_condition || "Veľmi dobrý";
  document.getElementById("item-est-value-input").value = item.estimated_value || "";
  document.getElementById("item-photo-input").value = item.photo_url || "";
  document.getElementById("item-notes-input").value = item.description || "";

  // Ak nákupná cena nie je zadaná, odporučíme orientačnú
  const purchaseInput = document.getElementById("item-price-input");
  if (purchaseInput && !purchaseInput.value) {
    purchaseInput.value = (item.estimated_value * 0.75).toFixed(2);
  }

  const suggestBox = document.getElementById("api-suggest-box");
  if (suggestBox) suggestBox.style.display = "none";

  showToast(`Metadáta a fotografia pre '${item.name}' automaticky doplnené z verejného API!`);
}

// ── 7. Graf vývoja trhových cien (Chart.js) ────────────────────────────────
let trendsChart = null;

async function renderTrendsChart() {
  const canvas = document.getElementById("chart-portfolio");
  if (!canvas) return;

  try {
    const res = await fetch("/api/chart");
    const data = await res.json();

    if (trendsChart) {
      trendsChart.destroy();
    }

    const ctx = canvas.getContext("2d");
    trendsChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: data.labels,
        datasets: [{
          label: "Trhová hodnota zbierky (€)",
          data: data.values,
          borderColor: "#09b1ba",
          backgroundColor: "rgba(9, 177, 186, 0.08)",
          fill: true,
          tension: 0.35,
          borderWidth: 2.5,
          pointBackgroundColor: "#09b1ba",
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "rgba(29, 29, 31, 0.92)",
            padding: 12,
            titleFont: { size: 13, family: "-apple-system, sans-serif" },
            bodyFont: { size: 14, weight: "bold", family: "-apple-system, sans-serif" },
            callbacks: {
              label: (context) => ` Hodnota: ${context.parsed.y.toFixed(2)} €`
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { font: { size: 12, family: "-apple-system, sans-serif" }, color: "#86868b" }
          },
          y: {
            grid: { color: "rgba(0, 0, 0, 0.05)" },
            ticks: {
              font: { size: 12, family: "-apple-system, sans-serif" },
              color: "#86868b",
              callback: (val) => val + " €"
            }
          }
        }
      }
    });
  } catch (err) {
    console.error("Chyba vykreslenia grafu:", err);
  }
}

function initChart() {
  // Inicializácia pri prvom načítaní
}
