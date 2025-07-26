# 📦 Inventory Management System

A web-based inventory management system that works with Excel files (ISSUES.xlsx) to track material issues, receipts, and returns.

## Features

- ✅ Load existing ISSUES.xlsx files or create new ones
- ✅ Add transactions: Issue, Receive, or Return materials
- ✅ Automatic balance calculation
- ✅ Material name suggestions from existing data
- ✅ Real-time data display and summary
- ✅ Download updated Excel files
- ✅ Low stock alerts

## How to Use

### 1. Opening the Application
- Open `index.html` in your web browser
- The system will automatically create a new Excel structure

### 2. Loading an Existing ISSUES.xlsx File
- Click "📁 Load ISSUES.xlsx" button
- Select your existing Excel file
- The system will load all data and show it in the table

### 3. Adding Transactions
Fill out the form with:
- **Material Name**: Enter the name of the material (suggestions will appear from existing materials)
- **Transaction Type**: Choose from:
  - **Issued**: Material given out (reduces balance)
  - **Received**: Material received into inventory (increases balance)
  - **Return**: Material returned to inventory (increases balance)
- **Quantity**: Enter the amount
- **Date**: Select the transaction date

Click "Add Transaction" to save.

### 4. Excel File Structure
The system works with the following columns in Sheet1:
- **Column A**: Material Name
- **Column B**: Date
- **Column C**: Issued (total issued quantity)
- **Column D**: Received (total received quantity)
- **Column E**: Return (total returned quantity)
- **Column F**: Balance (automatically calculated: Received + Return - Issued)

### 5. Downloading Files
- Click "💾 Download Updated File" to save the current data as ISSUES.xlsx
- The file will be downloaded to your default download folder

### 6. Creating New Files
- Click "📄 Create New File" to start fresh with an empty inventory

## Data Management

- **Balance Calculation**: Automatically calculated as (Received + Return - Issued)
- **Material Tracking**: Each material has one row that accumulates all transactions
- **Low Stock Alerts**: Items with balance < 10 are flagged in the summary
- **Data Persistence**: All changes are maintained in memory until you download the file

## Browser Compatibility

Works with modern browsers that support:
- HTML5 File API
- ES6 JavaScript features
- CSS Grid

## File Format Support

- ✅ .xlsx files (Excel 2007+)
- ✅ .xls files (Excel 97-2003)

## Tips

1. **Material Names**: Use consistent naming for materials to avoid duplicates
2. **Date Format**: The system uses your browser's default date format
3. **Backup**: Always keep backups of your original ISSUES.xlsx files
4. **Large Files**: The system handles large inventories efficiently in memory

## Troubleshooting

- **File Won't Load**: Ensure the file is a valid Excel format (.xlsx or .xls)
- **Missing Data**: Check that your Excel file has data in Sheet1
- **Download Issues**: Make sure your browser allows file downloads
- **Form Not Submitting**: Ensure all fields are filled out correctly

## GitHub Deployment

To deploy this system to GitHub Pages:

1. Create a new repository on GitHub
2. Upload all files (index.html, styles.css, script.js, README.md)
3. Go to repository Settings → Pages
4. Select "Deploy from a branch" and choose "main"
5. Your site will be available at: `https://yourusername.github.io/repositoryname`

---

**Note**: This system runs entirely in the browser and doesn't require a server. All Excel processing is done client-side using the SheetJS library.
