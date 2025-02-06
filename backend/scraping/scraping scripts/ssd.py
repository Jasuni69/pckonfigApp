import asyncio
from playwright.async_api import async_playwright
import json

async def scrape_infinite_scroll():
    url = "https://www.webhallen.com/se/category/50-Lagring?page=1&f=attributes%5Ecustom.cnet_harddisk_formfaktor_222-1-M.2%202280"
    scraped_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        # Scroll until no more products to load
        while True:
            products_before_scroll = await page.locator(".product-grid-item").count()
            await page.mouse.wheel(0, 3000)
            await asyncio.sleep(2)  # Wait for new products to load
            products_after_scroll = await page.locator(".product-grid-item").count()

            if products_after_scroll == products_before_scroll:
                print("No more products to load.")
                break

        # Select all product containers
        product_elements = await page.locator(".product-grid-item").all()

        # Extract product data
        for product in product_elements:
            name = await product.locator("span.product-list-item-title").inner_text()
            specs = await product.locator("span.product-list-subtitle").inner_text()
            price_element = await product.locator(".price-value").all_inner_texts()
            price = price_element[0] if price_element else "N/A"
            scraped_data.append({
                "name": name.strip(),
                "specs": specs.strip(),
                "price": price.strip()
            })

        await browser.close()

    # Save the scraped data to a JSON file
    output_file = "ssd.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(scraped_data, file, ensure_ascii=False, indent=4)

    print(f"Data saved to {output_file}")

# Run the scraping function
if __name__ == "__main__":
    asyncio.run(scrape_infinite_scroll())
