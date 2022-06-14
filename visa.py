from datetime import datetime

from utils import config
from utils.basic import Basic
from utils.log import logger
from time import sleep


class Visa(Basic):

    def __init__(self, driver):
        super().__init__(driver)

    def open_page(self, page):
        self.driver.get(page)

    def select_centre(self, county, city, category):
        self.wait_for_secs()
        self.click_el(name="JurisdictionId")
        self.click_el(xpath="//select[@name='JurisdictionId']/option[contains(text(),'{}')]".format(county))
        self.wait_for_loading()
        self.click_el(name="centerId")
        self.click_el(xpath="//select[@name='centerId']/option[contains(text(),'{}')]".format(city))
        self.wait_for_secs()
        self.click_el(name="category")
        self.click_el(xpath="//select[@name='category']/option[contains(text(),'{}')]".format(category))
        self.wait_for_secs()
        self.click_el(name='checkDate')
        logger.info("select centre finished")

    def go_to_appointment_page(self, phone='', email=''):
        self.open_page(config.OPENED_PAGE)
        # self.select_centre("England", "Manchester", "Normal")
        # self.enter_phone_and_email(phone, email)
        # self.enter_wrong_code(email, config.PASSWORD)
        # self.enter_code_from_email(email)

    def login(self):
        try:
            # self.click_el(xpath="//a[text() = 'Log in']")
            element = self.driver.find_element_by_xpath("//a[contains(text(),'Log in')]")
            element.click()
            self.wait_for_secs()
            self.enter_message(config.EMAIL, name='email')
            self.wait_for_secs()
            self.enter_message(config.PASSWORD, name='password')
            self.wait_for_secs()
            self.click_el(name="login")
            logger.info("log in finished")
        except Exception as e:
            logger.error(e)

    def go_to_book_appointment(self):
        unique_suffix = config.OPENED_PAGE.split('/')[-1]
        link = f'book-appointment/{unique_suffix}'
        element = self.driver.find_element_by_xpath("//a[contains(text(),'Book Appointment')]")
        element.click()
        logger.info(f"date appointment link = [{link}]")
        # open a new tab
        # self.driver.execute_script(f'window.open(\"{link}\","_blank");')
        # # switch to the new tab
        # self.driver.switch_to.window(self.driver.window_handles[-1])
        logger.info("go to book appointment finished")

    def check_available_dates(self):
        self.click_el(id="VisaTypeId")
        self.click_el(xpath="//select[@id='VisaTypeId']/option[contains(text(),'{}')]".format(config.CENTER[3]))
        self.wait_for_secs(1)

        # 勾选模式
        sms = self.driver.find_element_by_id("vasId12")
        if not sms.is_selected() and config.MODE[0] == 'Yes':
            sms.click()
            sleep(0.5)
        photo = self.driver.find_element_by_id("vasId5")
        if not photo.is_selected() and config.MODE[1] == 'Yes':
            photo.click()
            sleep(0.5)
        premium = self.driver.find_element_by_id("vasId1")
        if not premium.is_selected() and config.MODE[2] == 'Yes':
            premium.click()
            sleep(0.5)
        courier = self.driver.find_element_by_id("courierId")
        if not courier.is_selected() and config.MODE[3] == 'Yes':
            courier.click()
            sleep(0.5)

        # check date
        self.click_el(id="app_date")
        available_dates = {}
        next_button_xpath = "//div[@class = 'datepicker-days']//th[@class = 'next' and @style = 'visibility: visible;']"  # next month
        while True:
            nd = self.get_normal_dates()
            if nd:
                available_dates.update(nd)
            if self.driver.find_elements_by_xpath(next_button_xpath):
                self.wait_for_secs(0)
                self.click_el(xpath=next_button_xpath)
            else:
                break
        return available_dates

    def get_normal_dates(self):
        normal_dates_xpath = "//div[@class='datepicker-days']//td[not(contains(@class, 'disabled'))]"
        # days in the current month
        result_dates = {}
        dates = []

        if len(self.driver.find_elements_by_xpath(normal_dates_xpath)):
            found_month = self.driver.find_element_by_xpath(
                "//div[@class='datepicker-days']//th[@class='datepicker-switch']").text
            for day in self.driver.find_elements_by_xpath(normal_dates_xpath):  # need refactor fix
                dates.append(day.text)
            for day in dates:
                found_date = datetime.strptime(day + " " + found_month, '%d %B %Y')
                result_dates[found_date.strftime("%d/%m/%Y")] = []
            self.click_el(normal_dates_xpath)  # 自动点击

            # 选择日期，最晚的那个
            select_el = self.driver.find_element_by_id("app_time")
            select_el.click()
            options = select_el.find_element_by_tag_name('option')
            options[len(options) - 1].click()
            logger.info("Time selected !")

            # 点击确认
            self.driver.find_element_by_name("bookDate").click()
            logger.info("Finished !")

        return result_dates
