// Elements
const dateEl = document.getElementById('date-select');
const sectionEl = document.getElementById('section-select');
const subSectionEl = document.getElementById('sub-section-select');
const catEl = document.getElementById('category-select');
const statusEl = document.getElementById('status-select');
const searchBtn = document.getElementById('btn-fetch');
const pdfBtn = document.getElementById('btn-pdf');
const tableBody = document.getElementById('report-body');
const fetchSpinner = document.getElementById('fetch-spinner');

// Load Filters
function loadFilters() {
    fetch('/api/reports/sections')
        .then(res => res.json())
        .then(data => {
            data.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s;
                opt.textContent = s;
                sectionEl.appendChild(opt);
            });
            // After loading sections, update sub-sections
            updateSubSections();
        });

    fetch('/api/reports/categories')
        .then(res => res.json())
        .then(data => {
            data.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c;
                opt.textContent = c;
                catEl.appendChild(opt);
            });
        });
}

function updateSubSections() {
    const section = sectionEl.value;
    fetch(`/api/reports/sub_sections?section=${encodeURIComponent(section)}`)
        .then(res => res.json())
        .then(data => {
            // Clear existing options except default
            subSectionEl.innerHTML = '<option value="">All Sub-Sections</option>';
            data.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s;
                opt.textContent = s;
                subSectionEl.appendChild(opt);
            });
        });
}

function generateReport() {
    const date = dateEl.value;
    if (!date) return alert("Please select a date");

    const payload = {
        date: date,
        section: sectionEl.value,
        sub_section: subSectionEl.value,
        category: catEl.value,
        status: statusEl.value
    };

    searchBtn.disabled = true;
    fetchSpinner.style.display = 'block';

    fetch('/api/reports/present_status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
        .then(res => res.json())
        .then(data => {
            tableBody.innerHTML = '';
            if (!data.rows || data.rows.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="7" class="empty-state">No data found for the selected filters.</td></tr>';
            } else {
                data.rows.forEach(r => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                <td>${r.sl}</td>
                <td>${r.id}</td>
                <td>${r.name}</td>
                <td>${r.designation}</td>
                <td>${r.in_time}</td>
                <td>${r.out_time}</td>
                <td>${r.remarks || ''}</td>
            `;
                    tableBody.appendChild(row);
                });
            }
        })
        .catch(err => {
            console.error(err);
            alert("Failed to fetch report");
        })
        .finally(() => {
            searchBtn.disabled = false;
            fetchSpinner.style.display = 'none';
        });
}

function downloadPDF() {
    const date = dateEl.value;
    if (!date) return alert("Please select a date");

    const payload = {
        date: date,
        section: sectionEl.value,
        sub_section: subSectionEl.value,
        category: catEl.value,
        status: statusEl.value
    };

    // Open PDF in a new tab
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/reports/present_status/pdf`;
    form.target = '_blank';

    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'data';
    input.value = JSON.stringify(payload);

    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

loadFilters();
sectionEl.addEventListener('change', updateSubSections);
searchBtn.addEventListener('click', generateReport);
pdfBtn.addEventListener('click', downloadPDF);
