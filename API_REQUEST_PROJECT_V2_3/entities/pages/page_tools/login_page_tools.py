from entities.pages.page_tools.page_tools import PageTools


class LoginPageTools(PageTools):
    def __init__(self, driver):
        super().__init__(driver)

    def buttom_i_am_agency(self):
        self.click_element_by_xpath('//a[@id="blue-choice"]')

    def set_username(self, username: str):
        # Username
        web_element = self.write_xpath('//input[@name="username"]', username)

    def set_password(self, password: str):
        # Password
        web_element = self.write_xpath('//input[@name="password"]', password)
        web_element.submit()

    def set_validation_code(self, validation_code):
        web_element = self.write_xpath(
            '//input[@name="code"]', validation_code)
        remember_checkbox = self.click_element_by_xpath(
            '//input[@class="auth0-mfa-checkbox"]')
        web_element.submit()
