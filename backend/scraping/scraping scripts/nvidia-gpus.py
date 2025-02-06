import asyncio
from playwright.async_api import async_playwright
import json

async def scrape_nvidia_gpus():
    url_template = "https://www.webhallen.com/se/category/47-Grafikkort-GPU?f=attributes%5Ecustom.cnet_videoutgang_chiptillverkare_906-1-NVIDIA%20Geforce&page={}"
    scraped_data = []
    page_number = 1

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        while True:
            url = url_template.format(page_number)
            await page.goto(url)
            await asyncio.sleep(3)  # Wait for the page to fully load
            print(f"Scraping page {page_number}...")

            # Check if there are products on this page
            products_on_page = await page.locator(".product-grid-item").count()
            print(f"Products found on page {page_number}: {products_on_page}")

            if products_on_page == 0:
                print("No more products to load.")
                break

            # Select all product containers
            product_elements = await page.locator(".product-grid-item").all()

            # Extract product data
            for product in product_elements:
                try:
                    name = await product.locator("span.product-list-item-title").inner_text()
                except Exception:
                    name = "N/A"

                try:
                    specs_locator = product.locator("span.product-list-subtitle")
                    if await specs_locator.count() > 0:
                        specs = await specs_locator.inner_text()
                    else:
                        specs = "N/A"
                except Exception:
                    specs = "N/A"

                try:
                    price_element = await product.locator(".price-value").all_inner_texts()
                    price = price_element[0] if price_element else "N/A"
                except Exception:
                    price = "N/A"

                scraped_data.append({
                    "name": name.strip(),
                    "specs": specs.strip(),
                    "price": price.strip()
                })

            # Move to the next page
            page_number += 1

        await browser.close()

    # Save the scraped data to a JSON file
    output_file = "nvidia_gpus.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(scraped_data, file, ensure_ascii=False, indent=4)

    print(f"Data saved to {output_file}")

# Run the scraping function
if __name__ == "__main__":
    asyncio.run(scrape_nvidia_gpus())
