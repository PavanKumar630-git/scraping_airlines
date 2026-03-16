from DrissionPage import ChromiumPage, ChromiumOptions


class AzalBooking:

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
        self.page.listen.start("www.azal.az/book/api/orders/search")

        self.page.get("https://www.azal.az/en/index.html#booking")

        self.page.wait.doc_loaded()
        self.page.wait(5)

        # Accept cookies if present
        try:
            self.page.ele(
                'xpath://button[contains(text(),"Accept") or contains(text(),"accept") or contains(text(),"OK") or contains(text(),"Agree")]',
                timeout=5
            ).click(by_js=True)
            print("Cookies accepted.")
            self.page.wait(1)
        except:
            print("No cookie banner found, skipping.")

    def open_manage_booking(self):
        print("Clicking Manage Booking tab...")

        self.page.ele(
            'xpath://*[@id="mainPage"]/div[1]/div[2]/div/div/div/div[1]/div[1]/button[3]',
            timeout=20
        ).click(by_js=True)

        self.page.wait(2)

    def enter_booking_details(self):
        print("Entering Last Name...")
        last_name_input = self.page.ele(
            'xpath://*[@id="mainPage"]/div[1]/div[2]/div/div/div/div[1]/div[2]/div/form/div/div[1]/label/div[1]/input',
            timeout=20
        )
        last_name_input.clear()
        last_name_input.input(self.last_name)

        print("Entering PNR...")
        pnr_input = self.page.ele(
            'xpath://*[@id="mainPage"]/div[1]/div[2]/div/div/div/div[1]/div[2]/div/form/div/div[2]/label/div[1]/input',
            timeout=20
        )
        pnr_input.clear()
        pnr_input.input(self.pnr)

    def search_booking(self):
        print("Clicking Submit...")
        submit_btn = self.page.ele(
            'xpath://*[@id="mainPage"]/div[1]/div[2]/div/div/div/div[1]/div[2]/div/form/button',
            timeout=20
        )
        submit_btn.click()

    def capture_api(self):
        print("Waiting for API response...")

        for packet in self.page.listen.steps(timeout=120):
            print(f"URL: {packet.url}")

            if "orders/search" in packet.url:
                data = packet.response.body
                self.page.quit()
                return data

    def get_booking(self):
        self.init_browser()
        self.open_site()
        # self.open_manage_booking()
        self.enter_booking_details()
        self.search_booking()

        return self.capture_api()


# if __name__ == "__main__":

#     PNR = "YOUR_PNR"
#     LAST_NAME = "YOUR_LAST_NAME"

#     scraper = AzalBooking(PNR, LAST_NAME)

#     data = scraper.get_booking()

#     print(data)