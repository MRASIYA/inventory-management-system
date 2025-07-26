import os
import logging
import shutil
from datetime import datetime
from pathlib import Path
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file, flash
from werkzeug.exceptions import RequestEntityTooLarge
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configuration
EXCEL_FILE = 'ISSUES.xlsx'
BACKUP_DIR = 'backups'
MAX_RETRIES = 3
RETRY_DELAY = 0.5

class InventoryManager:
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.backup_dir = Path(BACKUP_DIR)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self):
        """Create a backup of the Excel file"""
        try:
            if os.path.exists(self.excel_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.backup_dir / f"ISSUES_backup_{timestamp}.xlsx"
                shutil.copy2(self.excel_file, backup_file)
                logger.info(f"Backup created: {backup_file}")
                return str(backup_file)
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
        return None
    
    def load_materials(self):
        """Load materials from Excel file with error handling"""
        try:
            if not os.path.exists(self.excel_file):
                logger.warning(f"Excel file {self.excel_file} not found")
                return []
            
            df = pd.read_excel(self.excel_file, sheet_name='Sheet1')
            materials = df['Materials'].dropna().unique().tolist()
            logger.info(f"Loaded {len(materials)} materials from Excel")
            return materials
        except Exception as e:
            logger.error(f"Error loading materials: {e}")
            return []
    
    def get_current_stock(self):
        """Get current stock levels"""
        try:
            if not os.path.exists(self.excel_file):
                return {}
            
            df = pd.read_excel(self.excel_file, sheet_name='Sheet1')
            stock_data = {}
            
            for _, row in df.iterrows():
                material = row['Materials']
                if pd.notna(material):
                    issued = row.get('Issued', 0) or 0
                    received = row.get('Received', 0) or 0
                    returned = row.get('Return', 0) or 0
                    
                    # Convert to numeric, defaulting to 0 if conversion fails
                    try:
                        issued = float(issued) if pd.notna(issued) else 0
                        received = float(received) if pd.notna(received) else 0
                        returned = float(returned) if pd.notna(returned) else 0
                    except (ValueError, TypeError):
                        issued = received = returned = 0
                    
                    current_stock = received + returned - issued
                    
                    stock_data[material] = {
                        'issued': issued,
                        'received': received,
                        'returned': returned,
                        'current_stock': current_stock
                    }
            
            logger.info(f"Retrieved stock data for {len(stock_data)} materials")
            return stock_data
        except Exception as e:
            logger.error(f"Error getting current stock: {e}")
            return {}
    
    def save_transaction(self, material, transaction_type, quantity):
        """Save transaction with retry mechanism and backup"""
        for attempt in range(MAX_RETRIES):
            try:
                # Create backup before modification
                backup_file = self.create_backup()
                
                # Load the Excel file
                df = pd.read_excel(self.excel_file, sheet_name='Sheet1')
                
                # Find the row for the material
                material_row = df[df['Materials'] == material]
                if material_row.empty:
                    logger.warning(f"Material '{material}' not found in Excel file")
                    return False, f"Material '{material}' not found"
                
                row_index = material_row.index[0]
                
                # Determine the column based on transaction type
                column_mapping = {
                    'Issues': 'Issued',
                    'Received': 'Received',
                    'Return': 'Return'
                }
                
                column = column_mapping.get(transaction_type)
                if not column:
                    return False, f"Invalid transaction type: {transaction_type}"
                
                # Get current value and add the new quantity
                current_value = df.at[row_index, column]
                if pd.isna(current_value):
                    current_value = 0
                else:
                    try:
                        current_value = float(current_value)
                    except (ValueError, TypeError):
                        current_value = 0
                
                new_value = current_value + float(quantity)
                df.at[row_index, column] = new_value
                
                # Save the updated DataFrame back to Excel
                with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='w') as writer:
                    df.to_excel(writer, sheet_name='Sheet1', index=False)
                
                logger.info(f"Transaction saved: {material} - {transaction_type} - {quantity}")
                return True, f"Transaction saved successfully"
                
            except PermissionError:
                logger.warning(f"File permission error, attempt {attempt + 1}/{MAX_RETRIES}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return False, "File is locked. Please close Excel and try again."
            except Exception as e:
                logger.error(f"Error saving transaction (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return False, f"Error saving transaction: {str(e)}"
        
        return False, "Failed to save transaction after multiple attempts"

# Initialize inventory manager
inventory_manager = InventoryManager(EXCEL_FILE)

@app.route('/')
def index():
    """Main page"""
    try:
        materials = inventory_manager.load_materials()
        return render_template('index.html', materials=materials)
    except Exception as e:
        logger.error(f"Error loading index page: {e}")
        flash('Error loading materials. Please check the Excel file.', 'error')
        return render_template('index.html', materials=[])

@app.route('/api/materials')
def api_materials():
    """API endpoint to get materials"""
    try:
        materials = inventory_manager.load_materials()
        return jsonify({'materials': materials, 'status': 'success'})
    except Exception as e:
        logger.error(f"API error getting materials: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/stock')
def api_stock():
    """API endpoint to get current stock"""
    try:
        stock_data = inventory_manager.get_current_stock()
        return jsonify({'stock': stock_data, 'status': 'success'})
    except Exception as e:
        logger.error(f"API error getting stock: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/save_transaction', methods=['POST'])
def api_save_transaction():
    """API endpoint to save transaction"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided', 'status': 'error'}), 400
        
        material = data.get('material')
        transaction_type = data.get('transaction_type')
        quantity = data.get('quantity')
        
        # Validate input
        if not all([material, transaction_type, quantity]):
            return jsonify({'error': 'Missing required fields', 'status': 'error'}), 400
        
        try:
            quantity = float(quantity)
            if quantity <= 0:
                return jsonify({'error': 'Quantity must be positive', 'status': 'error'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid quantity format', 'status': 'error'}), 400
        
        success, message = inventory_manager.save_transaction(material, transaction_type, quantity)
        
        if success:
            logger.info(f"Transaction API success: {material} - {transaction_type} - {quantity}")
            return jsonify({'message': message, 'status': 'success'})
        else:
            logger.warning(f"Transaction API failed: {message}")
            return jsonify({'error': message, 'status': 'error'}), 500
            
    except Exception as e:
        logger.error(f"API error saving transaction: {e}")
        return jsonify({'error': f'Server error: {str(e)}', 'status': 'error'}), 500

@app.route('/download')
def download_file():
    """Download the Excel file"""
    try:
        if not os.path.exists(EXCEL_FILE):
            flash('Excel file not found', 'error')
            return "File not found", 404
        
        logger.info("Excel file downloaded")
        return send_file(EXCEL_FILE, as_attachment=True, download_name=f"ISSUES_{datetime.now().strftime('%Y%m%d')}.xlsx")
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        flash(f'Error downloading file: {str(e)}', 'error')
        return "Error downloading file", 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

@app.errorhandler(RequestEntityTooLarge)
def too_large(e):
    """Handle file too large errors"""
    return "File is too large", 413

if __name__ == '__main__':
    # Ensure required directories exist
    Path(BACKUP_DIR).mkdir(exist_ok=True)
    
    # Check if Excel file exists, create a sample if not
    if not os.path.exists(EXCEL_FILE):
        logger.warning("Excel file not found, creating sample file")
        sample_data = {
            'Materials': ['Sample Material 1', 'Sample Material 2', 'Sample Material 3'],
            'Issued': [0, 0, 0],
            'Received': [0, 0, 0],
            'Return': [0, 0, 0]
        }
        df = pd.DataFrame(sample_data)
        df.to_excel(EXCEL_FILE, sheet_name='Sheet1', index=False)
        logger.info("Sample Excel file created")
    
    logger.info("Starting Flask application")
    app.run(debug=False, host='127.0.0.1', port=5000)
