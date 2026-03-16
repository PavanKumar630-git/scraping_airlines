from DrissionPage import ChromiumPage, ChromiumOptions

PNR = "8AdSOGV"
LAST_NAME = "CHOdfUHAN"


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

    page.listen.start("azal.az/book/api/orders/search")

    page.get("https://www.azal.az/en/index.html#booking")
    page.wait.doc_loaded()
    page.wait(5)

    # Accept cookies if present
    try:
        page.ele(
            'xpath://button[contains(text(),"Accept") or contains(text(),"accept") or contains(text(),"OK") or contains(text(),"Agree")]',
            timeout=5
        ).click(by_js=True)
        print("Cookies accepted.")
        page.wait(1)
    except:
        print("No cookie banner found, skipping.")

    # Click Manage Booking tab
    print("Clicking Manage Booking tab...")
    page.ele(
        'xpath://*[@id="mainPage"]/div[1]/div[2]/div/div/div/div[1]/div[1]/button[3]',
        timeout=20
    ).click(by_js=True)
    page.wait(2)

    # Enter Last Name
    print("Entering Last Name...")
    last_name_input = page.ele(
        'xpath://*[@id="mainPage"]/div[1]/div[2]/div/div/div/div[1]/div[2]/div/form/div/div[1]/label/div[1]/input',
        timeout=20
    )
    last_name_input.clear()
    last_name_input.input(LAST_NAME)

    # Enter PNR
    print("Entering PNR...")
    pnr_input = page.ele(
        'xpath://*[@id="mainPage"]/div[1]/div[2]/div/div/div/div[1]/div[2]/div/form/div/div[2]/label/div[1]/input',
        timeout=20
    )
    pnr_input.clear()
    pnr_input.input(PNR)

    # Click Submit
    print("Clicking Submit...")
    page.ele(
        'xpath://*[@id="mainPage"]/div[1]/div[2]/div/div/div/div[1]/div[2]/div/form/button',
        timeout=20
    ).click()

    print("Waiting for API response...")

    for packet in page.listen.steps(timeout=120):
        print(f"URL: {packet.url}")

        if "orders/search" in packet.url:
            data = packet.response.body
            page.quit()
            return data


if __name__ == "__main__":
    data = get_booking()
    print(data)