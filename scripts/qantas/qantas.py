from DrissionPage import ChromiumPage, ChromiumOptions


class QantasBooking:
    BASE_URL    = "https://www.qantas.com/en-in/manage-booking"
    API_PATTERN = "qantas.com"

    COOKIE_XPATH = (
        'xpath://button[contains(text(),"Accept") or contains(text(),"accept") '
        'or contains(text(),"OK") or contains(@id,"accept") or contains(@id,"cookie")]'
    )
    PNR_XPATH = (
        'xpath:/html/body/main/div[3]/div[1]/div/div/div/div/form/div[2]/div/div[1]/input'
    )
    LAST_NAME_XPATH = (
        'xpath:/html/body/main/div[3]/div[1]/div/div/div/div/form/div[2]/div/div[2]/input'
    )
    SUBMIT_XPATH = (
        'xpath:/html/body/main/div[3]/div[1]/div/div/div/div/form/div[2]/div/div[3]/input'
    )

    def __init__(self, pnr: str, last_name: str, headless: bool = False):
        self.pnr       = pnr
        self.last_name = last_name
        self.headless  = headless
        self.page: ChromiumPage | None = None

    # ------------------------------------------------------------------ #
    #  Setup                                                               #
    # ------------------------------------------------------------------ #

    def _build_options(self) -> ChromiumOptions:
        opts = ChromiumOptions()
        opts.auto_port()
        opts.headless(self.headless)
        opts.set_argument("--window-size=1920,1080")
        opts.set_argument("--disable-gpu")
        opts.set_argument("--no-sandbox")
        opts.set_argument("--disable-dev-shm-usage")
        opts.set_argument("--disable-blink-features=AutomationControlled")
        opts.set_user_agent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        )
        return opts

    def _init_page(self) -> None:
        self.page = ChromiumPage(self._build_options())

    # ------------------------------------------------------------------ #
    #  Page actions                                                        #
    # ------------------------------------------------------------------ #

    def _open_site(self) -> None:
        self.page.listen.start(self.API_PATTERN)
        self.page.get(self.BASE_URL)
        self.page.wait.doc_loaded()
        self.page.wait(5)

    def _accept_cookies(self) -> None:
        try:
            self.page.ele(self.COOKIE_XPATH, timeout=5).click(by_js=True)
            print("Cookies accepted.")
            self.page.wait(1)
        except Exception:
            print("No cookie banner found, skipping.")

    def _fill_form(self) -> None:
        print("Entering PNR...")
        pnr_input = self.page.ele(self.PNR_XPATH, timeout=20)
        pnr_input.clear()
        pnr_input.input(self.pnr)

        print("Entering Last Name...")
        last_name_input = self.page.ele(self.LAST_NAME_XPATH, timeout=20)
        last_name_input.clear()
        last_name_input.input(self.last_name)

    def _submit_form(self) -> None:
        print("Clicking Submit...")
        self.page.ele(self.SUBMIT_XPATH, timeout=20).click(by_js=True)

    def _wait_for_response(self, timeout: int = 120) -> dict:
        print("Waiting for API response...")
        for packet in self.page.listen.steps(timeout=timeout):
            print(f"URL: {packet.url}")
            if "qantas.com" in packet.url and packet.response:
                body = packet.response.body
                if body:
                    return body
        raise TimeoutError(f"No Qantas API response received within {timeout}s.")

    def _close(self) -> None:
        if self.page:
            self.page.quit()
            self.page = None

    # ------------------------------------------------------------------ #
    #  Public interface                                                    #
    # ------------------------------------------------------------------ #

    def fetch(self) -> dict:
        """Open Qantas manage booking, submit credentials, return API response body."""
        try:
            self._init_page()
            self._open_site()
            self._accept_cookies()
            self._fill_form()
            self._submit_form()
            return self._wait_for_response()
        finally:
            self._close()

    # Context-manager support
    def __enter__(self):
        self._init_page()
        return self

    def __exit__(self, *_):
        self._close()


# ---------------------------------------------------------------------- #
#  Entry point                                                            #
# ---------------------------------------------------------------------- #

if __name__ == "__main__":
    PNR       = "9PF6LR"
    LAST_NAME = "REKHI"

    scraper = QantasBooking(PNR, LAST_NAME)
    data    = scraper.fetch()
    print(data)