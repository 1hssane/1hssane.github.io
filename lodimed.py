import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def setup_driver():
    print("Setting up the Chrome WebDriver...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Optional: comment this if you want to see the browser
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    print("WebDriver setup complete.")
    return driver
def get_soup(driver, url):
    """Parse the content of a webpage using BeautifulSoup."""
    print(f"Navigating to the target page: {url}")
    driver.get(url)
    time.sleep(2)  # Wait for page to load
    print("Page loaded. Parsing the content...")
    return BeautifulSoup(driver.page_source, 'html.parser')
# API Configuration
API_URL = "https://api.sns.sobrus.ovh/api/purchase-orders/robot" 
LINK = "https://lodimed.ma"



def login_to_website(driver, url, username, password):
    print(f"Navigating to the login page: {url}")
    driver.get(url)

    # Wait until the email input field is present
    print("Waiting for the email input field to be present...")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))  # Use ID locator
    
    # Find the email and password input fields and the login button
    print("Locating the input fields and login button...")
    email_input = driver.find_element(By.ID, "email")  
    password_input = driver.find_element(By.NAME, "password") 
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']") 

    # Enter the login credentials
    print("Entering email and password...")
    email_input.send_keys(username)
    password_input.send_keys(password)

    # Submit the form by clicking the login button
    print("Submitting the login form...")
    login_button.click()

    # Wait for either the URL to change or a specific element that only appears post-login
    try:
        print("Waiting for the page to load after login...")
        
        # Option 1: Wait for URL change (login redirects to a new page)
        WebDriverWait(driver, 10).until(EC.url_changes(url))  # Wait until the URL changes from the login page

        print("Login successful and page transition confirmed.")
    except:
        print("Login failed or no page transition detected.")
        driver.quit()
        raise Exception("Login failed or stuck on login page.")
def passing_cmd(driver, product, quantity):
    """Place an order with the specified product and quantity."""
    # Step 1: Navigate to "Commandez maintenant"
    print("Navigating to the Commandez maintenant page...")
    command_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.nav-link[href='https://lodimed.ma/cart']"))
    )
    command_link.click()
    print("Successfully clicked on 'Commandez maintenant' link.")
    
    # Step 2: Wait for the product input field to be visible and input a product
    print("Waiting for the product input field to be visible...")
    product_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "productsfield"))
    )
    print("Product input field is visible. Entering product name...")
    product_field.send_keys(product)
    print(f"Entered product name: '{product}'.")

    # Step 3: Input the quantity
    print("Waiting for the quantity input field to be visible...")
    quantity_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "showquantite"))
    )
    quantity_field.clear()
    quantity_field.send_keys(str(quantity))
    print(f"Entered quantity: '{quantity}'.")

    # Step 4: Click the add button to add the product to the grid
    print("Waiting for the Add button to be clickable...")
    add_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "addTableRow"))
    )
    add_button.click()
    print("Clicked the add button.")

    # Step 5: Wait for the checkout button and click it
    print("Waiting for the checkout button to be clickable...")
    checkout_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btn-checkout"))
    )
    checkout_button.click()
    print("Successfully clicked the checkout button.")

    print("Order placed successfully.")
    time.sleep(2)
def check_orders(driver):
    """Check current orders on the website."""
    print("Navigating to 'Commandes en cours'...")

    orders_url = "https://lodimed.ma/Commandes"
    driver.get(orders_url)
    print(f"Navigated directly to: {orders_url}")

    # Wait for the orders table to load
    print("Waiting for the orders table to load...")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "myTable"))
    )
    print("Orders table is now visible.")

    # Wait for any dynamic content to load
    time.sleep(2)

    # Find the most recent 'Detail demmandés' link
    print("Looking for the most recent 'Detail demmandés' link...")
    detail_links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//a[contains(@class, 'btn-outline-primary') and contains(text(), 'Detail demmandés')]")
        )
    )

    if detail_links:
        # Get the first (most recent) link
        detail_link = detail_links[0]
        print(f"Found link with href: {detail_link.get_attribute('href')}")
        
        # Ensure the element is in view and click it
        driver.execute_script("arguments[0].scrollIntoView(true);", detail_link)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", detail_link)
        print("Clicked on the 'Detail demmandés' link.")

        # Wait for the details page to load
        print("Waiting for the details page to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-striped"))
        )

        try:
            # Get the entire row's outer HTML for full inspection
            entire_row = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//table[@class='table table-striped']//tbody//tr[1]")
                )
            )
            
            # Use outerHTML to inspect the entire row
            entire_row_html = entire_row.get_attribute("outerHTML").strip()
            print(f"Entire row HTML: '{entire_row_html}'")  # Debugging step to see the full row content

            # Extract data from the row
            columns = entire_row.find_elements(By.TAG_NAME, "td")  # Find all td elements in the row

            # Extract data from relevant columns (adjust indexes if needed)
            if len(columns) >= 8:  # Ensure there are enough columns
                designation = columns[1].text.strip()
                price_per_unit = columns[2].text.strip()
                quantity = columns[3].text.strip()
                qte_liv = columns[7].text.strip()  # The QTE LIV value is in the 8th column

                print(f"Designation: '{designation}', Price per unit: '{price_per_unit}', Quantity: '{quantity}', QTE LIV: '{qte_liv}'")
                return qte_liv
            else:
                print("The expected number of columns was not found in the row.")

        except Exception as e:
            print(f"Error extracting row data: {str(e)}")
    else:
        print("No detail links found.")
def get_orders(max_retries=3, delay=1):
    """Fetch purchase orders using the GET API with pagination and retry logic."""
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"link": LINK}
    all_orders = []
    page = 1

    while True:
        params['page'] = page
        
        for attempt in range(max_retries):
            try:
                response = requests.get(API_URL, headers=headers, params=params, timeout=10)
                response.raise_for_status()  # Raises an HTTPError for bad responses
                
                print(f"Response Status Code: {response.status_code}")
                print(f"Response Body: {response.text[:500]}...")  # Print first 500 characters
                
                data = response.json()
                
                if not data or 'data' not in data:
                    print(f"No data found on page {page}. Ending pagination.")
                    return all_orders
                
                orders = data['data']
                all_orders.extend(orders)
                
                print(f"Fetched {len(orders)} orders from page {page}")
                
                for order in orders:
                    print(f"Order Number: {order.get('orderNumber')}, Username: {order.get('username')}")
                    for product in order.get('products', []):
                        print(f"  Product ID: {product.get('productId')}, Ordered Quantity: {product.get('orderedQuantity')}")
                
                # Check if there's a next page
                if 'next_page_url' not in data or not data['next_page_url']:
                    print("No more pages. Ending pagination.")
                    return all_orders
                
                page += 1
                break  # Successful request, break the retry loop
            
            except requests.exceptions.RequestException as e:
                print(f"Request failed on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    print("Max retries reached. Ending pagination.")
                    return all_orders
                time.sleep(delay)  # Wait before retrying
    
    return all_orders
orders = get_orders()
import requests
import json  
import time
def update_orders(orders):
    """Update purchase orders using the PATCH API."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "link": LINK,
        "data": [
            {
                "orderNumber": order['orderNumber'],
                "products": [
                    {
                        "productId": product['productId'],
                        "orderedQuantity": product['orderedQuantity'],
                        "acceptedQuantity": product['acceptedQuantity'] 
                    } for product in order['products']
                ]
            } for order in orders
        ]
    }

    try:
        response = requests.patch(API_URL, headers=headers, data=json.dumps(payload), timeout=10)
        response.raise_for_status()

        print(f"Update Response Status Code: {response.status_code}")
        print(f"Update Response Body: {response.text[:500]}...")  # Print first 500 characters

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error updating orders: {str(e)}")
        return None
# Usage of the get_orders function
if __name__ == "__main__":
    driver = setup_driver()
    
    login_url = "https://lodimed.ma/login"  # Replace with the actual login URL
    target_url = "https://lodimed.ma/cart"  # Replace with the target URL after login
    username = "BADIR_SARL_MARR@LODIMED.MA"  # Replace with your actual email
    password = "10264252024"  # Replace with your actual password
    
    print("Starting the login process...")
    
    # Log in to the website
    login_to_website(driver, login_url, username, password)
    print("Login process completed. Now fetching orders...")

    # Fetch orders from the API
    orders = get_orders()
    
    if orders:
        # Assuming you want to place an order for the first order retrieved
        first_order = orders[0]
        product_name = first_order['products'][0]['productId']  # This can be fetched from the order
        product_quantity = first_order['products'][0]['orderedQuantity']  # Example extraction
        
        print(f"Placing order for product {product_name} with quantity {product_quantity}...")
        
        # Pass product and quantity to the command placement function
        passing_cmd(driver, product_name, product_quantity)

        # Now check the orders after placing the command
        time.sleep(3)
        qte_liv_value = check_orders(driver)
        
        if qte_liv_value is not None:
            print(f"Quantity Delivered (QTE LIV): {qte_liv_value}")
        else:
            print("Failed to retrieve the quantity delivered.")
        # Updating orders based on the retrieved delivered quantity
        for order in orders:
            for product in order['products']:
                product['acceptedQuantity'] = qte_liv_value  # Update acceptedQuantity with delivered quantity

        # Call update_orders function to send a PATCH request to the API
        update_response = update_orders(orders)

        if update_response:
            print("Orders successfully updated with delivered quantities.")
        else:
            print("Failed to update the orders.")
    
    # Close the browser after the entire process
    print("Closing the browser...")
    #driver.quit()
    print("Browser closed.")
