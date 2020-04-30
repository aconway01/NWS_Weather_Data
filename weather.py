from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from parsel import Selector
import smtplib
import pymongo
from time import sleep
import datetime

def main():

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("user-agent=aconway")
    driverPath = ''
    driver = webdriver.Chrome(driverPath, options=options)

    cities = open("USCities.txt", "r")

    empty = []
    failed = []

    mongodbURI = ""
    client = pymongo.MongoClient(mongodbURI)

    db = client['weather']

    for place in cities:
        try:
            date = datetime.datetime.now()
            today = str(date.year)+"-"+str(date.month)+"-"+str(date.day)
            time = str(date.hour)+":"+str(date.minute)

            weather = "https://www.weather.gov/"
            driver.get(weather)

            sleep(5)

            try:
                close = driver.find_element_by_xpath(
                    '//*[@id="acsFocusFirst"]')
                close.click()
                sleep(0.5)
            except:
                a = 1

            city = driver.find_element_by_xpath(
                '//*[@id="inputstring"]')

            for i in range(18):
                city.send_keys(Keys.BACK_SPACE)

            city.send_keys(place)

            sleep(0.5)

            search = driver.find_element_by_xpath('//*[@id="btnSearch"]')

            search.click()
            for i in range(4):
                try:
                    sleep(0.5)
                    search.click()
                except:
                    a = 1

            try:
                wait = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="seven-day-forecast-list"]//p[starts-with(@class,"temp temp-high")]')))
            except TimeoutException:
                print("Loading took too much time!")

            sel = Selector(text=driver.page_source)

            try:
                temp = str(sel.xpath(
                    '//*[@id="current_conditions-summary"]/p[2]/text()').get())
                temp = int(temp[:-2])
            except:
                temp = ""

            try:
                high = str(sel.xpath(
                    '//*[@id="seven-day-forecast-list"]//p[starts-with(@class,"temp temp-high")]/text()').getall()[0][6:])
                high = int(high[:-3])
            except:
                high = ""

            try:
                low = str(sel.xpath(
                    '//*[@id="seven-day-forecast-list"]//p[starts-with(@class,"temp temp-low")]/text()').getall()[0][5:])
                low = int(low[:-3])
            except:
                low = ""

            try:
                humidity = str(sel.xpath(
                    '//*[@id="current_conditions_detail"]/table/tbody/tr[1]/td[2]/text()').get())
                humidity = int(humidity[:-1])
            except:
                humidity = ""

            try:
                barometer = str(sel.xpath(
                    '//*[@id="current_conditions_detail"]/table/tbody/tr[3]/td[2]/text()').get())
                barometer = float(barometer[0:barometer.find(" in")])
            except:
                barometer = ""

            try:
                dewpoint = str(sel.xpath(
                    '//*[@id="current_conditions_detail"]/table/tbody/tr[4]/td[2]/text()').get())
                dewpoint = int(dewpoint[0:dewpoint.find("F")-1])
            except:
                dewpoint = ""

            docName = place.replace(" ", "").replace(",", "").lower().strip()

            col = db[docName]

            my_dict = {}

            cityState = place.strip()

            my_dict = {"city": cityState, "date": today, "time": time, "tempF": temp, "highF": high, "lowF": low,
                       "humidityPercent": humidity, "barometerIn": barometer, "dewpointF": dewpoint}

            col.replace_one({'date': today}, my_dict, True)

            print(cityState)
            print(docName)
            print("Date:", today)
            print("time:", time)
            print("tempF:", temp)
            print("highF:", high)
            print("lowF:", low)
            print("humidity_percent:", humidity)
            print("barometer_in:", barometer)
            print("dewpointF:", dewpoint)
            print()

            errs = ["N/A", "", "No", "Non"]

            if ((temp in errs) or (high in errs) or (low in errs) or (humidity in errs) or (barometer in errs) or (dewpoint in errs)):
                empty.append(place)

        except:
            failed.append(place)

    if (len(empty) > 0 or len(failed) > 0):
        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        s.starttls()

        # Authentication
        emailUser = ""
        emailPass = ""
        s.login(emailUser, emailPass)

        # message to be sent
        message = "Failed:/n"+failed+"/n"+"Empty:/n"+empty

        # sending the mail
        emailTo = ""
        s.sendmail(emailUser,emailTo, message)

        # terminating the session
        s.quit()

    driver.quit()


main()
