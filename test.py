from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_selenium():
    print("Setting up Chrome driver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    print("Opening Google...")
    driver.get("https://www.google.com")
    print(f"Page title: {driver.title}")
    
    driver.quit()
    print("Test completed successfully")

if __name__ == "__main__":
    test_selenium()
