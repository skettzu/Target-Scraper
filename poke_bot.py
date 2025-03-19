import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import os
from datetime import datetime
# To Do: Fix tcin [done], confirm stock checking[done], and purchasing

global all_url
class TargetPokemonBot:
    def __init__(self, target_email, target_password, check_interval=30):
        self.target_email = target_email
        self.target_password = target_password
        self.check_interval = check_interval
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        self.tcin = self.extract_tcin_from_url()
        #self.setup_browser()
        
    def extract_tcin_from_url(self):
        # Extract the TCIN (Target's product ID) from the URL
        # Example URL: https://www.target.com/p/pokemon-trading-card-game/-/A-12345678
        try:
            tcins = ""
            for url in all_url:
                tcin = url.split("A-")[1].split("#")[0]
                tcins += tcin
                tcins += ','
            tcins = tcins[:-1]
            return tcins
        except:
            print("Could not extract TCIN from URL. Please check the URL format.")
            return None
    
    def setup_browser(self):
        chrome_options = Options()
        self.driver = webdriver.Chrome(options=chrome_options)
        stealth(self.driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
        # Uncomment the line below if you want to run in headless mode
        # chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--window-size=1920,1080")
        #chrome_options.add_argument("--disable-notifications")
        
    def check_stock(self):
        """Check if the product is in stock using Target's API"""
        try:
            # Use Target's API to check stock
            api_url = f"https://redsky.target.com/redsky_aggregations/v1/web/product_summary_with_fulfillment_v1?key=9f36aeafbe60771e321a7cc95a78140772ab3e96&channel=WEB&tcins={self.tcin}"
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"Failed to check stock: {response.status_code}")
                print(f"API: {api_url}")
                return False, 0
                
            data = json.loads(response.text)
            
            # Check if product summaries exist
            if not data.get("data", {}).get("product_summaries", []):
                print("No product data found")
                return False, 0
                
            # Get the first product summary
            for x in range(len(data["data"]["product_summaries"])):
                print(f"Currently checking {all_url[x]} for stock")
                # Check if the product is available for shipping
                product_summary = data["data"]["product_summaries"][x]
                fulfillment = product_summary.get("fulfillment", {})
                shipping_options = fulfillment.get("shipping_options", {})
                
                # Check availability status
                is_available = False
                if shipping_options.get("availability_status") == "IN_STOCK":
                    print(f"{all_url[x]} is in stock!")
                    is_available = True
                    # set product url for purchasing
                    self.product_url = all_url[x]
                    return is_available, 1
                
                # Determine if product is sold out
                if fulfillment.get("sold_out", True):
                    is_available = False
                    return is_available, 1
                    
                # Get max quantity if available
                #max_quantity = 1
            '''
            if is_available and "shipping_options" in fulfillment:
                for option in fulfillment["shipping_options"]:
                    if "available_to_promise_quantity" in option:
                        max_quantity = min(option["available_to_promise_quantity"], 
                                          fulfillment.get("limits", {}).get("max_allowed_quantity", 1))
            '''
            return is_available, 1
        
        except Exception as e:
            print(f"Error checking stock: {e}")
            print(f"Response: {data}")
            return False, 0
    
    def login_to_target(self):
        """Log in to Target.com"""
        try:
            self.driver.get("https://www.target.com/account")
            
            # Wait for login form
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Enter credentials
            self.driver.find_element(By.ID, "username").send_keys(self.target_email)
            self.driver.find_element(By.ID, "password").send_keys(self.target_password)
            
            # Click login button
            self.driver.find_element(By.ID, "login").click()
            '''
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "Maybe Later"))
                )
                self.driver.find_element(By.ID, "Maybe Later").click()
            except:
                WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "Purchase history"))
                )
                print("Successfully logged in to Target")
                return True
            # Wait for successful login
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "Purchase history"))
            )
            '''
            print("Successfully logged in to Target")
            return True
            
        except Exception as e:
            print(f"Failed to login: {e}")
            return False
    
    def purchase_product(self, quantity):
        """Purchase the product"""
        try:
            # Navigate to product page
            self.driver.get(self.product_url)
            
            # Wait for product page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='shipItButton']"))
            )
            
            # Set quantity if more than 1
            if quantity > 1:
                # Find and click quantity dropdown
                quantity_dropdown = self.driver.find_element(By.CSS_SELECTOR, "[data-test='quantityPicker']")
                quantity_dropdown.click()
                
                # Select desired quantity
                quantity_option = self.driver.find_element(By.CSS_SELECTOR, f"[data-value='{quantity}']")
                quantity_option.click()
            
            # Click "Ship it" button
            ship_button = self.driver.find_element(By.CSS_SELECTOR, "[data-test='shipItButton']")
            ship_button.click()
            
            # Wait for cart page and click checkout
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='checkout-button']"))
            )
            checkout_button = self.driver.find_element(By.CSS_SELECTOR, "[data-test='checkout-button']")
            checkout_button.click()
            
            # Wait for checkout page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='placeOrderButton']"))
            )
            
            # Place order
            place_order_button = self.driver.find_element(By.CSS_SELECTOR, "[data-test='placeOrderButton']")
            place_order_button.click()
            
            # Wait for order confirmation
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ThankYouPage"))
            )
            
            print("Order successfully placed!")
            return True
            
        except Exception as e:
            print(f"Failed to purchase product: {e}")
            return False
    
    def monitor_and_purchase(self):
        """Monitor the product and purchase when in stock"""
        print(f"Starting to monitor {all_url}")
        
        while True:
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{current_time}] Checking stock...")
                
                is_available, max_quantity = self.check_stock()
                
                if is_available and max_quantity > 0:
                    print(f"Product is in stock! Available quantity: {max_quantity}")
                    purchase_success = self.purchase_product(max_quantity)
                    
                    if purchase_success:
                        print("Purchase completed successfully!")
                        break
                    else:
                        print("Purchase failed. Will try again in the next cycle.")
                else:
                    print("Product is not in stock. Waiting for restock...")
                
                # Wait before checking again
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def cleanup(self):
        """Close the browser and clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()

# Example usage
if __name__ == "__main__":
    all_url = ["https://www.target.com/p/pokemon-scarlet-violet-s3-5-booster-bundle-box/-/A-88897904", "https://www.target.com/p/2024-pok-scarlet-violet-s8-5-elite-trainer-box/-/A-93954435",
                   "https://www.target.com/p/2025-pokemon-prismatic-evolutions-accessory-pouch-special-collection/-/A-94300053", "https://www.target.com/p/pok-233-mon-trading-card-game-scarlet-38-violet-prismatic-evolutions-booster-bundle/-/A-93954446",
                   "https://www.target.com/p/pok-233-mon-trading-card-game-scarlet-38-violet-8212-journey-together-booster-bundle/-/A-94300074", "https://www.target.com/p/pokemon-trading-card-game-scarlet-38-violet-surging-sparks-booster-bundle/-/A-91619929"]
    target_email = "gameflip1244@gmail.com"
    target_password = "Boostingplease123"
    
    bot = TargetPokemonBot(target_email, target_password, check_interval=30)
    
    try:
        bot.monitor_and_purchase()
    except KeyboardInterrupt:
        print("Closing Program and Cleaning up...")
    finally:
        bot.cleanup()
        print("Successfully Exited!")
