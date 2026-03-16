from DrissionPage import ChromiumPage, ChromiumOptions


class MalaysiaBooking:

    def __init__(self, pnr, last_name):
        self.pnr = pnr
        self.last_name = last_name
        self.page = None

    def init_browser(self):
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

        self.page = ChromiumPage(opts)

    def open_site(self):
        self.page.listen.start("api-des.malaysiaairlines.com")

        self.page.get("https://www.malaysiaairlines.com/my/en/home.html")
        self.page.wait.doc_loaded()
        self.page.wait(5)

        # Accept cookies
        try:
            self.page.ele(
                'xpath:/html/body/div[2]/div/div/div[2]/div/div/div/div[2]/button',
                timeout=5
            ).click(by_js=True)
            print("Cookies accepted.")
            self.page.wait(1)
        except:
            print("No cookie banner found, skipping.")

    def open_manage_booking(self):
        print("Clicking Manage Booking tab...")

        manage_tab_selectors = [
            # 'xpath://span[text()="Manage booking"]',
            # 'xpath://span[contains(text(),"Manage booking")]',
            # 'xpath://span[contains(text(),"Manage Booking")]',
            # 'xpath://button[contains(.,"Manage booking")]',
            # 'xpath://button[contains(.,"Manage Booking")]',
            'xpath://div[contains(@id,"swiper-wrapper")]//div[3]/button',
        ]

        clicked = False
        for selector in manage_tab_selectors:
            try:
                self.page.ele(selector, timeout=5).click(by_js=True)
                clicked = True
                print(f"Manage Booking tab clicked using: {selector}")
                break
            except:
                continue

        if not clicked:
            print("\n--- DEBUG: All buttons on page ---")
            buttons = self.page.eles('xpath://button')
            for i, btn in enumerate(buttons):
                print(f"  [{i}] text='{btn.text.strip()[:60]}' | id='{btn.attr('id')}'")
            print("----------------------------------\n")
            raise Exception("Could not find Manage Booking tab — check debug output above")

        self.page.wait(2)

    def enter_booking_details(self):
        print("Entering PNR Code...")
        pnr_enter = self.page.ele(
            'xpath://*[@id="manage-booking"]/div/form/div[3]/div[1]/div/div[1]/div/label/div[2]/input',
            timeout=20
        )
        pnr_enter.clear()
        pnr_enter.input(self.pnr)

        print("Entering Last Name...")
        last_name_enter = self.page.ele(
            'xpath://*[@id="manage-booking"]/div/form/div[3]/div[2]/div/div[1]/div/label/div[2]/input',
            timeout=20
        )
        last_name_enter.clear()
        last_name_enter.input(self.last_name)

    def search_booking(self):
        print("Clicking Submit...")
        submit_btn = self.page.ele(
            'xpath://*[@id="manage-booking"]/div/form/div[3]/div[3]/div/button',
            timeout=20
        )
        submit_btn.click()

    def capture_api(self):
        print("Waiting for API response...")

        for packet in self.page.listen.steps(timeout=120):
            print(f"URL: {packet.url}")

            if "purchase/orders" in packet.url:
                data = packet.response.body
                self.page.quit()
                return data

    def get_booking(self):
        self.init_browser()
        self.open_site()
        self.open_manage_booking()
        self.enter_booking_details()
        self.search_booking()

        return self.capture_api()


# if __name__ == "__main__":

#     PNR = "TCFXYT"
#     LAST_NAME = "GIANGIULIO"

#     scraper = MalaysiaBooking(PNR, LAST_NAME)

#     data = scraper.get_booking()

#     print(data)