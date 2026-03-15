from DrissionPage import ChromiumPage, ChromiumOptions
import time

PNR = "8O2XSR"
LAST_NAME = "AHUJA"


def get_booking():

    
    # opts = ChromiumOptions()
    # opts.auto_port()

    # # run headless
    # opts.headless(False)

    # # make headless behave like normal browser
    # opts.set_argument('--window-size=1920,1080')
    # opts.set_argument('--disable-gpu')
    # opts.set_argument('--no-sandbox')
    # opts.set_argument('--disable-dev-shm-usage')
    # opts.set_argument('--disable-blink-features=AutomationControlled')

    # page = ChromiumPage(opts)



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
        "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    )

    page = ChromiumPage(opts)

    page.listen.start("api-des.srilankan.com")

    page.get("https://www.srilankan.com/en_uk/in")

    page.wait.doc_loaded()
    page.wait(5)

    # Accept cookies if present
    try:
        page.ele('#onetrust-accept-btn-handler', timeout=5).click()
    except:
        pass

    print("Opening Manage Booking tab...")
        # click manage booking tab
    # click manage booking tab
    page.ele('xpath://*[@id="bookingWidget"]/section/div[1]/button[2]', timeout=20).click(by_js=True)

    page.wait(2)

    # enter last name
    last_name_input = page.ele('#lastname2refx', timeout=20)
    last_name_input.clear()
    last_name_input.input(LAST_NAME)

    # enter booking reference
    pnr_input = page.ele('#bookref2refx', timeout=20)
    pnr_input.clear()
    pnr_input.input(PNR)

    # click search
    search_btn = page.ele('#btnMybSearch', timeout=20)
    search_btn.click()
    
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