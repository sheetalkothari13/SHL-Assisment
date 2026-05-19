/*
================================================================
SHL Assessment Recommender - Premium Javascript Engine
================================================================
*/

const API_BASE = window.location.origin;

// State Management
let state = {
    catalog: {},
    flattenedCatalog: [],
    sessions: [],
    campaigns: [],
    activeSessionId: null,
    basket: [], // items: { name, code, type, url, why_selected }
    campaignMetadata: {
        title: "New Recruitment Campaign",
        role: "",
        seniority: "Mid"
    }
};

// Competency Mapping by Test Type
const TEST_TYPE_MAPPING = {
    "K": "Technical Knowledge",
    "P": "Personality & Fit",
    "A": "Cognitive Ability",
    "I": "Industry Specific"
};

// Initialize Application
document.addEventListener("DOMContentLoaded", async () => {
    initEventListeners();
    await fetchCatalog();
    await fetchSessions();
    await fetchCampaigns();
    
    // Auto-create initial session if none exist
    if (state.sessions.length === 0) {
        await createNewSession();
    } else {
        await selectSession(state.sessions[0].id);
    }
});

// Event Listeners Registration
function initEventListeners() {
    // Session handlers
    document.getElementById("btn-new-chat").addEventListener("click", createNewSession);
    document.getElementById("btn-reset-chat").addEventListener("click", createNewSession);
    
    // Chat Form handlers
    const chatInput = document.getElementById("chat-input");
    const sendButton = document.getElementById("send-btn");
    
    sendButton.addEventListener("click", handleUserMessageSubmit);
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleUserMessageSubmit();
        }
    });
    
    // Quickstart Prompts
    document.querySelectorAll(".quickstart-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const prompt = chip.getAttribute("data-prompt");
            chatInput.value = prompt;
            handleUserMessageSubmit();
        });
    });

    // Catalog Search & Filters
    document.getElementById("catalog-search").addEventListener("input", handleCatalogSearch);
    
    document.querySelectorAll(".catalog-tab").forEach(tab => {
        tab.addEventListener("click", (e) => {
            document.querySelectorAll(".catalog-tab").forEach(t => t.classList.remove("active"));
            e.target.classList.add("active");
            renderCatalog();
        });
    });

    // Spec Sheet Basket handlers
    document.getElementById("campaign-title").addEventListener("input", (e) => {
        state.campaignMetadata.title = e.target.value;
    });
    document.getElementById("campaign-role").addEventListener("input", (e) => {
        state.campaignMetadata.role = e.target.value;
    });
    document.getElementById("campaign-seniority").addEventListener("change", (e) => {
        state.campaignMetadata.seniority = e.target.value;
    });

    document.getElementById("btn-save-campaign").addEventListener("click", handleSaveCampaign);

    // Modal close
    document.getElementById("modal-close").addEventListener("click", () => {
        document.getElementById("spec-modal").style.display = "none";
    });
}

// ----------------------------------------------------
// API Calls & Data Fetching
// ----------------------------------------------------

async function fetchCatalog() {
    try {
        const response = await fetch(`${API_BASE}/catalog`);
        state.catalog = await response.json();
        
        // Flatten catalog for search operations
        state.flattenedCatalog = [];
        Object.keys(state.catalog).forEach(type => {
            state.catalog[type].assessments.forEach(item => {
                state.flattenedCatalog.push(item);
            });
        });
        
        renderCatalog();
    } catch (e) {
        console.error("Failed to fetch catalog:", e);
    }
}

async function fetchSessions() {
    try {
        const response = await fetch(`${API_BASE}/sessions`);
        state.sessions = await response.json();
        renderSessionsList();
    } catch (e) {
        console.error("Failed to fetch sessions:", e);
    }
}

async function fetchCampaigns() {
    try {
        const response = await fetch(`${API_BASE}/campaigns`);
        state.campaigns = await response.json();
        renderCampaignsList();
    } catch (e) {
        console.error("Failed to fetch campaigns:", e);
    }
}

async function createNewSession() {
    try {
        const response = await fetch(`${API_BASE}/sessions`, { method: "POST" });
        const newSession = await response.json();
        await fetchSessions();
        await selectSession(newSession.id);
        
        // Reset basket for new conversation
        state.basket = [];
        renderBasket();
        updateCompetencyChart();
    } catch (e) {
        console.error("Failed to create new session:", e);
    }
}

async function selectSession(sessionId) {
    state.activeSessionId = sessionId;
    
    // Highlight session in sidebar
    document.querySelectorAll(".sidebar-item").forEach(item => {
        item.classList.remove("active");
        if (item.getAttribute("data-id") === sessionId) {
            item.classList.add("active");
        }
    });

    try {
        const response = await fetch(`${API_BASE}/sessions/${sessionId}`);
        const sessionDetails = await response.json();
        
        // Load messages and status
        renderChatHistory(sessionDetails.messages);
        updateTurnCounter(sessionDetails.turn_count, sessionDetails.status);
    } catch (e) {
        console.error("Failed to select session:", e);
    }
}

async function deleteSession(sessionId, event) {
    event.stopPropagation();
    if (!confirm("Are you sure you want to delete this conversation session?")) return;
    
    try {
        await fetch(`${API_BASE}/sessions/${sessionId}`, { method: "DELETE" });
        await fetchSessions();
        if (state.activeSessionId === sessionId && state.sessions.length > 0) {
            await selectSession(state.sessions[0].id);
        } else if (state.sessions.length === 0) {
            await createNewSession();
        }
    } catch (e) {
        console.error("Failed to delete session:", e);
    }
}

async function deleteCampaign(campaignId, event) {
    event.stopPropagation();
    if (!confirm("Are you sure you want to delete this saved Campaign Specification?")) return;
    
    try {
        await fetch(`${API_BASE}/campaigns/${campaignId}`, { method: "DELETE" });
        await fetchCampaigns();
    } catch (e) {
        console.error("Failed to delete campaign:", e);
    }
}

// ----------------------------------------------------
// UI Renderers
// ----------------------------------------------------

function renderSessionsList() {
    const listContainer = document.getElementById("sessions-list");
    listContainer.innerHTML = "";
    
    state.sessions.forEach(session => {
        const dateStr = new Date(session.updated_at).toLocaleDateString(undefined, {month:'short', day:'numeric'});
        
        const item = document.createElement("div");
        item.className = `sidebar-item ${session.id === state.activeSessionId ? "active" : ""}`;
        item.setAttribute("data-id", session.id);
        item.addEventListener("click", () => selectSession(session.id));
        
        item.innerHTML = `
            <div class="sidebar-item-info">
                <span class="sidebar-item-title">${escapeHTML(session.title)}</span>
                <span class="sidebar-item-subtitle">Turns: ${session.turn_count}/8 • ${dateStr}</span>
            </div>
            <div class="sidebar-item-delete" title="Delete conversation">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
            </div>
        `;
        
        item.querySelector(".sidebar-item-delete").addEventListener("click", (e) => deleteSession(session.id, e));
        listContainer.appendChild(item);
    });
}

function renderCampaignsList() {
    const listContainer = document.getElementById("campaigns-list");
    listContainer.innerHTML = "";
    
    if (state.campaigns.length === 0) {
        listContainer.innerHTML = `<div style="font-size:0.75rem; color:var(--text-muted); text-align:center; padding:1rem;">No saved campaigns yet. Add assessments to the basket below and save!</div>`;
        return;
    }
    
    state.campaigns.forEach(campaign => {
        const item = document.createElement("div");
        item.className = "sidebar-item";
        item.addEventListener("click", () => previewCampaignMarkdown(campaign.id));
        
        item.innerHTML = `
            <div class="sidebar-item-info">
                <span class="sidebar-item-title">${escapeHTML(campaign.title)}</span>
                <span class="sidebar-item-subtitle">${escapeHTML(campaign.role_name)} • ${campaign.items.length} Tests</span>
            </div>
            <div class="sidebar-item-delete" title="Delete spec sheet">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
            </div>
        `;
        
        item.querySelector(".sidebar-item-delete").addEventListener("click", (e) => deleteCampaign(campaign.id, e));
        listContainer.appendChild(item);
    });
}

function renderChatHistory(messages) {
    const chatContainer = document.getElementById("chat-messages");
    chatContainer.innerHTML = "";
    
    messages.forEach(msg => {
        const bubble = document.createElement("div");
        bubble.className = `chat-bubble ${msg.role}`;
        
        const avatarLetter = msg.role === "assistant" ? "🤖" : "👤";
        
        // Parse markdown lists/newlines into simple html structures
        const htmlContent = formatMarkdown(msg.content);
        
        bubble.innerHTML = `
            <div class="avatar">${avatarLetter}</div>
            <div class="message-content">
                ${htmlContent}
                ${renderBubbleRecommendations(msg.recommendations)}
            </div>
        `;
        
        chatContainer.appendChild(bubble);
    });
    
    scrollChatToBottom();
}

function renderBubbleRecommendations(recommendations) {
    if (!recommendations || recommendations.length === 0) return "";
    
    let cardsHtml = "";
    recommendations.forEach(rec => {
        const isAdded = state.basket.some(item => item.code === rec.name.toUpperCase());
        const addBtnLabel = isAdded ? "✓ Added" : "+ Add to Spec";
        const addBtnClass = isAdded ? "chat-rec-btn-add active" : "chat-rec-btn-add";
        
        cardsHtml += `
            <div class="chat-rec-card">
                <div class="chat-rec-header">
                    <span class="chat-rec-name">${escapeHTML(rec.name)}</span>
                    <span class="chat-rec-badge ${rec.test_type.toLowerCase()}">${rec.test_type}</span>
                </div>
                <div class="chat-rec-actions">
                    <button class="${addBtnClass}" onclick="handleRecCardAdd('${escapeJS(rec.name)}', '${rec.test_type}', '${escapeJS(rec.url)}')">${addBtnLabel}</button>
                    <a class="chat-rec-btn chat-rec-btn-link" href="${rec.url}" target="_blank">Portal ↗</a>
                </div>
            </div>
        `;
    });
    
    return `<div class="chat-recs-block">${cardsHtml}</div>`;
}

function renderCatalog() {
    const scroller = document.getElementById("catalog-scroller");
    scroller.innerHTML = "";
    
    const activeTab = document.querySelector(".catalog-tab.active").getAttribute("data-tab");
    const searchQuery = document.getElementById("catalog-search").value.toLowerCase();
    
    let filtered = state.flattenedCatalog;
    
    // Apply Category Tab Filter
    if (activeTab !== "all") {
        filtered = filtered.filter(item => item.type === activeTab);
    }
    
    // Apply Search Filter
    if (searchQuery.trim().length > 0) {
        filtered = filtered.filter(item => {
            return item.name.toLowerCase().includes(searchQuery) ||
                   item.code.toLowerCase().includes(searchQuery) ||
                   item.description.toLowerCase().includes(searchQuery) ||
                   item.domain.toLowerCase().includes(searchQuery) ||
                   (item.skills && item.skills.some(s => s.toLowerCase().includes(searchQuery))) ||
                   (item.dimensions && item.dimensions.some(d => d.toLowerCase().includes(searchQuery))) ||
                   (item.subtests && item.subtests.some(s => s.toLowerCase().includes(searchQuery))) ||
                   (item.use_cases && item.use_cases.some(u => u.toLowerCase().includes(searchQuery)));
        });
    }
    
    if (filtered.length === 0) {
        scroller.innerHTML = `<div style="font-size:0.8rem; color:var(--text-muted); text-align:center; padding:2rem;">No matching assessments found.</div>`;
        return;
    }
    
    filtered.forEach(assessment => {
        const card = document.createElement("div");
        card.className = "catalog-card";
        
        // Build sub-elements tags
        let tagsHtml = "";
        if (assessment.skills) {
            assessment.skills.forEach(s => tagsHtml += `<span class="card-tag card-tag-skills">${escapeHTML(s)}</span>`);
        }
        if (assessment.dimensions) {
            assessment.dimensions.forEach(d => tagsHtml += `<span class="card-tag card-tag-usecases">${escapeHTML(d)}</span>`);
        }
        if (assessment.subtests) {
            assessment.subtests.forEach(s => tagsHtml += `<span class="card-tag card-tag-skills">${escapeHTML(s)}</span>`);
        }
        if (assessment.seniority) {
            assessment.seniority.forEach(s => tagsHtml += `<span class="card-tag card-tag-seniority">${escapeHTML(s)}</span>`);
        }
        if (assessment.use_cases) {
            assessment.use_cases.forEach(u => tagsHtml += `<span class="card-tag card-tag-usecases">${escapeHTML(u)}</span>`);
        }
        
        const isAdded = state.basket.some(b => b.code === assessment.code);
        const addBtnLabel = isAdded ? "✓ Added to Shortlist" : "+ Add to Shortlist";
        
        card.innerHTML = `
            <div class="card-header-row" onclick="toggleCatalogCardExpand(this.parentNode)">
                <div class="card-title-group">
                    <div class="card-name-line">
                        <span class="card-name">${escapeHTML(assessment.name)}</span>
                        <span class="card-code">${assessment.code}</span>
                    </div>
                    <span class="card-domain">${escapeHTML(assessment.domain)}</span>
                </div>
                <div class="card-arrow">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                </div>
            </div>
            <div class="card-expand-body">
                <p class="card-desc">${escapeHTML(assessment.description)}</p>
                <div class="card-tags">${tagsHtml}</div>
                <div class="card-bottom-actions">
                    <button class="btn btn-primary" style="flex:1; padding:0.35rem 0.5rem; font-size:0.75rem;" onclick="handleRecCardAdd('${escapeJS(assessment.name)}', '${assessment.type}', '${escapeJS(assessment.url)}')">${addBtnLabel}</button>
                    <a class="btn btn-secondary" style="padding:0.35rem 0.5rem; font-size:0.75rem;" href="${assessment.url}" target="_blank">SHL Portal ↗</a>
                </div>
            </div>
        `;
        
        scroller.appendChild(card);
    });
}

function renderBasket() {
    const scroller = document.getElementById("basket-scroller");
    scroller.innerHTML = "";
    
    if (state.basket.length === 0) {
        scroller.innerHTML = `
            <div class="basket-empty-state">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color:var(--text-muted);"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path><line x1="3" y1="6" x2="21" y2="6"></line><path d="M16 10a4 4 0 0 1-8 0"></path></svg>
                <span>Shortlist Spec Basket is Empty</span>
                <span style="font-size:0.7rem; color:var(--text-muted)">Add assessments from advisor suggestions or catalog explorer</span>
            </div>
        `;
        return;
    }
    
    state.basket.forEach((item, index) => {
        const card = document.createElement("div");
        card.className = "basket-item";
        
        card.innerHTML = `
            <div class="basket-item-header">
                <span class="basket-item-name">${escapeHTML(item.name)}</span>
                <div class="basket-item-remove" onclick="removeBasketItem('${item.code}')" title="Remove">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </div>
            </div>
            <textarea class="basket-item-why" placeholder="Explain reasoning/why selected..." oninput="updateBasketItemReason(${index}, this.value)">${escapeHTML(item.why_selected || "")}</textarea>
        `;
        
        scroller.appendChild(card);
    });
}

function updateCompetencyChart() {
    const barsContainer = document.getElementById("competency-bars");
    barsContainer.innerHTML = "";
    
    // Core competencies to display
    const competencies = [
        { name: "Technical & Practical", key: "K", score: 0 },
        { name: "Personality & Team Fit", key: "P", score: 0 },
        { name: "General Cognitive Reasoning", key: "A", score: 0 },
        { name: "Industry Aptitude & Support", key: "I", score: 0 }
    ];
    
    // Calculate competency coverage based on items in the basket
    state.basket.forEach(item => {
        const match = competencies.find(c => c.key === item.type);
        if (match) {
            match.score += 25; // Increase coverage weight per test type
        }
    });
    
    // Render SVGs / Bars
    competencies.forEach(comp => {
        const finalScore = Math.min(comp.score, 100);
        
        const barItem = document.createElement("div");
        barItem.className = "competency-item";
        
        barItem.innerHTML = `
            <div class="competency-header">
                <span>${comp.name}</span>
                <span class="competency-header-val">${finalScore}%</span>
            </div>
            <div class="competency-bar-bg">
                <div class="competency-bar-fill" style="width: ${finalScore}%"></div>
            </div>
        `;
        
        barsContainer.appendChild(barItem);
    });
}

function updateTurnCounter(turnCount, status) {
    const fill = document.getElementById("progress-fill");
    const text = document.getElementById("progress-text");
    
    const fillPct = (turnCount / 8) * 100;
    fill.style.width = `${fillPct}%`;
    text.innerText = `${turnCount}/8`;
    
    // Update stage text
    const stageText = document.getElementById("stage-text");
    stageText.innerText = status;
}

// ----------------------------------------------------
// Event Handlers
// ----------------------------------------------------

async function handleUserMessageSubmit() {
    const chatInput = document.getElementById("chat-input");
    const content = chatInput.value.trim();
    if (!content) return;
    
    chatInput.value = "";
    
    // Append user message instantly to local screen
    appendTempChatMessage("user", content);
    
    // Render typing dots
    showTypingIndicator();
    
    try {
        const response = await fetch(`${API_BASE}/sessions/${state.activeSessionId}/message`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ role: "user", content: content })
        });
        
        const data = await response.json();
        
        removeTypingIndicator();
        
        // Refresh session from server
        await selectSession(state.activeSessionId);
        await fetchSessions(); // Refresh title updates
    } catch (e) {
        removeTypingIndicator();
        console.error("Failed to post message:", e);
        appendTempChatMessage("assistant", "I encountered an error connecting to the backend. Please check if your server is running.");
    }
}

function handleRecCardAdd(name, type, url) {
    const code = state.flattenedCatalog.find(c => c.name === name)?.code || name.toUpperCase();
    
    const exists = state.basket.some(item => item.code === code);
    if (exists) {
        // Remove it (Toggle behavior)
        removeBasketItem(code);
    } else {
        // Add to basket
        state.basket.push({
            name: name,
            code: code,
            type: type,
            url: url,
            why_selected: ""
        });
        
        renderBasket();
        updateCompetencyChart();
        renderCatalog(); // Refresh catalog button toggles
        
        // Also refresh chat cards state
        const chatContainer = document.getElementById("chat-messages");
        const scrollPos = chatContainer.scrollTop;
        const activeSession = state.sessions.find(s => s.id === state.activeSessionId);
        if (activeSession) {
            selectSession(state.activeSessionId).then(() => {
                chatContainer.scrollTop = scrollPos;
            });
        }
    }
}

function removeBasketItem(code) {
    state.basket = state.basket.filter(item => item.code !== code);
    renderBasket();
    updateCompetencyChart();
    renderCatalog();
    
    // Refresh chat list to update card buttons
    const chatContainer = document.getElementById("chat-messages");
    const scrollPos = chatContainer.scrollTop;
    selectSession(state.activeSessionId).then(() => {
        chatContainer.scrollTop = scrollPos;
    });
}

function updateBasketItemReason(index, value) {
    if (state.basket[index]) {
        state.basket[index].why_selected = value;
    }
}

function handleCatalogSearch() {
    renderCatalog();
}

function toggleCatalogCardExpand(cardElement) {
    // Collapse all other expanded cards first
    document.querySelectorAll(".catalog-card").forEach(card => {
        if (card !== cardElement) card.classList.remove("expanded");
    });
    
    cardElement.classList.toggle("expanded");
}

// Save Shortlist to SQLite Campaigns Specs
async function handleSaveCampaign() {
    if (state.basket.length === 0) {
        alert("Please add at least one assessment to your Campaign Shortlist basket first!");
        return;
    }
    
    if (!state.campaignMetadata.role) {
        alert("Please enter a target Job Role (e.g. Senior Java Engineer) before saving!");
        return;
    }
    
    const itemsPayload = state.basket.map(b => ({
        assessment_name: b.name,
        assessment_code: b.code,
        assessment_type: b.type,
        assessment_url: b.url,
        why_selected: b.why_selected || `Fulfills competencies needed for ${state.campaignMetadata.role}.`
    }));
    
    // Auto generate target skills from test types
    const targetSkills = state.basket.map(b => TEST_TYPE_MAPPING[b.type]);
    const uniqueSkills = [...new Set(targetSkills)];
    
    const notesMarkdown = generateCampaignNotesMarkdown(uniqueSkills);
    
    const payload = {
        title: state.campaignMetadata.title || `Campaign Spec for ${state.campaignMetadata.role}`,
        role_name: state.campaignMetadata.role,
        seniority: state.campaignMetadata.seniority,
        target_skills: uniqueSkills,
        notes: notesMarkdown,
        items: itemsPayload
    };
    
    try {
        const response = await fetch(`${API_BASE}/campaigns`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            const savedCampaign = await response.json();
            alert("Campaign Specification finalized and saved successfully in database!");
            await fetchCampaigns();
            previewCampaignMarkdown(savedCampaign.id);
        } else {
            const err = await response.json();
            alert(`Failed to save: ${err.detail}`);
        }
    } catch (e) {
        console.error("Save campaign error:", e);
    }
}

// ----------------------------------------------------
// Markdown Generation & Previews
// ----------------------------------------------------

function generateCampaignNotesMarkdown(uniqueSkills) {
    let md = `# SHL Assessment Campaign Specification\n\n`;
    md += `**Campaign Title**: ${state.campaignMetadata.title}\n`;
    md += `**Target Job Role**: ${state.campaignMetadata.role}\n`;
    md += `**Target Seniority**: ${state.campaignMetadata.seniority}\n\n`;
    md += `## 🎯 Target Competency Coverage\n`;
    uniqueSkills.forEach(skill => md += `- ${skill}\n`);
    md += `\n## 📋 Selection Rationale\n`;
    
    state.basket.forEach(item => {
        md += `### ${item.name} (${item.code})\n`;
        md += `- **Type**: ${TEST_TYPE_MAPPING[item.type]}\n`;
        md += `- **URL**: ${item.url}\n`;
        md += `- **Justification**: ${item.why_selected || "Fits candidate profile requirements."}\n\n`;
    });
    
    md += `---\n*Generated by SHL Assessment Advisor Service*`;
    return md;
}

async function previewCampaignMarkdown(campaignId) {
    try {
        const response = await fetch(`${API_BASE}/campaigns/${campaignId}`);
        const campaign = await response.json();
        
        const previewContainer = document.getElementById("markdown-preview-content");
        previewContainer.innerHTML = `
            <div style="display:flex; justify-content:space-between; margin-bottom:1rem;">
                <strong>Role: ${escapeHTML(campaign.role_name)} (Seniority: ${campaign.seniority})</strong>
                <span style="color:var(--text-secondary); font-size:0.75rem;">Created: ${new Date(campaign.created_at).toLocaleString()}</span>
            </div>
            <pre>${escapeHTML(campaign.notes || "")}</pre>
        `;
        
        document.getElementById("spec-modal").style.display = "flex";
    } catch (e) {
        console.error("Failed to preview campaign:", e);
    }
}

// ----------------------------------------------------
// Utility Functions
// ----------------------------------------------------

function appendTempChatMessage(role, content) {
    const chatContainer = document.getElementById("chat-messages");
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${role}`;
    const avatarLetter = role === "assistant" ? "🤖" : "👤";
    
    bubble.innerHTML = `
        <div class="avatar">${avatarLetter}</div>
        <div class="message-content">
            <p>${escapeHTML(content)}</p>
        </div>
    `;
    
    chatContainer.appendChild(bubble);
    scrollChatToBottom();
}

function showTypingIndicator() {
    const chatContainer = document.getElementById("chat-messages");
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble assistant typing-bubble";
    bubble.id = "chat-typing-indicator";
    
    bubble.innerHTML = `
        <div class="avatar">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        </div>
    `;
    
    chatContainer.appendChild(bubble);
    scrollChatToBottom();
}

function removeTypingIndicator() {
    const el = document.getElementById("chat-typing-indicator");
    if (el) el.remove();
}

function scrollChatToBottom() {
    const chatContainer = document.getElementById("chat-messages");
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function escapeHTML(str) {
    if (!str) return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function escapeJS(str) {
    if (!str) return "";
    return str.replace(/'/g, "\\'");
}

function formatMarkdown(text) {
    if (!text) return "";
    
    let html = escapeHTML(text);
    
    // Bold parsing (**text**)
    html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    
    // Lists formatting
    html = html.replace(/^\s*-\s+(.*?)$/gm, "<li>$1</li>");
    html = html.replace(/(<li>.*?<\/li>)/gs, "<ul>$1</ul>");
    
    // Fix nesting ul in ul
    html = html.replace(/<\/ul>\s*<ul>/g, "");
    
    // Newlines parsing
    html = html.replace(/\n/g, "<br>");
    
    return html;
}
