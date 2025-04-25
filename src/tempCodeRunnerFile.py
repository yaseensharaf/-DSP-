import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_socketio import SocketIO
import pandas as pd
from datetime import date

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = '123456'  # Change to a more secure key in production

# Initialize Flask-SocketIO
socketio = SocketIO(app)

# Load unique product data from CSV file
def get_product_data():
    file_path = 'data/ALL_H&M.csv'
    if os.path.exists(file_path):
        data = pd.read_csv(file_path, encoding='ISO-8859-1')
        products = data[['ProductName']].drop_duplicates(subset='ProductName')
        print("Unique products in dataset:")  # Debug
        print(products)
        return products.to_dict('records')  # Convert DataFrame to a list of dictionaries
    return []

# Load trending products from three datasets
def get_trending_products(limit=5):
    # Load data from the three datasets
    file_paths = ['data/ALL_H&M.csv', 'data/ALLRetail_Store_1.csv', 'data/ALLRetail_Store_2.csv']
    all_data = []

    for file_path in file_paths:
        if os.path.exists(file_path):
            data = pd.read_csv(file_path, encoding='ISO-8859-1')

            # Ensure the 'Date' column exists and is correctly parsed
            if 'Date' not in data.columns:
                print(f"Error: 'Date' column not found in {file_path}")
                continue
            
            data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
            data = data[data['Date'] > '2023-01-01']  # Filter data after 2023

            # Group by ProductName and sum the sales
            trending = data.groupby(['ProductName'])['Sales'].sum().reset_index()

            # Sort by Sales and take the top 'limit' products
            trending = trending.sort_values(by='Sales', ascending=False).head(limit)

            # Add a dataset identifier (for differentiation)
            trending['Store'] = file_path.split('/')[-1].replace('.csv', '')  # Extract store name from file name
            all_data.append(trending)
            print(f"Trending data from {file_path}:")
            print(trending.head())  # Debugging - see the data being loaded

    if not all_data:
        print("No data found after filtering.")
        return pd.DataFrame()  # Return an empty DataFrame if no data is found

    # Combine all datasets into one DataFrame
    combined_data = pd.concat(all_data)

    # Sort by total sales across all datasets
    combined_data = combined_data.groupby(['Store', 'ProductName']).agg({'Sales': 'sum'}).reset_index()

    trending = combined_data.sort_values(by='Sales', ascending=False).head(15)
    
    print("Combined and sorted trending data:")
    print(trending.head())  # Debugging - see the final combined data
    
    return trending

# Load lowest-selling products from H&M dataset
def get_lowest_selling_products(limit=5):
    file_path = 'data/ALL_H&M.csv'
    if os.path.exists(file_path):
        data = pd.read_csv(file_path, encoding='ISO-8859-1')

        # Ensure 'Date' and 'Sales' columns exist
        if 'Date' not in data.columns or 'Sales' not in data.columns:
            print(f"Missing 'Date' or 'Sales' column in {file_path}")
            return pd.DataFrame()

        # Parse dates and filter for data after 2023
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        data = data[data['Date'] > '2023-01-01']

        # Group by ProductName and sum the sales
        lowest_sales = data.groupby('ProductName')['Sales'].sum().reset_index()

        # Sort by Sales in ascending order to get lowest-selling products
        lowest_sales = lowest_sales.sort_values(by='Sales', ascending=True).head(limit)
        lowest_sales['Store'] = 'ALL_H&M'  # Set store name

        print(f"Lowest-selling products from {file_path}:")
        print(lowest_sales.head())  # Debugging

        return lowest_sales
    return pd.DataFrame()

@app.route('/')
@app.route('/index.html')
def index():
    products = get_product_data()  # Get product data
    today = date.today().strftime("%B %d, %Y")
    dark_mode = 'dark' if session.get('dark_mode') else ''
    return render_template('index.html', products=products, today=today, dark_mode=dark_mode)

@app.route('/trending.html')
def trending():
    trending_products = get_trending_products(limit=5)  # Get top 5 trending products for each dataset
    print("Trending Products:", trending_products)  # Debugging to see the data
    
    if trending_products.empty:
        flash("No trending products found after 2023.")
        return redirect(url_for('index'))

    today = date.today().strftime("%B %d, %Y")
    dark_mode = 'dark' if session.get('dark_mode') else ''
    
    # Render template with products data
    return render_template('trending.html', products=trending_products.to_dict('records'), today=today, dark_mode=dark_mode)

@app.route('/updateAll', methods=['POST'])
def update_all():
    data = request.get_json()  # Get JSON data from client
    with open('update_data.json', 'w') as f:
        json.dump(data, f)
    socketio.emit('data_updated', data)  # Broadcast update
    return jsonify({'status': 'success'})

@app.route('/toggle-dark-mode', methods=['POST'])
def toggle_dark_mode():
    session['dark_mode'] = not session.get('dark_mode', False)
    return ('', 204)

@app.route('/recommend.html')
def recommend():
    # Define file paths for the two other retail stores
    file_paths = ['data/ALLRetail_Store_1.csv', 'data/ALLRetail_Store_2.csv']
    top_sales_products = []

    for file_path in file_paths:
        if os.path.exists(file_path):
            data = pd.read_csv(file_path, encoding='ISO-8859-1')

            # Ensure 'Date' and 'Sales' columns exist
            if 'Date' not in data.columns or 'Sales' not in data.columns:
                print(f"Missing 'Date' or 'Sales' column in {file_path}")
                continue

            # Parse dates and filter for data after 2023
            data['Date'] = pd.to_datetime(data['Date'], dayfirst=True, errors='coerce')
            data = data[data['Date'] > '2023-01-01']

            # Group by ProductName and sum the sales
            store_top_sales = data.groupby('ProductName')['Sales'].sum().reset_index()

            # Sort by Sales and get the top 5 products for each store
            store_top_sales = store_top_sales.sort_values(by='Sales', ascending=False).head(5)
            store_top_sales['Store'] = file_path.split('/')[-1].replace('.csv', '')  # Store name
            top_sales_products.append(store_top_sales)

    # Combine all data into a single DataFrame
    top_sales_df = pd.concat(top_sales_products)

    if top_sales_df.empty:
        flash("No data found for top-selling products in the stores.")
        return redirect(url_for('index'))

    today = date.today().strftime("%B %d, %Y")
    dark_mode = 'dark' if session.get('dark_mode') else ''

    return render_template('recommend.html', top_sales=top_sales_df.to_dict('records'), today=today, dark_mode=dark_mode)

@app.route('/lowest.html')
def lowest():
    lowest_products = get_lowest_selling_products(limit=5)  # Get lowest 5 products for H&M
    print("Lowest-Selling Products:", lowest_products)  # Debugging
    
    if lowest_products.empty:
        flash("No data found for lowest-selling products in H&M.")
        return redirect(url_for('index'))

    today = date.today().strftime("%B %d, %Y")
    dark_mode = 'dark' if session.get('dark_mode') else ''
    
    return render_template('lowest.html', lowest_sales=lowest_products.to_dict('records'), today=today, dark_mode=dark_mode)

@app.route('/help.html')
def help():
    today = date.today().strftime("%B %d, %Y")
    dark_mode = 'dark' if session.get('dark_mode') else ''
    return render_template('help.html', today=today, dark_mode=dark_mode)

# Get unique product names from sales data
def get_product_names():
    file_path = 'data/ALL_H&M.csv'
    if os.path.exists(file_path):
        # Read CSV with proper encoding to handle special characters
        data = pd.read_csv(file_path, encoding='ISO-8859-1')
        # Get unique product names (no duplicates)
        unique_product_names = data['ProductName'].dropna().drop_duplicates()
        return sorted(unique_product_names)
    return []


def get_product_data():
    all_data_path = 'data/ALL_H&M.csv'  # Sales data, only has ProductName
    category_data_path = 'data/H_M.csv'  # Has ProductName + Category

    if os.path.exists(all_data_path) and os.path.exists(category_data_path):
        # Load both datasets
        all_data = pd.read_csv(all_data_path, encoding='ISO-8859-1')
        category_data = pd.read_csv(category_data_path, encoding='ISO-8859-1')

        # Drop duplicates from the category file
        category_data = category_data[['ProductName', 'Category']].drop_duplicates()

        # Merge category info into the ALL data
        merged = all_data[['ProductName']].drop_duplicates().merge(
            category_data, on='ProductName', how='left'
        )

        # Handle any missing categories if needed
        merged['Category'] = merged['Category'].fillna('Uncategorized')

        return merged.to_dict('records')
    return []

# Route to return the product image URL as JSON
@app.route('/product_image/<product_name>')
def product_image(product_name):
    # Replace spaces with underscores to match the image filename
    filename = product_name.replace(" ", "_") + ".png"
    image_path = os.path.join("static", "images", filename)
    if os.path.exists(image_path):
        return jsonify({"image_url": url_for('static', filename=f"images/{filename}")})
    return jsonify({"error": "Image not found"}), 404



@app.route('/product_sales/<product_name>')
def product_sales(product_name):
    from urllib.parse import unquote
    product_name = unquote(product_name)  # Decode URL-encoded names

    file_paths = [
        'data/ALL_H&M.csv',
        'data/ALLRetail_Store_1.csv',
        'data/ALLRetail_Store_2.csv'
    ]

    sales_data = []

    for file_path in file_paths:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, encoding='ISO-8859-1')
            if {'ProductName', 'Date', 'Sales'}.issubset(df.columns):
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df = df[df['ProductName'] == product_name]
                df = df.dropna(subset=['Date'])

                if not df.empty:
                    grouped = df.groupby('Date')['Sales'].sum().reset_index()
                    sales_data.append(grouped)

    if not sales_data:
        return jsonify({"error": f"No sales data found for {product_name}"}), 404

    # Combine all sources into one timeline
    combined = pd.concat(sales_data).groupby('Date')['Sales'].sum().reset_index()
    combined = combined.sort_values(by='Date')

    return jsonify({
        "dates": combined['Date'].dt.strftime('%Y-%m-%d').tolist(),
        "quantities": combined['Sales'].tolist()
    })

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001)