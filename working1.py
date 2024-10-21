import streamlit as st
from pymongo import MongoClient

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI
db = client['purchase_db']  # Database name
orders_collection = db['orders']  # Collection name

# Streamlit title
st.title('Submit a Purchase Order with Multiple Products')
# Initialize session state to store products
if "products" not in st.session_state:
    st.session_state["products"] = []

# Function to add a new product
def add_product():
    st.session_state["products"].append({"product_id": "", "quantity": 1, "price_per_unit": 0.0})

# Function to remove the last added product
def remove_product():
    if st.session_state["products"]:
        st.session_state["products"].pop()

# Function to delete all data in the MongoDB collection
def delete_all_orders():
    result = orders_collection.delete_many({})  # Delete all documents
    return result.deleted_count  # Return number of deleted documents

# Function to delete a specific product from an order
def delete_product_from_order(customer_id, product_id):
    result = orders_collection.update_one(
        {'Supplier_Name': customer_id}, 
        {'$pull': {'products': {'product_id': product_id}}}
    )
    return result.modified_count

# Buttons to add or remove products
col1,col2=st.columns([1,1])
col1.button("Add Product", on_click=add_product)
col2.button("Remove Last Product", on_click=remove_product)
# Streamlit form for customer details and products
with st.form("purchase_order_form"):
    col3,col4=st.columns([3,1])
    # Customer details
    Supplier_Name = col3.text_input("Supplier Name", max_chars=20)
    order_date = col4.date_input("Order Date")
    col5,col6,col7,col8=st.columns([4,1,2,2])
    col5.text('Product Name')
    col6.text('Quantity')
    col7.text('Price')
    col8.text('Total Amount')
    
    

    # Loop through the products in session state to display them
    for index, product in enumerate(st.session_state["products"]):
        #st.subheader(f"Product {index + 1}")
        col1,col2,col3,col4=st.columns([4,1,2,2])
        product_id = col1.text_input(f"Product ID {index + 1}", 
                        key=f"product_id_{index}", max_chars=20,label_visibility='hidden',
                        placeholder='Enter Product')
        quantity = col2.number_input(f"Quantity {index + 1}", min_value=1, step=1, key=f"quantity_{index}",label_visibility='hidden')
        
        price_per_unit = col3.number_input(f"Price per Unit {index + 1}", min_value=0.0, step=0.01, key=f"price_per_unit_{index}",label_visibility='hidden')
        
        col4.number_input(f'Total_value {index+1}',min_value=quantity*price_per_unit,label_visibility='hidden')
        # Update session state with product info
        st.session_state["products"][index]["product_id"] = product_id
        st.session_state["products"][index]["quantity"] = quantity
        st.session_state["products"][index]["price_per_unit"] = price_per_unit

    # Form submission button
    submitted = st.form_submit_button("Submit Purchase Order")

    if submitted:
        if Supplier_Name and st.session_state["products"]:
            # Prepare purchase order data
            purchase_order = {
                'Supplier_Name': Supplier_Name,
                'order_date': order_date.strftime("%Y-%m-%d"),
                'products': st.session_state["products"]
            }
            
            # Insert the order into the MongoDB collection
            orders_collection.insert_one(purchase_order)
            
            st.success(f"Purchase order for Customer ID: {Supplier_Name} successfully submitted!")
            # Clear products after submission
            st.session_state["products"] = []
        else:
            st.error("Please fill all the required fields correctly and add at least one product.")

# Display existing orders (optional)
st.subheader("Existing Orders")
orders = orders_collection.find()  # Fetch all documents from the orders collection
for order in orders:
    st.write(order)

# Function to retrieve purchase orders from MongoDB
def fetch_purchase_orders():
    return list(orders_collection.find({}))

import pandas as pd

# Display the purchase orders in a formatted table
def display_orders_table(orders):
    if not orders:
        st.write("No purchase orders found.")
        return

    # Flattening the product details for each purchase order into a displayable format
    formatted_orders = []
    for order in orders:
        for product in order['products']:
            formatted_orders.append({
                "Customer ID": order['Supplier_Name'],
                "Order Date": order['order_date'],
                "Product ID": product['product_id'],
                "Quantity": product['quantity'],
                "Price per Unit": product['price_per_unit']
            })

    # Convert to a DataFrame for better display
    df = pd.DataFrame(formatted_orders)
    st.dataframe(df)

# Optionally, display each order separately
def display_orders_detailed(orders):
    if not orders:
        st.write("No purchase orders found.")
        return

    for order in orders:
        st.subheader(f"Order for Customer ID: {order['Supplier_Name']} on {order['order_date']}")
        for idx, product in enumerate(order['products']):
            st.write(f"**Product {idx + 1}:**")
            st.write(f"- Product ID: {product['product_id']}")
            st.write(f"- Quantity: {product['quantity']}")
            st.write(f"- Price per Unit: {product['price_per_unit']}")
        st.write("---")

# Fetch the orders from MongoDB
orders = fetch_purchase_orders()

# Step 1: Add a checkbox to ask for confirmation before deleting
st.subheader("Delete All Purchase Orders")
confirm_delete = st.checkbox("I confirm that I want to delete all purchase orders")

# Step 2: Add a button to trigger the delete operation (only if confirmed)
if confirm_delete:
    if st.button("Delete All Orders"):
        deleted_count = delete_all_orders()
        st.success(f"Successfully deleted {deleted_count} purchase orders.")
        orders = fetch_purchase_orders()  # Refresh the orders after deletion
else:
    st.info("Please confirm before deleting all orders.")
# Section for deleting a specific product from an order
st.subheader("Delete a Specific Product from an Order")
customer_id_for_product = st.text_input("Enter Customer ID of the order:")
product_id_to_delete = st.text_input("Enter Product ID to delete from the order:")
if st.button("Delete Product"):
    if customer_id_for_product and product_id_to_delete:
        modified_count = delete_product_from_order(customer_id_for_product, product_id_to_delete)
        if modified_count:
            st.success(f"Successfully deleted Product ID: {product_id_to_delete} from Customer ID: {customer_id_for_product}'s order.")
        else:
            st.error("No matching product found in the given order.")
    else:
        st.error("Please provide both a valid Customer ID and Product ID.")


# Option 1: Display the orders in a table
st.subheader("All Purchase Orders (Table View)")
display_orders_table(orders)


# Function to retrieve purchase orders from MongoDB
def fetch_purchase_orders():
    return list(orders_collection.find({}))

# Function to delete a specific order by customer_id
def delete_order_by_customer_id(customer_id):
    result = orders_collection.delete_one({'customer_id': customer_id})  # Delete order by customer_id
    return result.deleted_count

# Fetch the orders from MongoDB
orders = fetch_purchase_orders()

# Prepare the data for display in a DataFrame
if orders:
    formatted_orders = []
    for order in orders:
        for product in order['products']:
            formatted_orders.append({
                "Customer ID": order['Supplier_Name'],
                "Order Date": order['order_date'],
                "Product ID": product['product_id'],
                "Quantity": product['quantity'],
                "Price per Unit": product['price_per_unit']
            })
df = pd.DataFrame(formatted_orders)
# Display the table
st.subheader("All Purchase Orders")
st.dataframe(df)
# Extract unique Customer IDs for selection
unique_orders = df[['Customer ID', 'Order Date']].drop_duplicates()
unique_orders['Order Info'] = unique_orders['Customer ID'] + ' - ' + unique_orders['Order Date'].astype(str)

# Let the user select a row (i.e., an order) using a selectbox
selected_order = st.selectbox(
    "Select an order to delete", 
    unique_orders['Order Info'].tolist()
)


# Create an empty list for storing checkboxes to select rows
selected_customer_ids = []

st.subheader("All Purchase Orders")

# Loop through each unique order and add a checkbox for selecting the row
for order in df[['Customer ID', 'Order Date']].drop_duplicates().itertuples():
    customer_id = order[1]
    order_date = order[2]

    # Create a checkbox for each order row
    if st.checkbox(f"Select Order: {customer_id} - {order_date}", key=f"{customer_id}"):
        selected_customer_ids.append(customer_id)

    # Display the order details
    order_data = df[df['Customer ID'] == customer_id]
    st.dataframe(order_data)

# Button to delete the selected orders
if st.button("Delete Selected Orders"):
    if selected_customer_ids:
        for customer_id in selected_customer_ids:
            deleted_count = delete_order_by_customer_id(customer_id)
            if deleted_count:
                st.success(f"Successfully deleted the order for Customer ID: {customer_id}")
            else:
                st.error(f"Failed to delete the order for Customer ID: {customer_id}")
    else:
        st.warning("Please select at least one order to delete.")
else:
    st.write("No purchase orders found.")


# Parse the Customer ID from the selected option
selected_customer_id = selected_order.split(" - ")[0]  # Extract Customer ID from the selected string

# Button to delete the selected order
if st.button("Delete Selected Order"):
    deleted_count = delete_order_by_customer_id(selected_customer_id)
    if deleted_count:
        st.success(f"Successfully deleted the order for Customer ID: {selected_customer_id}")
    else:
        st.error(f"No order found for Customer ID: {selected_customer_id}")
else:
    st.write("No purchase orders found.")
# Option 2: Display each order in detail
st.subheader("All Purchase Orders (Detailed View)")
display_orders_detailed(orders)

"""
# Fetch the orders from MongoDB
orders = fetch_purchase_orders()

if orders:
    st.subheader("All Purchase Orders (Product-wise View)")
    
    # Loop through each order and display product details
    for order in orders:
        customer_id = order['Supplier_Name']
        order_date = order['order_date']
        st.write(f"**Order for Customer ID: {customer_id} on {order_date}**")
        
        # Create a DataFrame to display product details in a table
        products_df = pd.DataFrame(order['products'])
        
        # Add a column for 'Delete' buttons
        products_df['Delete'] = products_df['product_id'].apply(
            lambda product_id: st.button(f"Delete {product_id}", key=f"{customer_id}_{product_id}")
        )
        
        # Display the DataFrame (without the 'Delete' column)
        st.dataframe(products_df[['product_id', 'quantity', 'price_per_unit']])
        
        # Check if any 'Delete' button was clicked
        for product in order['products']:
            product_id = product['product_id']
            if st.session_state.get(f"{customer_id}_{product_id}", False):
                # Delete the product from the order
                deleted_count = delete_product_from_order(customer_id, product_id)
                if deleted_count:
                    st.success(f"Successfully deleted Product ID: {product_id} from Order of Customer ID: {customer_id}")
                    # Refresh page after deletion
                    st.experimental_rerun()
                else:
                    st.error(f"Failed to delete Product ID: {product_id} from Order of Customer ID: {customer_id}")
        st.write("---")
else:
    st.write("No purchase orders found.") """
    