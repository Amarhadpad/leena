from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace this with a random and unique string

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
BOOKINGS_CSV = os.path.join(DATA_DIR, 'bookings.csv')

def read_bookings_from_csv():
    bookings = []
    try:
        with open(BOOKINGS_CSV, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert id to int for sorting and filtering
                row['id'] = int(row['id'])
                bookings.append(row)
    except FileNotFoundError:
        pass
    return bookings

# Routes for the website pages
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/services')
def services():
    return render_template('services.html')
@app.route('/tech')
def tech():
    return render_template('admin_login.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')
from flask import session, request

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "Admin" and password == "lolo@2025":
            session['logged_in'] = True
            flash('Login successful!', 'success')
            # Redirect to admin page after login
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password.', 'danger')
            return render_template('admin_login.html')
    else:
        # Show admin page directly without login check
        sort_by = request.args.get('sort_by', 'id')
        search_term = request.args.get('search', '').lower()

        bookings = read_bookings_from_csv()

        # Filter bookings by search term
        if search_term:
            bookings = [b for b in bookings if search_term in b['name'].lower() or search_term in b['contact_no'].lower() or search_term in b['service'].lower()]

        # Sort bookings
        if sort_by in ['id', 'name', 'service', 'service_date']:
            bookings = sorted(bookings, key=lambda x: x[sort_by])

        return render_template('admin.html', bookings=bookings)


# Separate route for admin dashboard page
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('admin'))

    sort_by = request.args.get('sort_by', 'id')
    search_term = request.args.get('search', '').lower()

    bookings = read_bookings_from_csv()

    # Filter bookings by search term
    if search_term:
        bookings = [b for b in bookings if search_term in b['name'].lower() or search_term in b['contact_no'].lower() or search_term in b['service'].lower()]

    # Sort bookings
    if sort_by in ['id', 'name', 'service', 'service_date']:
        bookings = sorted(bookings, key=lambda x: x[sort_by])

    return render_template('admin.html', bookings=bookings)


# Handling the form submission for bookings
def write_bookings_to_csv(bookings):
    with open(BOOKINGS_CSV, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'name', 'contact_no', 'service', 'service_date', 'special_request']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for booking in bookings:
            writer.writerow(booking)

@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    name = request.form['name']
    contact_no = request.form['contact_no']
    service = request.form['service']
    service_date = request.form['service_date']
    special_request = request.form['special_request']

    try:
        bookings = read_bookings_from_csv()
        # Generate new id
        if bookings:
            new_id = max(b['id'] for b in bookings) + 1
        else:
            new_id = 1

        new_booking = {
            'id': new_id,
            'name': name,
            'contact_no': contact_no,
            'service': service,
            'service_date': service_date,
            'special_request': special_request
        }
        bookings.append(new_booking)
        write_bookings_to_csv(bookings)

        flash('Your booking has been successfully submitted!', 'success')
        return redirect(url_for('booking_details', booking_id=new_id))

    except Exception as e:
        print(f"Error: {e}")
        flash('There was an error while submitting your booking. Please try again.', 'danger')
        return redirect(url_for('contact'))


@app.route('/booking_details/<int:booking_id>', methods=['GET', 'POST'])
def booking_details(booking_id):
    bookings = read_bookings_from_csv()
    booking = next((b for b in bookings if b['id'] == booking_id), None)

    if not booking:
        flash('Booking not found!', 'danger')
        return redirect(url_for('contact'))

    if request.method == 'POST':
        updated_name = request.form['name']
        updated_contact_no = request.form['contact_no']
        updated_service = request.form['service']
        updated_service_date = request.form['service_date']
        updated_special_request = request.form['special_request']

        # Update the booking in the list
        for b in bookings:
            if b['id'] == booking_id:
                b['name'] = updated_name
                b['contact_no'] = updated_contact_no
                b['service'] = updated_service
                b['service_date'] = updated_service_date
                b['special_request'] = updated_special_request
                break

        try:
            write_bookings_to_csv(bookings)
            flash('Your booking has been successfully updated!', 'success')
            return redirect(url_for('booking_details', booking_id=booking_id))
        except Exception as e:
            print(f"Error: {e}")
            flash('There was an error updating your booking. Please try again.', 'danger')
            return redirect(url_for('booking_details', booking_id=booking_id))

    return render_template('booking_details.html', booking=booking)


# Admin Panel Route
from functools import wraps
from flask import session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Avoid redirect loop by allowing access to login page without login
        if not session.get('logged_in') and request.endpoint != 'tech':
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('tech'))  # Assuming 'tech' is the login page
        return f(*args, **kwargs)
    return decorated_function


# Removed duplicate admin route to fix AssertionError

@app.route('/toggle_status/<int:booking_id>', methods=['POST'])
def toggle_status(booking_id):
    bookings = read_bookings_from_csv()
    for b in bookings:
        if b['id'] == booking_id:
            if b.get('status') == 'Confirmed':
                b['status'] = 'Pending'
            else:
                b['status'] = 'Confirmed'
            break
    try:
        write_bookings_to_csv(bookings)
        flash('Booking status toggled successfully!', 'success')
    except Exception as e:
        flash('Error toggling booking status. Please try again.', 'danger')
    return redirect(url_for('admin'))

# Removed duplicate delete_booking route to fix AssertionError


# Manage Stock
STOCK_CSV = os.path.join(DATA_DIR, 'stock.csv')

def read_stock_from_csv():
    stock_items = []
    try:
        with open(STOCK_CSV, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert id and quantity to int, price to float
                row['id'] = int(row['id'])
                row['quantity'] = int(row['quantity'])
                row['price'] = float(row['price'])
                stock_items.append(row)
    except FileNotFoundError:
        pass
    return stock_items

def write_stock_to_csv(stock_items):
    with open(STOCK_CSV, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'product_name', 'price', 'quantity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in stock_items:
            writer.writerow(item)

@app.route('/manage_stock', methods=['GET', 'POST'])
def manage_stock():
    if request.method == 'POST':
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])

        stock_items = read_stock_from_csv()
        product = next((item for item in stock_items if item['product_name'] == product_name), None)

        if product:
            product['quantity'] += quantity
        else:
            new_id = max([item['id'] for item in stock_items], default=0) + 1
            stock_items.append({
                'id': new_id,
                'product_name': product_name,
                'price': 0.0,
                'quantity': quantity
            })

        try:
            write_stock_to_csv(stock_items)
            return redirect(url_for('manage_stock'))
        except Exception as e:
            print(f"Error: {e}")
            return "There was an error updating the stock."

    stock_items = read_stock_from_csv()
    return render_template('manage_stock.html', stock_items=stock_items)

@app.route('/update_stock', methods=['POST'])
def update_stock():
    try:
        data = request.get_json()  # Get bill details from frontend
        stock_items = read_stock_from_csv()

        for item in data['items']:
            product_name = item['description']
            quantity_sold = int(item['quantity'])

            product = next((p for p in stock_items if p['product_name'] == product_name), None)
            if product:
                if product['quantity'] >= quantity_sold:
                    product['quantity'] -= quantity_sold
                else:
                    return f"Not enough stock for {product_name}", 400
            else:
                return f"Product {product_name} not found in stock", 400

        write_stock_to_csv(stock_items)
        return "Stock updated successfully", 200

    except Exception as e:
        print(f"Error updating stock: {e}")
        return "Error updating stock", 500

# Function to fetch stock items
def get_stock_items():
    return read_stock_from_csv()


# Route to create a bill
@app.route('/create_bill', methods=['GET', 'POST'])
def create_bill():
    import datetime
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        total_amount = float(request.form['total_amount'])  # Convert to float if needed
        items = request.form.getlist('items')  # List of selected items
        quantities = request.form.getlist('quantities')  # List of corresponding quantities
        
        # Create the bill in the CSV file and update stock accordingly
        try:
            # Read current stock
            stock_items = read_stock_from_csv()

            # Reduce stock based on selected items and quantities
            for i, item_id in enumerate(items):
                quantity = int(quantities[i])
                # Find the product by id
                product = next((item for item in stock_items if str(item['id']) == item_id), None)
                if product:
                    if product['quantity'] >= quantity:
                        product['quantity'] -= quantity
                    else:
                        flash(f"Not enough stock for {product['product_name']}", 'danger')
                        return redirect(url_for('create_bill'))
                else:
                    flash(f"Product with id {item_id} not found", 'danger')
                    return redirect(url_for('create_bill'))

            # Write updated stock back to CSV
            write_stock_to_csv(stock_items)

            # Save bill details to CSV
            bills_csv_path = os.path.join(DATA_DIR, 'bills.csv')
            bills_exist = os.path.exists(bills_csv_path)
            current_date = datetime.date.today().isoformat()
            bill_number = 'B' + ''.join(random.choices(string.digits, k=6))
            with open(bills_csv_path, mode='a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['bill_number', 'date', 'customer_name', 'total_amount', 'items', 'quantities']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if not bills_exist:
                    writer.writeheader()
                writer.writerow({
                    'bill_number': bill_number,
                    'date': current_date,
                    'customer_name': customer_name,
                    'total_amount': total_amount,
                    'items': ','.join(items),
                    'quantities': ','.join(quantities)
                })

            return redirect(url_for('admin'))  # Redirect to admin page after successful bill creation
        
        except Exception as e:
            print(f"Error creating bill: {e}")
            flash(f"There was an error processing the bill: {e}", 'danger')
            return redirect(url_for('create_bill'))

    # Generate a random bill number (e.g., B123456)
    bill_number = 'B' + ''.join(random.choices(string.digits, k=6))

    # Fetch the available stock items
    stock = get_stock_items()

    # Pass bill_number to the template
    return render_template('create_bill.html', stock=stock, bill_number=bill_number)



# Route to render invoice page with stock items
@app.route('/invoice')
def invoice():
    stock_items = read_stock_from_csv()
    return render_template('invoice.html', stock_items=stock_items)

# Route to create invoice and update stock
@app.route('/create_invoice', methods=['POST'])
def create_invoice():
    import io
    from flask import jsonify, send_file

    data = request.json
    items = data['items']  # Items in the invoice

    # Seller and buyer details
    seller_name = data['seller_name']
    seller_address = data['seller_address']
    seller_gstin = data['seller_gstin']
    buyer_name = data['buyer_name']
    buyer_address = data['buyer_address']
    buyer_gstin = data['buyer_gstin']

    # Invoice details
    invoice_number = data['invoice_number']
    invoice_date = data['invoice_date']
    total_value = data['total_value']
    cgst = data['cgst']
    sgst = data['sgst']
    grand_total = data['grand_total']

    try:
        stock_items = read_stock_from_csv()

        # Update stock based on invoice items
        for item in items:
            product_name = item['description']  # Product name
            quantity_sold = int(item['quantity'])  # Quantity sold

            product = next((p for p in stock_items if p['product_name'] == product_name), None)
            if product:
                if product['quantity'] >= quantity_sold:
                    product['quantity'] -= quantity_sold
                else:
                    return jsonify({"error": f"Not enough stock for {product_name}"}), 400
            else:
                return jsonify({"error": f"Product {product_name} not found in stock"}), 404

        write_stock_to_csv(stock_items)

        # Save invoice details to CSV
        invoice_csv_path = os.path.join(DATA_DIR, 'invoices.csv')
        invoice_exists = os.path.exists(invoice_csv_path)
        with open(invoice_csv_path, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['invoice_number', 'invoice_date', 'seller_name', 'seller_address', 'seller_gstin',
                          'buyer_name', 'buyer_address', 'buyer_gstin', 'total_value', 'cgst', 'sgst', 'grand_total']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not invoice_exists:
                writer.writeheader()
            writer.writerow({
                'invoice_number': invoice_number,
                'invoice_date': invoice_date,
                'seller_name': seller_name,
                'seller_address': seller_address,
                'seller_gstin': seller_gstin,
                'buyer_name': buyer_name,
                'buyer_address': buyer_address,
                'buyer_gstin': buyer_gstin,
                'total_value': total_value,
                'cgst': cgst,
                'sgst': sgst,
                'grand_total': grand_total
            })

        # Generate the PDF invoice
        pdf_buffer = io.BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)

        # Invoice header
        pdf.drawString(100, 750, "TAX INVOICE")
        pdf.drawString(100, 730, f"Seller: {seller_name}")
        pdf.drawString(100, 710, f"Address: {seller_address}")
        pdf.drawString(100, 690, f"GSTIN: {seller_gstin}")
        pdf.drawString(100, 670, f"Buyer: {buyer_name}")
        pdf.drawString(100, 650, f"Address: {buyer_address}")
        pdf.drawString(100, 630, f"GSTIN: {buyer_gstin}")
        pdf.drawString(100, 610, f"Invoice No: {invoice_number}")
        pdf.drawString(100, 590, f"Date: {invoice_date}")

        # Table header for the invoice items
        pdf.drawString(100, 570, "Description     Quantity     Rate     Amount")
        y_position = 550

        # Add each item to the invoice
        for item in items:
            description = item['description']
            quantity = item['quantity']
            rate = item['rate']
            amount = float(quantity) * float(rate)
            pdf.drawString(100, y_position, f"{description}      {quantity}        {rate}       {amount}")
            y_position -= 20

        # Totals at the end of the invoice
        pdf.drawString(100, y_position - 20, f"Total Value: {total_value}")
        pdf.drawString(100, y_position - 40, f"CGST (9%): {cgst}")
        pdf.drawString(100, y_position - 60, f"SGST (9%): {sgst}")
        pdf.drawString(100, y_position - 80, f"Grand Total: {grand_total}")

        pdf.save()

        # Send the PDF as a response to the client
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name=f"Invoice_{invoice_number}.pdf", mimetype='application/pdf')

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Error updating stock"}), 500
@app.route('/edit_booking/<int:booking_id>', methods=['GET', 'POST'])
def edit_booking(booking_id):
    bookings = read_bookings_from_csv()
    booking = next((b for b in bookings if b['id'] == booking_id), None)

    if not booking:
        flash('Booking not found!', 'danger')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        updated_name = request.form['name']
        updated_contact_no = request.form['contact_no']
        updated_service = request.form['service']
        updated_service_date = request.form['service_date']
        updated_special_request = request.form['special_request']

        for b in bookings:
            if b['id'] == booking_id:
                b['name'] = updated_name
                b['contact_no'] = updated_contact_no
                b['service'] = updated_service
                b['service_date'] = updated_service_date
                b['special_request'] = updated_special_request
                break

        try:
            write_bookings_to_csv(bookings)
            flash('Booking updated successfully!', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            flash('Error updating booking. Please try again.', 'danger')
            return redirect(url_for('edit_booking', booking_id=booking_id))

    return render_template('edit_booking.html', booking=booking)

@app.route('/view_booking/<int:booking_id>')
def view_booking(booking_id):
    bookings = read_bookings_from_csv()
    booking = next((b for b in bookings if b['id'] == booking_id), None)

    if not booking:
        flash('Booking not found!', 'danger')
        return redirect(url_for('admin'))

    return render_template('view_booking.html', booking=booking)

@app.route('/confirm_booking/<int:booking_id>', methods=['POST'])
def confirm_booking(booking_id):
    bookings = read_bookings_from_csv()
    booking_found = False
    for b in bookings:
        if b['id'] == booking_id:
            b['status'] = 'Confirmed'
            booking_found = True
            # Insert booking data into adminbooking.csv
            try:
                adminbooking_csv = os.path.join(DATA_DIR, 'adminbooking.csv')
                with open(adminbooking_csv, mode='a', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['id', 'name', 'contact_no', 'service', 'service_date', 'special_request', 'status']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    # Write header if file is empty
                    if os.stat(adminbooking_csv).st_size == 0:
                        writer.writeheader()
                    writer.writerow(b)
            except Exception as e:
                flash(f'Error inserting booking into adminbooking.csv: {e}', 'danger')
            break
    if not booking_found:
        flash('Booking not found!', 'danger')
        return redirect(url_for('admin'))
    try:
        write_bookings_to_csv(bookings)
        flash('Booking confirmed successfully!', 'success')
    except Exception as e:
        flash('Error confirming booking. Please try again.', 'danger')
    return redirect(url_for('admin'))

@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    bookings = read_bookings_from_csv()
    new_bookings = [b for b in bookings if b['id'] != booking_id]

    if len(new_bookings) == len(bookings):
        flash("No booking found with this ID!", 'danger')
        return redirect(url_for('admin'))

    try:
        write_bookings_to_csv(new_bookings)
        flash("Booking deleted successfully!", 'success')
        return redirect(url_for('admin'))
    except Exception as e:
        flash(f"There was an error deleting the booking: {e}", 'danger')
        return redirect(url_for('admin'))

@app.route('/cancel_booking/<int:booking_id>')
def cancel_booking(booking_id):
    bookings = read_bookings_from_csv()
    for b in bookings:
        if b['id'] == booking_id:
            b['status'] = 'Canceled'
            break
    try:
        write_bookings_to_csv(bookings)
        flash('Booking canceled successfully!', 'success')
    except Exception as e:
        flash('Error canceling booking. Please try again.', 'danger')
    return redirect(url_for('admin'))

@app.route('/print_invoice/<int:booking_id>')
def print_invoice(booking_id):
    # For simplicity, redirect to booking details or implement invoice generation
    return redirect(url_for('booking_details', booking_id=booking_id))

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
