from DrissionPage import ChromiumPage, ChromiumOptions

PNR = "765D57"
LAST_NAME = "VARDHAN"


def get_booking():

    opts = ChromiumOptions()
    opts.auto_port()
    opts.headless(False)

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

    page.listen.start("lot.com/api/v1/ibe/purchase/order-retrieve")

    page.get("https://www.lot.com/in/en")
    page.wait.doc_loaded()
    page.wait(5)

    # Accept cookies if present
    try:
        page.ele(
            'xpath://button[contains(text(),"Accept") or contains(text(),"accept") or contains(text(),"OK") or contains(@id,"accept") or contains(@id,"cookie")]',
            timeout=5
        ).click(by_js=True)
        print("Cookies accepted.")
        page.wait(1)
    except:
        print("No cookie banner found, skipping.")

    # Click Manage Booking tab
    print("Clicking Manage Booking tab...")
    page.ele(
        'xpath://*[@id="managebooking2_booker-nav-button"]',
        timeout=20
    ).click(by_js=True)
    page.wait(2)

    # Enter PNR
    print("Entering PNR...")
    pnr_input = page.ele('xpath://*[@formcontrolname="bookingReferenceField"]', timeout=20)
    pnr_input.clear()
    pnr_input.input(PNR)

    # Enter Last Name
    print("Entering Last Name...")
    last_name_input = page.ele('xpath://*[@formcontrolname="lastNameField"]', timeout=20)
    last_name_input.clear()
    last_name_input.input(LAST_NAME)

    # Click Submit
    print("Clicking Submit...")
    page.ele(
        'xpath://*[@id="ea8617864ef2df2daade3f12b6d2fe0f"]/form/button',
        timeout=20
    ).click(by_js=True)

    # Wait for API response
    print("Waiting for API response...")

    for packet in page.listen.steps(timeout=120):
        print(f"URL: {packet.url}")

        if "order-retrieve" in packet.url:
            data = packet.response.body
            page.quit()
            return data


if __name__ == "__main__":
    data = get_booking()
    print(data)