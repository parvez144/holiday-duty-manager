const dateEl = document.getElementById('date-select');
const sectionEl = document.getElementById('section-select');
const subSectionEl = document.getElementById('sub-section-select');
const catEl = document.getElementById('category-select');
const searchBtn = document.getElementById('btn-fetch');
const tableBody = document.getElementById('report-body');
const fetchSpinner = document.getElementById('fetch-spinner');

// Holiday Management Selectors
const holidayListBody = document.getElementById('holiday-list-body');
const newHDate = document.getElementById('new-h-date');
const newHName = document.getElementById('new-h-name');
const addHolidayBtn = document.getElementById('btn-add-holiday');

// Tab logic
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.getAttribute('data-tab');
        
        // Update buttons
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update content
        tabContents.forEach(content => {
            content.style.display = content.id === tabId ? 'block' : 'none';
        });

        if (tabId === 'holiday-tab') {
            loadHolidays();
        }
    });
});

async function loadFilters() {
    try {
        const [sections, categories] = await Promise.all([
            fetch('/api/reports/sections').then(r => r.json()),
            fetch('/api/reports/categories').then(r => r.json())
        ]);

        sections.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s;
            opt.textContent = s;
            sectionEl.appendChild(opt);
        });

        categories.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            catEl.appendChild(opt);
        });

        // Initialize sub-sections
        updateSubSections();
    } catch (err) {
        console.error("Failed to load filters", err);
    }
}

async function updateSubSections() {
    const section = sectionEl.value;
    try {
        const res = await fetch(`/api/reports/sub_sections?section=${encodeURIComponent(section)}`);
        const subSections = await res.json();

        // Clear existing options except the first one
        subSectionEl.innerHTML = '<option value="">All Sub-Sections</option>';

        subSections.forEach(ss => {
            const opt = document.createElement('option');
            opt.value = ss;
            opt.textContent = ss;
            subSectionEl.appendChild(opt);
        });
    } catch (err) {
        console.error("Failed to update sub-sections", err);
    }
}

async function generateReport() {
    const date = dateEl.value;
    if (!date) return alert("Please select a date");

    searchBtn.disabled = true;
    fetchSpinner.style.display = 'block';
    tableBody.innerHTML = '<tr><td colspan="8" class="empty-state">Loading data...</td></tr>';

    try {
        const res = await fetch('/api/reports/payment_sheet', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                date: date,
                section: sectionEl.value,
                sub_section: subSectionEl.value,
                category: catEl.value
            })
        });

        const data = await res.json();

        if (data.rows && data.rows.length > 0) {
            tableBody.innerHTML = data.rows.map(row => `
                <tr>
                    <td>${row.sl}</td>
                    <td>${row.id}</td>
                    <td>${row.name}</td>
                    <td>${row.section}</td>
                    <td>${row.in_time}</td>
                    <td>${row.out_time}</td>
                    <td>${row.hour} hrs</td>
                    <td>${row.amount}</td>
                </tr>
            `).join('');
        } else {
            tableBody.innerHTML = '<tr><td colspan="8" class="empty-state">No processed holiday data found for this day. Make sure you have added the holiday and clicked "Process" in the Holiday Management tab.</td></tr>';
        }
    } catch (err) {
        alert("Error fetching report data");
        tableBody.innerHTML = '<tr><td colspan="8" class="empty-state" style="color:#ef4444">Failed to load data.</td></tr>';
    } finally {
        searchBtn.disabled = false;
        fetchSpinner.style.display = 'none';
    }
}

function downloadReport(type) {
    const date = dateEl.value;
    if (!date) return alert("Please select a date");

    const payload = {
        date: date,
        section: sectionEl.value,
        sub_section: subSectionEl.value,
        category: catEl.value
    };

    if (type === 'pdf') {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/reports/payment_sheet/${type}`;
        form.target = '_blank';

        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'data';
        input.value = JSON.stringify(payload);

        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
    } else {
        fetch(`/reports/payment_sheet/${type}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(res => res.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `payment_sheet_${date}.xlsx`;
                document.body.append(a);
                a.click();
                a.remove();
            })
            .catch(err => alert(`Error downloading ${type}`));
    }
}

// Holiday Management Functions
async function loadHolidays() {
    try {
        const res = await fetch('/api/holidays');
        const holidays = await res.json();
        
        if (holidays.length === 0) {
            holidayListBody.innerHTML = '<tr><td colspan="5" class="empty-state">No holidays defined yet.</td></tr>';
            return;
        }

        holidayListBody.innerHTML = holidays.map(h => `
            <tr>
                <td>${h.date}</td>
                <td>${h.name}</td>
                <td><span class="badge badge-${h.status}">${h.status}</span></td>
                <td>${h.processed_at || 'Never'}</td>
                <td>
                    <div class="action-btns">
                        ${h.status === 'draft' ? `
                            <button onclick="processHoliday(${h.id})" class="btn-sm btn-process" title="Import data from iClock">
                                <i class="fas fa-sync"></i> Process
                            </button>
                            <button onclick="finalizeHoliday(${h.id})" class="btn-sm btn-finalize" title="Lock data for payment">
                                <i class="fas fa-lock"></i> Finalize
                            </button>
                            <button onclick="deleteHoliday(${h.id})" class="btn-sm btn-delete-sm">
                                <i class="fas fa-trash"></i>
                            </button>
                        ` : `
                            <span style="color: var(--accent); font-size: 0.8rem; margin-right: 0.5rem;"><i class="fas fa-check-circle"></i> Locked</span>
                            ${currentUserRole === 'Admin' ? `
                                <button onclick="deleteHoliday(${h.id})" class="btn-sm btn-delete-sm" title="Admin Force Delete">
                                    <i class="fas fa-trash"></i>
                                </button>
                            ` : ''}
                        `}
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (err) {
        console.error("Failed to load holidays", err);
    }
}

async function addHoliday() {
    const date = newHDate.value;
    const name = newHName.value;
    if (!date || !name) return alert("Please provide both date and description");

    try {
        const res = await fetch('/api/holidays', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ date, name })
        });
        const data = await res.json();
        if (data.error) return alert(data.error);
        
        newHName.value = '';
        loadHolidays();
    } catch (err) {
        alert("Failed to add holiday");
    }
}

async function processHoliday(id) {
    if (!confirm("This will fetch attendance data from iClock and replace any existing snapshot for this day. Proceed?")) return;
    
    try {
        const res = await fetch(`/api/holidays/${id}/process`, { method: 'POST' });
        const data = await res.json();
        alert(data.message || data.error);
        loadHolidays();
    } catch (err) {
        alert("Processing failed");
    }
}

async function finalizeHoliday(id) {
    if (!confirm("Are you sure? Finalizing will lock the data and prevent any further changes or re-processing.")) return;
    
    try {
        const res = await fetch(`/api/holidays/${id}/finalize`, { method: 'POST' });
        loadHolidays();
    } catch (err) {
        alert("Finalization failed");
    }
}

async function deleteHoliday(id) {
    if (!confirm("Delete this holiday and all its snapshot data?")) return;
    
    try {
        await fetch(`/api/holidays/${id}`, { method: 'DELETE' });
        loadHolidays();
    } catch (err) {
        alert("Deletion failed");
    }
}

// Event Listeners
sectionEl.addEventListener('change', updateSubSections);
searchBtn.addEventListener('click', generateReport);
document.getElementById('btn-pdf').addEventListener('click', () => downloadReport('pdf'));
document.getElementById('btn-excel').addEventListener('click', () => downloadReport('excel'));
addHolidayBtn.addEventListener('click', addHoliday);

window.addEventListener('load', loadFilters);
