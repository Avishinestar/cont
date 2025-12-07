
let allData = [];
let recentData = [];
let archivedData = [];
const SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000;

document.addEventListener('DOMContentLoaded', () => {
    fetchData();
});

async function fetchData() {
    try {
        const response = await fetch('data.json');
        const data = await response.json();

        processData(data);
        updateCounts();
        switchTab('recent'); // Default tab
    } catch (error) {
        console.error("Error loading data:", error);
        document.getElementById('content-grid').innerHTML = '<p style="color:red; text-align:center;">Failed to load data.</p>';
    }
}

function processData(data) {
    allData = data;
    const now = new Date();

    recentData = data.filter(item => {
        const date = new Date(item.date);
        const diff = now - date;
        return diff <= SEVEN_DAYS_MS && diff >= 0;
    });

    archivedData = data.filter(item => {
        const date = new Date(item.date);
        const diff = now - date;
        return diff > SEVEN_DAYS_MS;
    });
}

function updateCounts() {
    document.getElementById('recent-count').textContent = recentData.length;
    document.getElementById('archive-count').textContent = archivedData.length;
}

window.switchTab = function (tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`.tab-btn[onclick="switchTab('${tabName}')"]`).classList.add('active');

    // Render content
    const dataToRender = tabName === 'recent' ? recentData : archivedData;
    renderGrid(dataToRender);
}

function renderGrid(data) {
    const grid = document.getElementById('content-grid');
    grid.innerHTML = '';

    if (data.length === 0) {
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 2rem;">No records found.</div>';
        return;
    }

    data.forEach((item, index) => {
        const card = createCard(item, index);
        grid.appendChild(card);
    });
}

function createCard(item, index) {
    const div = document.createElement('div');
    div.className = 'card';
    div.style.animationDelay = `${index * 0.05}s`; // Staggered animation

    const isWin = item.type.includes('Won') || item.type.includes('Order') || item.type.includes('L1');
    let badgeClass = isWin ? 'status-win' : 'status-bid';
    if (item.sentiment === 'negative') badgeClass = 'status-bid';

    // Emoji logic
    let sentimentEmoji = '';
    if (item.sentiment === 'positive') sentimentEmoji = '<span style="font-size: 1.2rem; margin-left: 0.5rem;" title="Positive Impact">👍</span>';
    else if (item.sentiment === 'negative') sentimentEmoji = '<span style="font-size: 1.2rem; margin-left: 0.5rem;" title="Negative Impact">👎</span>';

    // Format stats
    let amountVal = item.amount_cr ? (typeof item.amount_cr === 'number' ? `₹${item.amount_cr.toLocaleString()} Cr` : item.amount_cr) : 'N/A';
    let orderBookVal = item.order_book_cr ? item.order_book_cr : 'N/A';

    // Create Stats Section
    const statsHtml = `
        <div class="stats-container" style="display: flex; gap: 1rem; margin-top: 1rem;">
             <div class="stat-badge">
                <div class="stat-label">Deal Value</div>
                <div class="stat-value">${amountVal}</div>
             </div>
             <div class="stat-badge">
                <div class="stat-label">Total Order Book</div>
                <div class="stat-value">${orderBookVal}</div>
             </div>
        </div>
    `;

    div.innerHTML = `
        <div class="card-header">
            <div>
                <div class="company-name">
                    ${item.company} ${sentimentEmoji}
                </div>
                <div style="font-size: 0.9rem; color: var(--accent-blue); margin-top: 0.2rem;">
                    <span style="opacity: 0.7;">Client:</span> ${item.client}
                </div>
            </div>
            <span class="status-badge ${badgeClass}">${item.type}</span>
        </div>
        <div class="card-body">
            ${statsHtml}
            <div class="category-tag" style="margin-bottom: 0.5rem;">${item.category}</div>
            <p>${item.description}</p>
        </div>
        <div class="card-footer">
            <span class="date">📅 ${new Date(item.date).toLocaleDateString(undefined, {
        year: 'numeric', month: 'long', day: 'numeric'
    })}</span>
             <a href="${item.pdf_link}" target="_blank" style="text-decoration: none; display: flex; align-items: center; gap: 0.5rem; color: var(--primary); font-size: 0.9rem; font-weight: 600; padding: 0.3rem 0.8rem; border-radius: 5px; background: rgba(0, 242, 234, 0.1); transition: all 0.2s ease;">
                📄 View PDF
             </a>
        </div>
    `;
    return div;
}
