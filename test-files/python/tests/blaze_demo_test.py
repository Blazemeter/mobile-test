
import unittest
import os
from appium import webdriver
from time import sleep
from selenium.webdriver.support.ui import Select


class BlazeDemoTests(unittest.TestCase):
  SLEEP_TIME = 240

  def setUp(self):
    # set up appium
    # app = os.path.abspath(
    #     '../mobile apps/BlazeDemo/Build/Products/Debug-iphonesimulator/BlazeDemo.app')

    self.driver = webdriver.Remote(
        command_executor='http://127.0.0.1:4723/wd/hub',
        desired_capabilities={
            'bundleId': 'CA.BlazeDemo',
        })

  def tearDown(self):
    self.driver.quit()

  def test_a_purchase_flow(self):
    self.go_to_home_page(source='Philadelphia', to='New York')
    self.confirm_selection('Philadelphia', 'New York')
    self.purchase_flight()
    self.confirm_purchase()

  def go_to_home_page(self, source='Philadelphia', to='New York'):
    self.driver.implicitly_wait(BlazeDemoTests.SLEEP_TIME)
    # Go to home page & assert title
    contexts = self.driver.contexts

    for context_name in contexts:
      print("Context:", context_name)

    # Ideally there should be 1
    webViews = [i for i in contexts if 'WEBVIEW' in i]
    self.driver.switch_to.context(webViews[0])

    el = self.driver.find_element_by_tag_name('h1')
    self.assertEqual("Welcome to the Simple Travel Agency!", el.text)
    # Assert the drop down has values

    self._select_value('fromPort', source, zoom=True)
    self._select_value('toPort', to)

    submit_button = self.driver.find_element_by_tag_name('input')
    self.save_screenshot('home_page')
    submit_button.click()

  def confirm_selection(self, origination, destination):
    self.driver.implicitly_wait(BlazeDemoTests.SLEEP_TIME)
    el = self.driver.find_element_by_tag_name('h3')
    self.assertEqual("Flights from {0} to {1}:".format(
        origination, destination), el.text)

    choices = self.driver.find_elements_by_xpath('//tbody//tr')
    self.assertEqual(5, len(choices))

    self.save_screenshot('confirm_selection')
    form = self.driver.find_elements_by_xpath('//tbody//tr//form')[1]
    form.submit()

  def purchase_flight(self):
    self.driver.implicitly_wait(BlazeDemoTests.SLEEP_TIME)
    el = self.driver.find_element_by_tag_name('h2')
    self.assertTrue("has been reserved" in el.text)

    self.save_screenshot('purchase_flight')
    submit_button = self.driver.find_element_by_xpath(
        "//input[@value='Purchase Flight']")
    submit_button.click()

    self.confirm_purchase()

  def confirm_purchase(self):
    self.driver.implicitly_wait(BlazeDemoTests.SLEEP_TIME)
    el = self.driver.find_element_by_tag_name('h1')
    self.save_screenshot('thanks')
    self.assertEqual("Thank you for your purchase today!", el.text)

  def _select_value(self, element_name, value, zoom=False):
    el = self.driver.find_element_by_name(element_name)
    self.assertIsNotNone(el)
    # if zoom:
    #   import pdb
    #   pdb.set_trace()
    #   self.driver.zoom(el)

    dropdown = Select(el)
    dropdown.select_by_value(value)

  def save_screenshot(self, name):
    screenshot_folder = os.getenv('SCREENSHOT_PATH', '.')
    self.driver.save_screenshot(screenshot_folder + "/" + name + ".png")
