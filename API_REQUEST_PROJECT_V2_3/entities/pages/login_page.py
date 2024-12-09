import pyotp

from entities.pages.page import Page
from entities.pages.page_tools.login_page_tools import LoginPageTools
from selenium.common.exceptions import WebDriverException


class LoginPage(Page):
    def __init__(self) -> None:
        super().__init__()

    def otp_code_generator(self):
        ISSUER = "mercadolibre"
        EMAIL = "wellington@movesmart.com.br"
        SECRET = "KVGHUYS3MZ5HMWCDKZYVARZUKEUUKKLG"

        totp = pyotp.TOTP(SECRET)

        otp_code = totp.now()

        return otp_code

    def login(self, username: str, password: str, driver: dict = None) -> None | bool:

        if driver:

            login_page_tools = LoginPageTools(driver=driver)

            try:
                # Clicar no botão "Sou agência"
                login_page_tools.buttom_i_am_agency()

                # Inserir o username
                login_page_tools.set_username(username=username)
                # Inserir a password
                login_page_tools.set_password(password=password)

                # Inserir o código de validação
                login_page_tools.set_validation_code(self.otp_code_generator())
            except WebDriverException as e:
                desired_url = "https://envios.adminml.com/logistics/monitoring-distribution"
                current_url = driver.current_url

                if desired_url != current_url:
                    return False
            return True
