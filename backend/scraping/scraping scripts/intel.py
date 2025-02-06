import asyncio
from playwright.async_api import async_playwright
import json

async def scrape_intel_cpus():
    url = "https://www.webhallen.com/se/category/82-Processor-CPU?f=attributes%5Ebrand-1-Intel"
    scraped_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Use headless=True for final execution
        page = await browser.new_page()
        await page.goto(url)

        # Scroll and wait until all products are fully loaded
        max_attempts = 20
        for attempt in range(max_attempts):
            print(f"Scrolling attempt {attempt + 1}")
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            await asyncio.sleep(3)  # Wait for products to load
            products_loaded = await page.locator(".product-grid-item").count()
            print(f"Total products loaded so far: {products_loaded}")

            # Stop scrolling if all products are loaded
            if products_loaded >= 33:  # Total items expected
                print("All products loaded.")
                break

        # Ensure sufficient time for everything to stabilize
        await asyncio.sleep(3)

        # Select all product containers from both pages
        product_elements = await page.locator(".product-grid-item").all()

        print(f"Total products found: {len(product_elements)}")

        # Extract product data
        for product in product_elements:
            try:
                name = await product.locator("span.product-list-item-title").inner_text()
                specs = await product.locator("span.product-list-subtitle").inner_text()
                price_element = await product.locator(".price-value").all_inner_texts()
                price = price_element[0] if price_element else "N/A"
                scraped_data.append({
                    "name": name.strip(),
                    "specs": specs.strip(),
                    "price": price.strip()
                })
            except Exception as e:
                print(f"Error scraping product: {e}")

        await browser.close()

    # Save the scraped data to a JSON file
    output_file = "intel_cpus.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(scraped_data, file, ensure_ascii=False, indent=4)

    print(f"Data saved to {output_file}")

# Run the scraping function
if __name__ == "__main__":
    asyncio.run(scrape_intel_cpus())
