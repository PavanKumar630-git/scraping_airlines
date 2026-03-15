from DrissionPage import ChromiumPage, ChromiumOptions
import time


class SriLankanBooking:

    def __init__(self, pnr, last_name):
        self.pnr = pnr
        self.last_name = last_name
        self.page = None

    def init_browser(self):
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

        self.page = ChromiumPage(opts)

    def open_site(self):
        self.page.listen.start("api-des.srilankan.com")

        self.page.get("https://www.srilankan.com/en_uk/in")
        self.page.wait.doc_loaded()
        self.page.wait(5)

        # Accept cookies
        try:
            self.page.ele('#onetrust-accept-btn-handler', timeout=5).click()
        except:
            pass

    def open_manage_booking(self):
        print("Opening Manage Booking tab...")

        self.page.ele(
            'xpath://*[@id="bookingWidget"]/section/div[1]/button[2]',
            timeout=20
        ).click(by_js=True)

        self.page.wait(2)

    def enter_booking_details(self):

        # Last name
        last_name_input = self.page.ele('#lastname2refx', timeout=20)
        last_name_input.clear()
        last_name_input.input(self.last_name)

        # Booking reference
        pnr_input = self.page.ele('#bookref2refx', timeout=20)
        pnr_input.clear()
        pnr_input.input(self.pnr)

    def search_booking(self):

        search_btn = self.page.ele('#btnMybSearch', timeout=20)
        search_btn.click()

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

#     PNR = "8O2XSR"
#     LAST_NAME = "AHUJA"

#     scraper = SriLankanBooking(PNR, LAST_NAME)

#     data = scraper.get_booking()

#     print(data)