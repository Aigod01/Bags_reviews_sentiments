""""""

import time
import random
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BRANDS              = ["Safari", "Skybags", "American Tourister", "VIP"]
PRODUCTS_PER_BRAND  = 10
REVIEWS_PER_PRODUCT = 10
PRODUCT_FILE        = "data/products.csv"
REVIEW_FILE         = "data/reviews.csv"

def create_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--lang=en-IN")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver

def wait_random(a=3, b=7):
    time.sleep(random.uniform(a, b))

def get_title(card):
    """"""
    selectors = [
        "h2 a span",
        "h2 span.a-size-medium",
        "h2 span.a-size-base-plus",
        "h2 span",
    ]
    for sel in selectors:
        try:
            val = card.find_element(By.CSS_SELECTOR, sel).text.strip()
            if val and val != "":
                return val
        except:
            continue

    try:
        return card.find_element(By.XPATH, ".//h2//span").text.strip()
    except:
        return "N/A"

def get_rating(card):
    """"""
    xpaths = [
        ".//span[@class='a-icon-alt']",
        ".//i[contains(@class,'a-star')]//span[@class='a-icon-alt']",
        ".//span[contains(@aria-label,'out of 5')]",
    ]
    for xp in xpaths:
        try:
            el = card.find_element(By.XPATH, xp)

            aria = el.get_attribute("aria-label")
            if aria and "out of" in aria:
                return aria.split(" ")[0]

            inner = el.get_attribute("innerHTML")
            if inner:
                val = inner.strip().split(" ")[0]
                try:
                    float(val)
                    return val
                except:
                    pass
        except:
            continue
    return None

def get_review_count(card):
    """"""
    xpaths = [
        ".//span[@class='a-size-base s-underline-text']",
        ".//a[@aria-label and contains(@aria-label,'rating')]",
        ".//span[contains(@aria-label,'ratings')]",
    ]
    for xp in xpaths:
        try:
            el = card.find_element(By.XPATH, xp)

            aria = el.get_attribute("aria-label")
            if aria:

                count = aria.split(" ")[0].replace(",", "")
                if count.isdigit():
                    return count

            txt = el.text.replace(",", "").strip()
            if txt.isdigit():
                return txt
        except:
            continue
    return None

def get_price(card, driver):
    """"""
    try:
        asin = card.get_attribute("data-asin")

        price = driver.execute_script(
            """""",
            asin
        )
        if price:
            return price.replace("₹", "").replace(",", "").strip()
    except:
        pass

    for sel in [".a-price .a-offscreen", ".a-price[data-a-size='xl'] .a-offscreen"]:
        try:
            els = card.find_elements(By.CSS_SELECTOR, sel)
            if els:
                val = els[0].get_attribute("innerHTML").replace("₹","").replace(",","").strip()
                if val:
                    return val
        except:
            continue
    return None

def get_mrp(card, driver):
    """"""
    try:
        asin = card.get_attribute("data-asin")
        mrp = driver.execute_script(
            """""",
            asin
        )
        if mrp:
            return mrp.replace("₹", "").replace(",", "").strip()
    except:
        pass

    for sel in [".a-price.a-text-price .a-offscreen", ".a-text-price .a-offscreen"]:
        try:
            els = card.find_elements(By.CSS_SELECTOR, sel)
            if els:
                val = els[0].get_attribute("innerHTML").replace("₹","").replace(",","").strip()
                if val:
                    return val
        except:
            continue
    return None

def calc_discount(price, mrp):
    try:
        if price and mrp and float(mrp) > 0:
            return round((1 - float(price) / float(mrp)) * 100, 1)
    except:
        pass
    return None

def get_url(card, asin):
    try:
        return card.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
    except:
        return f"https://www.amazon.in/dp/{asin}"

def get_products(driver, brand, limit=10):
    print(f"\n Scraping: {brand}")
    url = f"https://www.amazon.in/s?k={brand.replace(' ', '+')}+luggage+trolley+bag"
    driver.get(url)
    wait_random(4, 7)

    products = []
    page = 1

    while len(products) < limit:
        print(f"   Page {page} | collected: {len(products)}")

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-component-type='s-search-result']")
                )
            )
        except:
            print("    Page load failed — possible CAPTCHA. Solve it manually and press Enter.")
            input()
            continue

        cards = driver.find_elements(
            By.CSS_SELECTOR, "[data-component-type='s-search-result']"
        )
        print(f"   Found {len(cards)} cards")

        for card in cards:
            if len(products) >= limit:
                break
            try:
                asin = card.get_attribute("data-asin")
                if not asin:
                    continue

                title        = get_title(card)
                rating       = get_rating(card)
                review_count = get_review_count(card)
                price        = get_price(card, driver)
                mrp          = get_mrp(card, driver)
                discount     = calc_discount(price, mrp)
                link         = get_url(card, asin)

                products.append({
                    "brand":        brand,
                    "asin":         asin,
                    "title":        title,
                    "price":        price,
                    "mrp":          mrp,
                    "discount_pct": discount,
                    "rating":       rating,
                    "review_count": review_count,
                    "url":          link,
                })

                print(f"       {title[:50]} | ₹{price} | {rating} | {review_count} reviews")

            except Exception as e:
                print(f"   [!] Card error: {e}")
                continue

        try:
            next_btn = driver.find_element(By.CSS_SELECTOR, ".s-pagination-next")
            classes  = next_btn.get_attribute("class") or ""
            if "disabled" in classes:
                print("   Last page reached.")
                break
            next_btn.click()
            page += 1
            wait_random(3, 6)
        except:
            print("   No next page.")
            break

    print(f"    {brand}: {len(products)} products")
    return products

def get_reviews(driver, asin, brand, limit=10):
    url = f"https://www.amazon.in/product-reviews/{asin}?sortBy=recent"
    driver.get(url)
    wait_random(3, 5)

    reviews = []

    while len(reviews) < limit:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-hook='review']"))
            )
        except:
            break

        cards = driver.find_elements(By.CSS_SELECTOR, "[data-hook='review']")

        for c in cards:
            if len(reviews) >= limit:
                break
            try:
                body = c.find_element(
                    By.CSS_SELECTOR, "[data-hook='review-body'] span"
                ).text.strip()
                if not body:
                    continue

                r_rating = None
                try:
                    el = c.find_element(
                        By.CSS_SELECTOR, "[data-hook='review-star-rating'] .a-icon-alt"
                    )
                    aria = el.get_attribute("aria-label")
                    r_rating = aria.split(" ")[0] if aria else el.get_attribute("innerHTML").split(" ")[0]
                except:
                    pass

                try:
                    r_title = c.find_element(
                        By.CSS_SELECTOR, "[data-hook='review-title'] span:last-child"
                    ).text.strip()
                except:
                    r_title = ""

                try:
                    r_date = c.find_element(
                        By.CSS_SELECTOR, "[data-hook='review-date']"
                    ).text.strip()
                except:
                    r_date = ""

                reviews.append({
                    "brand":  brand,
                    "asin":   asin,
                    "title":  r_title,
                    "rating": r_rating,
                    "body":   body,
                    "date":   r_date,
                })
            except:
                continue

        try:
            driver.find_element(By.CSS_SELECTOR, ".a-last a").click()
            wait_random(2, 4)
        except:
            break

    return reviews

def main():
    os.makedirs("data", exist_ok=True)
    driver = create_driver()

    all_products = []
    all_reviews  = []

    try:

        print("\n Scraping Products ")
        for brand in BRANDS:
            items = get_products(driver, brand, PRODUCTS_PER_BRAND)
            all_products.extend(items)
            wait_random(5, 9)

        df_p = pd.DataFrame(all_products)
        df_p.to_csv(PRODUCT_FILE, index=False)
        print(f"\n Products saved  {PRODUCT_FILE} ({len(df_p)} rows)")
        print("\n Sample ")
        print(df_p[["brand","title","price","rating","discount_pct"]].head(8).to_string())

        print("\n Scraping Reviews ")
        for i, p in enumerate(all_products):
            print(f"[{i+1}/{len(all_products)}] {p['brand']} | {p['asin']}")
            reviews = get_reviews(driver, p["asin"], p["brand"], REVIEWS_PER_PRODUCT)
            print(f"    {len(reviews)} reviews")
            all_reviews.extend(reviews)
            wait_random(3, 6)

        df_r = pd.DataFrame(all_reviews)
        df_r.to_csv(REVIEW_FILE, index=False)
        print(f"\n Reviews saved  {REVIEW_FILE} ({len(df_r)} rows)")

    finally:
        driver.quit()
        print("\n Done! Now run: python src/sentiment.py")

if __name__ == "__main__":
    main()