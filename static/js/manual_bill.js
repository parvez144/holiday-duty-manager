document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('items-body');
    const addRowBtn = document.getElementById('add-row-btn');
    const grandTotalVal = document.getElementById('grand-total-val');
    
    // Load initial data if editing
    if (INITIAL_BILL_DATA && INITIAL_BILL_DATA.items && INITIAL_BILL_DATA.items.length > 0) {
        document.getElementById('bill-title').value = INITIAL_BILL_DATA.title;
        document.getElementById('bill-date').value = INITIAL_BILL_DATA.bill_date;
        document.getElementById('bill-prepared-by').value = INITIAL_BILL_DATA.prepared_by;
        
        INITIAL_BILL_DATA.items.forEach(item => {
            addRow(item);
        });
    } else {
        // Add one empty row by default
        addRow();
    }

    addRowBtn.addEventListener('click', () => addRow());

    function addRow(data = {}) {
        const tr = document.createElement('tr');
        
        tr.innerHTML = `
            <td>
                <div class="input-group-relative">
                    <input type="text" class="input-emp-id" placeholder="ID" value="${data.emp_id || ''}" autocomplete="off">
                    <div class="autocomplete-results"></div>
                </div>
            </td>
            <td><input type="text" class="input-name" placeholder="Name" value="${data.name || ''}" required></td>
            <td><input type="text" class="input-desig" placeholder="Designation" value="${data.designation || ''}"></td>
            <td><textarea class="input-desc" placeholder="Duty description..." rows="1">${data.description || ''}</textarea></td>
            <td><input type="number" class="input-qty" value="${data.qty || 1}" step="0.5" min="0"></td>
            <td><input type="number" class="input-rate" value="${data.rate || 0}" step="0.01" min="0"></td>
            <td class="amount-cell">0.00</td>
            <td><button class="btn-rm-row" title="Remove"><i class="fas fa-times"></i></button></td>
        `;
        
        tableBody.appendChild(tr);
        
        setupRowEvents(tr);
        calculateRowAmount(tr);
    }

    function setupRowEvents(tr) {
        const qtyInput = tr.querySelector('.input-qty');
        const rateInput = tr.querySelector('.input-rate');
        const empIdInput = tr.querySelector('.input-emp-id');
        const nameInput = tr.querySelector('.input-name');
        const desigInput = tr.querySelector('.input-desig');
        const rmBtn = tr.querySelector('.btn-rm-row');
        const resultsBox = tr.querySelector('.autocomplete-results');
        
        qtyInput.addEventListener('input', () => calculateRowAmount(tr));
        rateInput.addEventListener('input', () => calculateRowAmount(tr));
        
        rmBtn.addEventListener('click', () => {
            tr.remove();
            calculateGrandTotal();
        });

        // Autocomplete logic
        let debounceTimer;
        empIdInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();
            if (query.length < 1) {
                resultsBox.style.display = 'none';
                return;
            }
            
            debounceTimer = setTimeout(async () => {
                try {
                    const res = await fetch(`/api/reports/employees/search?q=${encodeURIComponent(query)}`);
                    const data = await res.json();
                    
                    resultsBox.innerHTML = '';
                    if (data.length > 0) {
                        data.forEach(emp => {
                            const div = document.createElement('div');
                            div.className = 'autocomplete-item';
                            div.textContent = `${emp.id} - ${emp.name}`;
                            div.addEventListener('click', () => {
                                empIdInput.value = emp.id;
                                nameInput.value = emp.name;
                                desigInput.value = emp.designation;
                                resultsBox.style.display = 'none';
                            });
                            resultsBox.appendChild(div);
                        });
                        resultsBox.style.display = 'block';
                    } else {
                        resultsBox.style.display = 'none';
                    }
                } catch (err) {
                    console.error("Error fetching employees", err);
                }
            }, 300);
        });

        // Close autocomplete when clicking outside
        document.addEventListener('click', (e) => {
            if (!empIdInput.contains(e.target) && !resultsBox.contains(e.target)) {
                resultsBox.style.display = 'none';
            }
        });
    }

    function calculateRowAmount(tr) {
        const qty = parseFloat(tr.querySelector('.input-qty').value) || 0;
        const rate = parseFloat(tr.querySelector('.input-rate').value) || 0;
        const amt = qty * rate;
        tr.querySelector('.amount-cell').textContent = amt.toFixed(2);
        // store the raw value as dataset
        tr.dataset.amount = amt;
        calculateGrandTotal();
    }

    function calculateGrandTotal() {
        let total = 0;
        const rows = document.querySelectorAll('#items-body tr');
        rows.forEach(tr => {
            total += parseFloat(tr.dataset.amount || 0);
        });
        grandTotalVal.textContent = total.toFixed(2);
    }
});

async function saveBill(printAfterSave = false) {
    const title = document.getElementById('bill-title').value.trim();
    const date = document.getElementById('bill-date').value;
    const preparedBy = document.getElementById('bill-prepared-by').value.trim();
    
    if (!title || !date) {
        alert("Please enter Bill Title and Date.");
        return;
    }

    const items = [];
    const rows = document.querySelectorAll('#items-body tr');
    let hasInvalidRow = false;

    rows.forEach(tr => {
        const name = tr.querySelector('.input-name').value.trim();
        if (!name) {
            hasInvalidRow = true;
            tr.querySelector('.input-name').style.borderBottom = '1px solid #ef4444';
            return;
        } else {
            tr.querySelector('.input-name').style.borderBottom = '';
        }
        
        items.push({
            emp_id: tr.querySelector('.input-emp-id').value.trim(),
            name: name,
            designation: tr.querySelector('.input-desig').value.trim(),
            description: tr.querySelector('.input-desc').value.trim(),
            qty: parseFloat(tr.querySelector('.input-qty').value) || 0,
            rate: parseFloat(tr.querySelector('.input-rate').value) || 0,
            amount: parseFloat(tr.dataset.amount || 0)
        });
    });

    if (hasInvalidRow) {
        alert("Please fill in all employee names.");
        return;
    }

    if (items.length === 0) {
        alert("Please add at least one item.");
        return;
    }

    const payload = {
        id: typeof BILL_ID !== 'undefined' && BILL_ID ? BILL_ID : null,
        title: title,
        bill_date: date,
        prepared_by: preparedBy,
        items: items
    };

    try {
        const saveBtn = document.getElementById('save-btn');
        const origText = saveBtn.innerHTML;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        saveBtn.disabled = true;

        const res = await fetch('/manual_bill/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await res.json();
        if (result.success) {
            if (printAfterSave) {
                window.open(`/manual_bill/pdf/${result.id}`, '_blank');
            }
            window.location.href = '/manual_bill';
        } else {
            alert("Failed to save bill: " + (result.error || "Unknown error"));
        }
    } catch (err) {
        console.error("Save error:", err);
        alert("An error occurred while saving.");
    } finally {
        const saveBtn = document.getElementById('save-btn');
        saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Bill';
        saveBtn.disabled = false;
    }
}
