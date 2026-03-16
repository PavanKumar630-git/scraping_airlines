from DrissionPage import ChromiumPage, ChromiumOptions

PNR = "9QOX8K"
LAST_NAME = "BHATIA"


def get_booking():

    opts = ChromiumOptions()
    opts.auto_port()
    opts.headless(True)

    opts.set_argument('--window-size=1920,1080')
    opts.set_argument('--disable-gpu')
    opts.set_argument('--no-sandbox')
    opts.set_argument('--disable-dev-shm-usage')
    opts.set_argument("--disable-blink-features=AutomationControlled")
    opts.set_user_agent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    )

    page = ChromiumPage(opts)

    page.listen.start("api-des.malaysiaairlines.com")

    page.get("https://www.malaysiaairlines.com/my/en/home.html")
    page.wait.doc_loaded()
    page.wait(5)

    # Accept cookies
    try:
        page.ele('xpath:/html/body/div[2]/div/div/div[2]/div/div/div/div[2]/button', timeout=5).click(by_js=True)
        print("Cookies accepted.")
        page.wait(1)
    except:
        print("No cookie banner found, skipping.")

    # Click Manage Booking tab
    print("Clicking Manage Booking tab...")

    manage_tab_selectors = [
        'xpath://span[text()="Manage booking"]',
        'xpath://span[contains(text(),"Manage booking")]',
        'xpath://span[contains(text(),"Manage Booking")]',
        'xpath://button[contains(.,"Manage booking")]',
        'xpath://button[contains(.,"Manage Booking")]',
        'xpath://div[contains(@id,"swiper-wrapper")]//div[3]/button',
    ]

    clicked = False
    for selector in manage_tab_selectors:
        try:
            page.ele(selector, timeout=5).click(by_js=True)
            clicked = True
            print(f"Manage Booking tab clicked using: {selector}")
            break
        except:
            continue

    if not clicked:
        # Debug: print all buttons to find correct selector
        print("\n--- DEBUG: All buttons on page ---")
        buttons = page.eles('xpath://button')
        for i, btn in enumerate(buttons):
            print(f"  [{i}] text='{btn.text.strip()[:60]}' | id='{btn.attr('id')}'")
        print("----------------------------------\n")
        raise Exception("Could not find Manage Booking tab — check debug output above")

    page.wait(2)

    # Enter Last Name
    print("Entering Last Name...")
    last_name_input = page.ele('xpath://*[@id="manage-booking"]/div/form/div[3]/div[1]/div/div[1]/div/label/div[2]/input', timeout=20)
    last_name_input.clear()
    last_name_input.input(PNR)

    # Enter PNR
    print("Entering PNR...")
    pnr_input = page.ele('xpath://*[@id="manage-booking"]/div/form/div[3]/div[2]/div/div[1]/div/label/div[2]/input', timeout=20)
    pnr_input.clear()
    pnr_input.input(LAST_NAME)

    # Click Submit
    print("Clicking Submit...")
    submit_btn = page.ele('xpath://*[@id="manage-booking"]/div/form/div[3]/div[3]/div/button', timeout=20)
    submit_btn.click()

    print("Waiting for API response...")

    for packet in page.listen.steps(timeout=120):
        print(f"URL: {packet.url}")
        if "purchase/orders" in packet.url:
            data = packet.response.body
            page.quit()
            return data


if __name__ == "__main__":
    data = get_booking()
    print(data)