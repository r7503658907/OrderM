import streamlit as st
import json
import os
import pandas as pd
import base64
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from io import BytesIO


# Function to load data from JSON file
def load_data(filename, default_data):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump(default_data, f, indent=4)
        return default_data
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


# Define default data
default_products = []
default_customers = []
default_orders = []

# Load initial data
products = load_data('products.json', default_products)
customers = load_data('customers.json', default_customers)
orders = load_data('orders.json', default_orders)


# Function to save data to JSON file
def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


# Function to add a new product
def add_product(product_id, name, price, quantity):
    new_product = {
        'id': product_id,
        'name': name,
        'price': price,
        'quantity': quantity
    }
    products.append(new_product)
    save_data(products, 'products.json')


# Function to update an existing product
def update_product(product_id, name, price, quantity):
    for product in products:
        if 'id' in product and str(product['id']) == product_id:
            product['name'] = name
            product['price'] = price
            product['quantity'] = quantity
            save_data(products, 'products.json')
            return True
    return False


# Function to delete a product
def delete_product(product_id):
    for idx, product in enumerate(products):
        if 'id' in product and str(product['id']) == product_id:
            del products[idx]
            save_data(products, 'products.json')
            return True
    return False


# Function to add a new customer
def add_customer(name, address, mobile, email):
    customer_id = str(uuid.uuid4())[:4]  # Generate a short UUID
    new_customer = {
        'id': customer_id,
        'name': name,
        'address': address,
        'mobile': mobile,
        'email': email
    }
    customers.append(new_customer)
    save_data(customers, 'customers.json')


# Function to update an existing customer
def update_customer(customer_id, name, address, mobile, email):
    for customer in customers:
        if 'id' in customer and str(customer['id']) == str(customer_id):  # Check if 'id' key exists
            # Update customer details
            customer['name'] = name
            customer['address'] = address
            customer['mobile'] = mobile
            customer['email'] = email
            # Save updated data to JSON file
            save_data(customers, 'customers.json')
            return True
    return False


# Function to delete a customer
def delete_customer(customer_id):
    for idx, customer in enumerate(customers):
        if 'id' in customer and str(customer['id']) == str(customer_id):  # Check if 'id' key exists
            del customers[idx]
            save_data(customers, 'customers.json')
            return True
    return False


# Function to add a new order
def add_order(customer_id):
    order_id = str(uuid.uuid4())[:4]  # Generate a short UUID
    new_order = {
        'order_id': order_id,
        'customer_id': customer_id,
        'products': [],
        'total_amount': 0.0
    }
    orders.append(new_order)
    save_data(orders, 'orders.json')
    return new_order


# Function to update an existing order
def update_order(order_id, product_id, quantity):
    for order in orders:
        if order['order_id'] == order_id:
            for product in products:
                if product['id'] == product_id:
                    order['products'].append({'product_id': product_id, 'name': product['name'], 'quantity': quantity,
                                              'price': product['price']})
                    order['total_amount'] += quantity * product['price']
                    save_data(orders, 'orders.json')
                    return True
    return False


# Function to delete an order
def delete_order(order_id):
    for idx, order in enumerate(orders):
        if order['order_id'] == order_id:
            del orders[idx]
            save_data(orders, 'orders.json')
            return True
    return False


# Function to download products as Excel file
def download_products():
    df = pd.DataFrame(products)
    df['Total Price'] = df['price'] * df['quantity']  # Calculate total price for each product
    df.to_excel('products.xlsx', index=False)
    st.success('Products data downloaded successfully!')
    # Provide a download link for the Excel file
    st.markdown(get_download_link('products.xlsx', 'Download Products Excel File'), unsafe_allow_html=True)


# Function to download customers as Excel file
def download_customers():
    df = pd.DataFrame(customers)
    df.to_excel('customers.xlsx', index=False)
    st.success('Customers data downloaded successfully!')
    # Provide a download link for the Excel file
    st.markdown(get_download_link('customers.xlsx', 'Download Customers Excel File'), unsafe_allow_html=True)


# Function to download orders as Excel file
def download_orders():
    order_data = []
    for order in orders:
        for product in order['products']:
            order_data.append({
                'Order ID': order['order_id'],
                'Customer ID': order['customer_id'],
                'Product ID': product['product_id'],
                'Product Name': product['name'],
                'Product Quantity': product['quantity'],
                'Product Price': product['price'],
                'Total Amount': order['total_amount']
            })
    df = pd.DataFrame(order_data)
    df.to_excel('orders.xlsx', index=False)
    st.success('Orders data downloaded successfully!')
    # Provide a download link for the Excel file
    st.markdown(get_download_link('orders.xlsx', 'Download Orders Excel File'), unsafe_allow_html=True)


# Function to generate a download link for a file
def get_download_link(file_path, link_text):
    with open(file_path, 'rb') as f:
        data = f.read()
    b64_data = base64.b64encode(data).decode('utf-8')
    href = f'<a href="data:application/octet-stream;base64,{b64_data}" download="{file_path}">{link_text}</a>'
    return href


def generate_invoice(order, customer, products):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    # Define custom styles
    style_heading = ParagraphStyle(
        name='Heading1',
        parent=styles['Heading1'],
        alignment=1,  # Center alignment for heading
        fontSize=20,
        leading=22,
        spaceAfter=20,
        textColor=colors.darkblue
    )

    style_subheading = ParagraphStyle(
        name='SubHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.darkblue
    )

    style_body = ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        alignment=0,  # Left alignment for body text
        fontSize=12,
        leading=14
    )

    style_customer_info = ParagraphStyle(
        name='CustomerInfo',
        parent=styles['Normal'],
        fontSize=12,
        leading=18,
        spaceAfter=20
    )

    style_table_header = ParagraphStyle(
        name='TableHeader',
        parent=styles['Normal'],
        fontSize=12,
        leading=14,
        textColor=colors.white
    )


    # Heading
    heading_text = "<b>INVOICE</b>"
    heading = Paragraph(heading_text, style_heading)

    # Company information
    company_name = Paragraph("<b>RevivingIndia</b>", style_subheading)
    company_address = "123 Street, City, Country, Zip Code"
    company_contact = "Phone: (000) 000-0000"
    company_address_para = Paragraph(company_address, style_body)
    company_contact_para = Paragraph(company_contact, style_body)


    # Current date
    current_date = datetime.now().strftime('%d-%m-%Y')

    # Customer information
    customer_info = f"""
        <b>Customer Name:</b> {customer.get('name', 'N/A')}<br/>
        <b>Customer ID:</b> {customer['id']}<br/>
        <b>Order ID:</b> {order['order_id']}<br/>
        <b>Date:</b> {current_date}
    """
    customer_info_para = Paragraph(customer_info, style_customer_info)

    # Table data
    data = [
        [Paragraph("DESCRIPTION", style_table_header), Paragraph("QTY", style_table_header),
         Paragraph("UNIT PRICE", style_table_header), Paragraph("AMOUNT", style_table_header)]
    ]
    for product in order['products']:
        product_info = next((p for p in products if p['id'] == product['product_id']), None)
        product_name = product_info.get('name', 'N/A') if product_info else 'N/A'
        qty = product['quantity']
        unit_price = product['price']
        amount = qty * unit_price
        data.append([product_name, qty, f" {unit_price:.2f}", f" {amount:.2f}"])

    # Subtotals and totals
    subtotal = sum(p['price'] * p['quantity'] for p in order['products'])
    tax_rate = 0.0425  # Example tax rate
    tax_amount = subtotal * tax_rate
    total_amount = subtotal + tax_amount

    data.append(["", "", "Subtotal", f" {subtotal:.2f}"])
    data.append(["", "", "Tax Rate", f"{tax_rate * 100:.2f}%"])
    data.append(["", "", "Tax", f" {tax_amount:.2f}"])
    data.append(["", "", "Total", f" {total_amount:.2f}"])

    # Table
    table = Table(data, hAlign='LEFT', colWidths=[200, 50, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('BACKGROUND', (-1, -1), (-1, -1), colors.lightblue),
    ]))

    # Build story
    elements = [
        heading,
        # logo,
        Spacer(1, 12),
        company_name,
        company_address_para,
        company_contact_para,
        Spacer(1, 24),

        Spacer(1, 12),
        customer_info_para,
        Spacer(1, 12),
        table
    ]

    doc.build(elements)

    buffer.seek(0)
    return buffer

# Streamlit UI
st.title('Product, Customer, and Order Management')

menu = st.sidebar.selectbox('Menu', [ 'Home','Customers','Products','Orders' ])

if menu == 'Home':
    st.subheader('Home')
    st.write('Welcome to the Product, Customer, and Order Management System!')

if menu == 'Products':
    st.sidebar.subheader('Manage Products')
    action = st.sidebar.selectbox('Select Action',
                          ['View Products', 'Add Product', 'Update Product', 'Delete Product', 'Download Products'])

    if action == 'View Products':
        # Display products
        st.subheader('Latest Products (Newest 5)')
        latest_products = products[-5:]  # Get the latest 5 products
        if len(latest_products) > 0:
            product_df = pd.DataFrame(latest_products)
            product_df['Total Price'] = product_df['price'] * product_df['quantity']  # Calculate total price
            product_df = product_df[['id', 'name', 'quantity', 'price', 'Total Price']]  # Reorder columns
            st.table(
                product_df.style.set_properties(**{'border': '1px solid black', 'border-collapse': 'collapse'}).format(
                    {'price': '{:.0f}', 'Total Price': '{:.0f}', 'quantity': '{:.0f}'}))
        else:
            st.write('No products available.')
    elif action == 'Add Product':
        # Add product
        st.subheader('Add Product')
        product_id = st.text_input('Enter Product ID')
        name = st.text_input('Enter Product Name')
        price = st.number_input('Enter Product Price', min_value=0.0)
        quantity = st.number_input('Enter Product Quantity', min_value=1)
        if st.button('Add Product'):
            add_product(product_id, name, price, quantity)
            st.success('Product Added Successfully!')
    elif action == 'Update Product':
        # Update product
        st.subheader('Update Product')
        product_id = st.text_input('Enter Product ID to Update')
        if product_id:
            name = st.text_input('Enter New Name')
            price = st.number_input('Enter New Price', min_value=0.0)
            quantity = st.number_input('Enter New Quantity', min_value=1)
            if st.button('Update Product'):
                if update_product(str(product_id), name, price, quantity):
                    st.success('Product Updated Successfully!')
                else:
                    st.warning('Product ID not found!')
    elif action == 'Delete Product':
        # Delete product
        st.subheader('Delete Product')
        product_id = st.text_input('Enter Product ID to Delete')
        if product_id:
            if delete_product(product_id):
                st.success('Product Deleted Successfully!')
            else:
                st.warning('Product ID not found!')
    elif action == 'Download Products':
        # Download products as Excel file
        download_products()


if menu == 'Customers':
    st.subheader('Manage Customers')
    action = st.selectbox('Select Action', ['View Customers', 'Add Customer', 'Update Customer', 'Delete Customer',
                                            'Download Customers'])

    if action == 'View Customers':
        # Display customers
        st.subheader('Latest Customers (Newest 5)')
        latest_customers = customers[-5:]  # Get the latest 5 customers
        if len(latest_customers) > 0:
            customer_df = pd.DataFrame(latest_customers)
            st.table(customer_df.style.set_properties(**{'border': '1px solid black', 'border-collapse': 'collapse'}))
        else:
            st.write('No customers available.')
    elif action == 'Add Customer':
        # Add customer
        st.subheader('Add Customer')
        name = st.text_input('Enter Customer Name')
        address = st.text_input('Enter Customer Address')
        mobile = st.text_input('Enter Customer Mobile')
        email = st.text_input('Enter Customer Email')
        if st.button('Add Customer'):
            add_customer(name, address, mobile, email)
            st.success('Customer Added Successfully!')
    elif action == 'Update Customer':
        # Update customer
        st.subheader('Update Customer')
        customer_id = st.text_input('Enter Customer ID to Update')
        if customer_id:
            name = st.text_input('Enter New Name')
            address = st.text_input('Enter New Address')
            mobile = st.text_input('Enter New Mobile')
            email = st.text_input('Enter New Email')
            if st.button('Update Customer'):
                if update_customer(customer_id, name, address, mobile, email):
                    st.success('Customer Updated Successfully!')
                else:
                    st.warning('Customer ID not found!')
    elif action == 'Delete Customer':
        # Delete customer
        st.subheader('Delete Customer')
        customer_id = st.text_input('Enter Customer ID to Delete')
        if customer_id:
            if delete_customer(customer_id):
                st.success('Customer Deleted Successfully!')
            else:
                st.warning('Customer ID not found!')
    elif action == 'Download Customers':
        # Download customers as Excel file
        download_customers()

if menu == 'Orders':
    st.subheader('Manage Orders')
    action = st.selectbox('Select Action',
                          ['View Orders', 'Add Order', 'Update Order', 'Delete Order', 'Download Orders'])

    if action == 'View Orders':
        customer_id_filter = st.text_input("Enter Customer ID to filter (leave blank to show all)")
        order_id_filter = st.text_input("Enter Order ID to generate bill")

        if st.button("Generate Bill"):
            order_to_bill = next((o for o in orders if o['order_id'] == order_id_filter), None)
            print(order_to_bill)

            if order_to_bill:
                try:
                    if 'customer_id' not in order_to_bill:
                        st.write("Error: 'customer_id' key not found in the order.")
                    else:
                        customer_id = order_to_bill['customer_id']
                        print(customer_id)
                        customer_info = next((c for c in customers if c['id'] == customer_id), None)
                        print(customer_info)
                        if customer_info:
                            pdf_buffer = generate_invoice(order_to_bill, customer_info, products,)
                            st.download_button(
                                label="Download Bill",
                                data=pdf_buffer,
                                file_name=f"bill_order_{order_id_filter}.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.write("Error: Customer information not found.")
                except KeyError as e:
                    st.write(f"KeyError: {e}")
                    st.write("Order to Bill:", order_to_bill)
                    st.write("Customers:", customers)
            else:
                st.write("Order ID not found.")
        st.subheader('Latest Orders (Newest 5)')
        latest_orders = orders[-10:]

        if len(latest_orders) > 0:
            order_data = []
            total_amount_by_customer = {}
            for order in latest_orders:
                if customer_id_filter.strip() == '' or order['customer_id'] == customer_id_filter.strip():
                    total_price = sum(product['price'] * product['quantity'] for product in order['products'])

                    for product in order['products']:
                        product_name = 'N/A'
                        for p in products:
                            if p['id'] == product['product_id']:
                                product_name = p.get('name', 'N/A')
                                break

                        order_data.append({
                            'Order ID': order['order_id'],
                            'Customer ID': order['customer_id'],
                            'Product ID': product['product_id'],
                            'Product Name': product_name,
                            'Product Quantity': product['quantity'],
                            'Product Price': format(product['price'], '.2f').rstrip('0').rstrip('.')
                        })

                    if order['customer_id'] in total_amount_by_customer:
                        total_amount_by_customer[order['customer_id']] += total_price
                    else:
                        total_amount_by_customer[order['customer_id']] = total_price

            filtered_order_data = [order for order in order_data if
                                   customer_id_filter.strip() == '' or order[
                                       'Customer ID'] == customer_id_filter.strip()]
            order_df = pd.DataFrame(filtered_order_data)

            if len(filtered_order_data) > 0:
                st.table(order_df.style.set_properties(**{'border': '1px solid black', 'border-collapse': 'collapse'}))
            else:
                st.write('No orders available for the specified customer ID.')

            st.subheader('Total Amount by Customer ID')
            if customer_id_filter.strip() != '':
                if total_amount_by_customer and customer_id_filter.strip() in total_amount_by_customer:
                    total_amount = total_amount_by_customer[customer_id_filter.strip()]
                    customer_df = pd.DataFrame([{
                        'Customer ID': customer_id_filter.strip(),
                        'Total Amount': format(total_amount, '.2f').rstrip('0').rstrip('.')
                    }])
                    st.table(customer_df.style.set_properties(
                        **{'border': '1px solid black', 'border-collapse': 'collapse'}))
                else:
                    st.write('No orders available for the specified customer ID.')
        else:
            st.write('No orders available.')

    elif action == 'Add Order':
        # Add order
        st.subheader('Add Order')
        customer_id = st.selectbox('Select Customer ID', [c['id'] for c in customers])
        if st.button('Create Order'):
            new_order = add_order(customer_id)
            st.success(f'Order {new_order["order_id"]} Created Successfully!')

        order_id = st.selectbox('Select Order ID to Add Products',
                                [o['order_id'] for o in orders if o['customer_id'] == customer_id])
        product_id = st.selectbox('Select Product ID', [p['id'] for p in products])
        quantity = st.number_input('Enter Quantity', min_value=1)
        if st.button('Add Product to Order'):
            if update_order(order_id, product_id, quantity):
                st.success('Product Added to Order Successfully!')
            else:
                st.warning('Order ID or Product ID not found!')
    elif action == 'Update Order':
        # Update order
        st.subheader('Update Order')
        order_id = st.selectbox('Select Order ID to Update', [o['order_id'] for o in orders])
        product_id = st.selectbox('Select Product ID to Update', [p['id'] for p in products])
        quantity = st.number_input('Enter New Quantity', min_value=1)
        if st.button('Update Product Quantity in Order'):
            if update_order(order_id, product_id, quantity):
                st.success('Order Updated Successfully!')
            else:
                st.warning('Order ID or Product ID not found!')
    elif action == 'Delete Order':
        # Delete order
        st.subheader('Delete Order')
        order_id = st.text_input('Enter Order ID to Delete')
        if order_id:
            if delete_order(order_id):
                st.success('Order Deleted Successfully!')
            else:
                st.warning('Order ID not found!')
    elif action == 'Download Orders':
        # Download orders as Excel file
        download_orders()
