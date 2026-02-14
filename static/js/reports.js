const dateEl = document.getElementById('date-select');
const sectionEl = document.getElementById('section-select');
const subSectionEl = document.getElementById('sub-section-select');
const catEl = document.getElementById('category-select');
const searchBtn = document.getElementById('btn-fetch');
const tableBody = document.getElementById('report-body');
const fetchSpinner = document.getElementById('fetch-spinner');

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
            tableBody.innerHTML = '<tr><td colspan="8" class="empty-state">No attendance found for this day.</td></tr>';
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
        // Open PDF in a new tab
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
        // Download Excel file
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

sectionEl.addEventListener('change', updateSubSections);
searchBtn.addEventListener('click', generateReport);
document.getElementById('btn-pdf').addEventListener('click', () => downloadReport('pdf'));
document.getElementById('btn-excel').addEventListener('click', () => downloadReport('excel'));

window.addEventListener('load', loadFilters);
