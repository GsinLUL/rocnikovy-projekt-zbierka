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

// ── 5. Vinted Snajper Feed, Dynamické Časy & Telegram Integrácia ─────────
let currentVintedCategory = "all";
let currentVintedQuery = "";
let currentVintedSort = "newest";
let vintedSearchTimeout = null;
let liveStreamCountdown = 6;
let latestListingId = null;

function initVintedFeed() {
  // 1. Vyhľadávacie pole v zachytených inzerátoch
  const searchInput = document.getElementById("vinted-search-input");
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(vintedSearchTimeout);
      vintedSearchTimeout = setTimeout(() => {
        currentVintedQuery = searchInput.value.trim();
        loadVintedListings();
      }, 250);
    });
  }

  // 2. Počiatočné načítanie inzerátov
  loadVintedListings();

  // 3. Živý ticker pre odpočítavanie sekúnd ("pred X sekundami") - každú 1 sekundu!
  setInterval(updateLiveTimestamps, 1000);

  // 4. Periodické overovanie nových inzerátov (živý radarový stream každých 6 sekúnd)
  setInterval(pollNewVintedListings, 6000);
}

// Dynamický výpočet relatívneho času v prirodzenej slovenčine
function formatRelativeTime(timestampMs) {
  if (!timestampMs) return "nedávno";
  const now = Date.now();
  const diffSec = Math.max(0, Math.floor((now - timestampMs) / 1000));

  if (diffSec < 4) {
    return "práve teraz";
  }
  if (diffSec < 60) {
    if (diffSec === 1) return "pred 1 sekundou";
    if (diffSec >= 2 && diffSec <= 4) return `pred ${diffSec} sekundami`;
    return `pred ${diffSec} sekundami`;
  }
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) {
    if (diffMin === 1) return "pred 1 minútou";
    if (diffMin >= 2 && diffMin <= 4) return `pred ${diffMin} minútami`;
    return `pred ${diffMin} minútami`;
  }
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) {
    if (diffHours === 1) return "pred 1 hodinou";
    if (diffHours >= 2 && diffHours <= 4) return `pred ${diffHours} hodinami`;
    return `pred ${diffHours} hodinami`;
  }
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays === 1) return "pred 1 dňom";
  if (diffDays >= 2 && diffDays <= 4) return `pred ${diffDays} dňami`;
  return `pred ${diffDays} dňami`;
}

// Funkcia prechodu všetkých zobrazených kariet a aktualizáciu textu času
function updateLiveTimestamps() {
  const badges = document.querySelectorAll(".vinted-time-badge");
  badges.forEach(badge => {
    const ts = parseInt(badge.getAttribute("data-ts"), 10);
    if (ts) {
      const textSpan = badge.querySelector(".time-text");
      if (textSpan) {
        textSpan.textContent = formatRelativeTime(ts);
      }
    }
  });

  // Odpočítavanie pre indikátor streamu
  const timerText = document.getElementById("live-timer-text");
  if (timerText) {
    liveStreamCountdown = liveStreamCountdown > 1 ? liveStreamCountdown - 1 : 6;
    timerText.textContent = `Stream: aktívny (${liveStreamCountdown}s)`;
  }
}

// Prepínanie kategórií pomocou pill tlačidiel
function switchVintedCategory(categoryKey, btnEl) {
  currentVintedCategory = categoryKey;
  const pills = document.querySelectorAll(".pill-vinted-cat");
  pills.forEach(p => p.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");
  loadVintedListings();
}

// Zmena radenia
function handleSortChange(sortVal) {
  currentVintedSort = sortVal;
  loadVintedListings();
}

// Načítanie inzerátov zo servera
async function loadVintedListings() {
  const grid = document.getElementById("vinted-grid");
  if (!grid) return;

  grid.innerHTML = `
    <div style="grid-column: 1 / -1; text-align: center; padding: 45px 20px; color: var(--apple-secondary);">
      <p style="font-size: 24px; margin-bottom: 8px;">⚡</p>
      <p style="font-weight: 500;">Načítavam najnovšie ponuky z Vinted Snajpera...</p>
    </div>
  `;

  try {
    const params = new URLSearchParams({
      search_name: currentVintedCategory,
      q: currentVintedQuery,
      sort_by: currentVintedSort,
      limit: "60"
    });

    const res = await fetch(`/api/vinted/listings?${params.toString()}`);
    const data = await res.json();
    const listings = data.listings || [];

    if (listings.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--apple-secondary);">
          <p style="font-size: 32px; margin-bottom: 10px;">🔍</p>
          <p style="font-size: 16px; font-weight: 600; color: var(--apple-text);">Nenašli sa žiadne inzeráty</p>
          <p style="font-size: 13px; margin-top: 4px;">Skúste zmeniť kategóriu alebo hľadaný výraz.</p>
        </div>
      `;
      return;
    }

    if (listings.length > 0) {
      latestListingId = listings[0].item_id;
    }

    renderVintedGrid(listings);
  } catch (err) {
    console.error("Chyba načítania inzerátov:", err);
  }
}

// Vykreslenie kariet inzerátov s prehľadným oddelením funkcií
function renderVintedGrid(listings) {
  const grid = document.getElementById("vinted-grid");
  if (!grid) return;

  grid.innerHTML = listings.map(item => {
    const photo = item.image_url || "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80";
    const isAdded = item.already_added;
    const timeText = formatRelativeTime(item.added_at_ts);

    // Bezpečný objekt pre JSON odovzdanie do QuickAdd
    const safeItem = JSON.stringify({
      item_id: item.item_id,
      title: item.title,
      price: item.numeric_price,
      estimated_market_value: item.estimated_market_value,
      url: item.url,
      image_url: item.image_url,
      search_name: item.search_name
    }).replace(/'/g, "&#39;");

    return `
      <div class="vinted-card ${item.is_new ? 'new-item-highlight' : ''}" id="vinted-card-${item.item_id}">
        <div class="card-img-wrapper">
          <img src="${photo}" alt="${item.title}" class="card-img" onerror="this.src='https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80'">
          
          <!-- Živý odpočet sekúnd / minút -->
          <span class="vinted-time-badge" data-ts="${item.added_at_ts}">
            <span class="dot-live"></span>
            <span class="time-text">${timeText}</span>
          </span>

          <span class="vinted-category-badge">⚡ ${item.search_name}</span>
        </div>

        <div class="card-body">
          <h3 class="vinted-card-title" title="${item.title}">${item.title}</h3>
          
          <div class="vinted-price-box">
            <span class="vinted-price-main">${item.price_formatted || item.price}</span>
            <span class="vinted-protection-line">(${item.buyer_protection_str || 's ochranou'})</span>
          </div>

          <!-- KĽÚČOVÉ ODDELENIE: Hlavná akcia = Otvoriť na Vinted, Vedľajšia = Uložiť do zbierky -->
          <div class="vinted-actions-row">
            <!-- 1. HLAVNÁ VÝRAZNÁ AKCIA: Otvorenie inzerátu na trhovisku -->
            <a href="${item.url}" target="_blank" class="btn-open-vinted">
              <span>Otvoriť na Vinted</span>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
            </a>

            <!-- 2. NENÁPADNÁ SEKUNDÁRNA AKCIA: Zaznamenať do zbierky (menej viditeľná) -->
            <button 
              class="btn-subtle-collect ${isAdded ? 'collected' : ''}" 
              id="btn-collect-${item.item_id}"
              onclick='handleQuickAdd(${safeItem})'
              title="${isAdded ? 'Tento inzerát je už zaevidovaný vo vašej zbierke' : 'Uložiť tento predmet ako záznam do mojej zbierky'}"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="${isAdded ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
              </svg>
              <span>${isAdded ? 'V zbierke' : '+ Zbierka'}</span>
            </button>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

// Overovanie nových inzerátov v pozadí pre živý stream
async function pollNewVintedListings() {
  try {
    const res = await fetch(`/api/vinted/listings?search_name=all&limit=5`);
    const data = await res.json();
    const listings = data.listings || [];

    if (listings.length > 0 && latestListingId && listings[0].item_id !== latestListingId) {
      // Objavil sa nový inzerát!
      const newItem = listings[0];
      latestListingId = newItem.item_id;

      if (currentVintedCategory === "all" || currentVintedCategory === newItem.search_name) {
        prependNewListing(newItem);
        showToast(`⚡ Vinted Snajper zachytil nový inzerát: ${newItem.title.substring(0, 32)}... (${newItem.price_formatted})! Odoslané aj na Telegram.`);
      }
    }
  } catch (err) {
    // Tiché zlyhanie pri periodickom dopyte
  }
}

// Pridanie novej karty na vrchol gridu
function prependNewListing(item) {
  const grid = document.getElementById("vinted-grid");
  if (!grid) return;

  item.is_new = true;
  const photo = item.image_url || "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80";
  const isAdded = item.already_added;
  const timeText = formatRelativeTime(item.added_at_ts);

  const safeItem = JSON.stringify({
    item_id: item.item_id,
    title: item.title,
    price: item.numeric_price,
    estimated_market_value: item.estimated_market_value,
    url: item.url,
    image_url: item.image_url,
    search_name: item.search_name
  }).replace(/'/g, "&#39;");

  const cardHtml = `
    <div class="vinted-card new-item-highlight" id="vinted-card-${item.item_id}">
      <div class="card-img-wrapper">
        <img src="${photo}" alt="${item.title}" class="card-img" onerror="this.src='https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&auto=format&fit=crop&q=80'">
        <span class="vinted-time-badge" data-ts="${item.added_at_ts}">
          <span class="dot-live"></span>
          <span class="time-text">${timeText}</span>
        </span>
        <span class="vinted-category-badge">⚡ ${item.search_name}</span>
      </div>
      <div class="card-body">
        <h3 class="vinted-card-title" title="${item.title}">${item.title}</h3>
        <div class="vinted-price-box">
          <span class="vinted-price-main">${item.price_formatted || item.price}</span>
          <span class="vinted-protection-line">(${item.buyer_protection_str || 's ochranou'})</span>
        </div>
        <div class="vinted-actions-row">
          <a href="${item.url}" target="_blank" class="btn-open-vinted">
            <span>Otvoriť na Vinted</span>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
          </a>
          <button 
            class="btn-subtle-collect ${isAdded ? 'collected' : ''}" 
            id="btn-collect-${item.item_id}"
            onclick='handleQuickAdd(${safeItem})'
            title="Uložiť tento predmet ako záznam do mojej zbierky"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="${isAdded ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
            </svg>
            <span>${isAdded ? 'V zbierke' : '+ Zbierka'}</span>
          </button>
        </div>
      </div>
    </div>
  `;

  grid.insertAdjacentHTML("afterbegin", cardHtml);
}

// Simulácia nového úlovku bota (Demonštrácia reálneho času a Telegramu)
async function simulateNewDeal() {
  const btn = document.querySelector(".btn-simulate-deal");
  if (btn) {
    btn.style.opacity = "0.7";
    btn.style.pointerEvents = "none";
  }

  try {
    const res = await fetch("/api/vinted/simulate-deal", { method: "POST" });
    const data = await res.json();
    if (data.success && data.item) {
      prependNewListing(data.item);
      const tgMsg = data.telegram_sent ? "Zároveň odoslané na váš Telegram! 📲" : "Zaevidované v radare.";
      showToast(`⚡ Bot zachytil nový inzerát: ${data.item.title.substring(0, 32)}... ${tgMsg}`);
    } else {
      showToast("Chyba pri simulácii", false);
    }
  } catch (err) {
    console.error("Chyba simulácie:", err);
  } finally {
    if (btn) {
      btn.style.opacity = "1";
      btn.style.pointerEvents = "auto";
    }
  }
}

// KĽÚČOVÉ AUTOMATICKÉ PRIDÁVANIE DO ZBIERKY (Nenadradené / Sekundárne)
async function handleQuickAdd(item) {
  const btn = document.getElementById(`btn-collect-${item.item_id}`);
  if (btn && btn.classList.contains("collected")) return;

  if (btn) {
    btn.innerHTML = `<span>Ukladám...</span>`;
    btn.style.opacity = "0.7";
  }

  try {
    const payload = {
      title: item.title,
      price: item.price,
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
        btn.innerHTML = `
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
          </svg>
          <span>V zbierke</span>
        `;
        btn.classList.add("collected");
        btn.style.opacity = "1";
      }

      // Okamžitý prepočet v hornej lište (celková hodnota portfólia)
      updateSummaryStats(data.summary);
      showToast(data.message);

      // Aktualizácia zbierky na pozadí
      const searchInput = document.getElementById("collection-search");
      fetchFilteredCollection(searchInput ? searchInput.value : "", "all");
    } else {
      if (btn) {
        btn.innerHTML = `<span>+ Zbierka</span>`;
        btn.style.opacity = "1";
      }
      showToast(data.error || "Chyba pri ukladaní", false);
    }
  } catch (err) {
    console.error("Chyba Quick Add:", err);
    if (btn) {
      btn.innerHTML = `<span>+ Zbierka</span>`;
      btn.style.opacity = "1";
    }
  }
}

// ── Telegram Modal & Testovacie funkcie ─────────────────────────────────
function openTelegramModal() {
  const modal = document.getElementById("modal-telegram");
  if (modal) modal.classList.add("active");
}

function closeTelegramModal() {
  const modal = document.getElementById("modal-telegram");
  if (modal) modal.classList.remove("active");
}

async function handleSaveTelegram(e) {
  e.preventDefault();
  const token = document.getElementById("tg-input-token").value.trim();
  const chatId = document.getElementById("tg-input-chat-id").value.trim();

  try {
    const res = await fetch("/api/telegram/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: token, chat_id: chatId })
    });
    const data = await res.json();
    if (data.success) {
      showToast("✓ Telegram nastavenia boli úspešne uložené!");
      const statusText = document.getElementById("tg-status-text");
      if (statusText) {
        statusText.innerHTML = `<span class="tg-dot active"></span> Aktívne (posiela do chatu)`;
      }
      closeTelegramModal();
    } else {
      showToast(data.error || "Chyba ukladania", false);
    }
  } catch (err) {
    console.error("Chyba Telegram save:", err);
  }
}

async function testTelegramAlert() {
  showToast("✈️ Odosielam testovaciu notifikáciu do Telegramu...");
  try {
    const res = await fetch("/api/telegram/test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: "Sony PlayStation 2 Slim (Test bota)",
        price: 45.0,
        url: "https://www.vinted.sk/catalog?search_text=ps2",
        search_name: "PS2 Snajper"
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast("✓ Správa bola úspešne doručená do vášho Telegramu!");
      const statusText = document.getElementById("tg-status-text");
      if (statusText) {
        statusText.innerHTML = `<span class="tg-dot active"></span> Aktívne (posiela do chatu)`;
      }
    } else {
      showToast(`Telegram upozornenie: ${data.error || "Zlyhanie odoslania"}`, false);
      openTelegramModal();
    }
  } catch (err) {
    console.error("Chyba testu Telegramu:", err);
    showToast("Chyba spojenia s Telegramom", false);
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
