// Global variables
let workbook = null;
let inventoryData = [];
let materialNames = new Set();

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Set current date as default
    document.getElementById('date').valueAsDate = new Date();
    
    // Set up event listeners
    document.getElementById('fileInput').addEventListener('change', handleFileSelect);
    document.getElementById('inventoryForm').addEventListener('submit', handleFormSubmit);
    
    // Create new file by default
    createNewFile();
});

// Handle Excel file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                workbook = XLSX.read(e.target.result, {type: 'binary'});
                loadWorksheetData();
                displayData();
                updateMaterialList();
                showMessage('File loaded successfully!', 'success');
            } catch (error) {
                showMessage('Error reading file: ' + error.message, 'error');
            }
        };
        reader.readAsBinaryString(file);
    }
}

// Load data from the worksheet
function loadWorksheetData() {
    const sheetName = 'Sheet1';
    if (workbook.SheetNames.includes(sheetName)) {
        const worksheet = workbook.Sheets[sheetName];
        inventoryData = XLSX.utils.sheet_to_json(worksheet, {header: 1});
        
        // Extract material names from the data
        materialNames.clear();
        if (inventoryData.length > 1) {
            for (let i = 1; i < inventoryData.length; i++) {
                if (inventoryData[i][0]) {
                    materialNames.add(inventoryData[i][0]);
                }
            }
        }
    }
}

// Create a new Excel file structure
function createNewFile() {
    // Create new workbook
    workbook = XLSX.utils.book_new();
    
    // Create initial data structure
    inventoryData = [
        ['Material Name', 'Date', 'Issued', 'Received', 'Return', 'Balance']
    ];
    
    // Create worksheet and add to workbook
    const worksheet = XLSX.utils.aoa_to_sheet(inventoryData);
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');
    
    displayData();
    showMessage('New file created successfully!', 'success');
}

// Handle form submission
function handleFormSubmit(event) {
    event.preventDefault();
    
    const materialName = document.getElementById('materialName').value.trim();
    const transactionType = document.getElementById('transactionType').value;
    const quantity = parseInt(document.getElementById('quantity').value);
    const date = document.getElementById('date').value;
    
    if (!materialName || !transactionType || !quantity || !date) {
        showMessage('Please fill in all fields', 'error');
        return;
    }
    
    addTransaction(materialName, date, transactionType, quantity);
    
    // Reset form
    document.getElementById('inventoryForm').reset();
    document.getElementById('date').valueAsDate = new Date();
    
    showMessage('Transaction added successfully!', 'success');
}

// Add transaction to the inventory
function addTransaction(materialName, date, transactionType, quantity) {
    // Find existing row for this material
    let existingRowIndex = -1;
    for (let i = 1; i < inventoryData.length; i++) {
        if (inventoryData[i][0] === materialName) {
            existingRowIndex = i;
            break;
        }
    }
    
    if (existingRowIndex === -1) {
        // Create new row for this material
        const newRow = [materialName, date, 0, 0, 0, 0];
        inventoryData.push(newRow);
        existingRowIndex = inventoryData.length - 1;
    }
    
    // Update the appropriate column based on transaction type
    const row = inventoryData[existingRowIndex];
    row[1] = date; // Update date
    
    switch (transactionType) {
        case 'Issued':
            row[2] = (row[2] || 0) + quantity;
            break;
        case 'Received':
            row[3] = (row[3] || 0) + quantity;
            break;
        case 'Return':
            row[4] = (row[4] || 0) + quantity;
            break;
    }
    
    // Calculate balance: Received + Return - Issued
    row[5] = (row[3] || 0) + (row[4] || 0) - (row[2] || 0);
    
    // Update material names set
    materialNames.add(materialName);
    
    // Update worksheet
    const worksheet = XLSX.utils.aoa_to_sheet(inventoryData);
    workbook.Sheets['Sheet1'] = worksheet;
    
    // Refresh display
    displayData();
    updateMaterialList();
    displaySummary();
}

// Display the current data
function displayData() {
    const dataDisplay = document.getElementById('dataDisplay');
    
    if (inventoryData.length <= 1) {
        dataDisplay.innerHTML = '<p>No inventory data available</p>';
        return;
    }
    
    let html = '<table border="1" style="width: 100%; border-collapse: collapse;">';
    
    // Add header row
    html += '<tr style="background-color: #f0f0f0;">';
    for (let j = 0; j < inventoryData[0].length; j++) {
        html += `<th style="padding: 8px; text-align: left;">${inventoryData[0][j]}</th>`;
    }
    html += '</tr>';
    
    // Add data rows
    for (let i = 1; i < inventoryData.length; i++) {
        html += '<tr>';
        for (let j = 0; j < inventoryData[i].length; j++) {
            const cellValue = inventoryData[i][j] || 0;
            const cellColor = (j === 5 && cellValue < 0) ? 'color: red;' : '';
            html += `<td style="padding: 8px; ${cellColor}">${cellValue}</td>`;
        }
        html += '</tr>';
    }
    
    html += '</table>';
    dataDisplay.innerHTML = html;
}

// Update material name suggestions
function updateMaterialList() {
    const materialList = document.getElementById('materialList');
    materialList.innerHTML = '';
    
    materialNames.forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        materialList.appendChild(option);
    });
}

// Display inventory summary
function displaySummary() {
    const summaryDisplay = document.getElementById('summaryDisplay');
    
    if (inventoryData.length <= 1) {
        summaryDisplay.innerHTML = '<p>No data for summary</p>';
        return;
    }
    
    let totalMaterials = inventoryData.length - 1;
    let totalIssued = 0;
    let totalReceived = 0;
    let totalReturned = 0;
    let lowStockItems = 0;
    
    for (let i = 1; i < inventoryData.length; i++) {
        totalIssued += inventoryData[i][2] || 0;
        totalReceived += inventoryData[i][3] || 0;
        totalReturned += inventoryData[i][4] || 0;
        
        if ((inventoryData[i][5] || 0) < 10) {
            lowStockItems++;
        }
    }
    
    const html = `
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
            <div style="background: #e8f5e8; padding: 15px; border-radius: 5px;">
                <h3>📊 Overall Statistics</h3>
                <p><strong>Total Materials:</strong> ${totalMaterials}</p>
                <p><strong>Total Issued:</strong> ${totalIssued}</p>
                <p><strong>Total Received:</strong> ${totalReceived}</p>
                <p><strong>Total Returned:</strong> ${totalReturned}</p>
            </div>
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px;">
                <h3>⚠️ Alerts</h3>
                <p><strong>Low Stock Items:</strong> ${lowStockItems}</p>
                <p><em>(Items with balance < 10)</em></p>
            </div>
        </div>
    `;
    
    summaryDisplay.innerHTML = html;
}

// Download Excel file
function downloadExcel() {
    if (!workbook) {
        showMessage('No data to download', 'error');
        return;
    }
    
    XLSX.writeFile(workbook, 'ISSUES.xlsx');
    showMessage('File downloaded successfully!', 'success');
}

// Show message to user
function showMessage(message, type) {
    // Remove existing message
    const existingMessage = document.querySelector('.message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 1000;
        ${type === 'success' ? 'background-color: #28a745;' : 'background-color: #dc3545;'}
    `;
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    // Remove message after 3 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.parentNode.removeChild(messageDiv);
        }
    }, 3000);
}
