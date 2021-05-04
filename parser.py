import time
from datetime import datetime
import random
import json
from selenium import webdriver
from pprint import pprint


URL = 'https://mostotrest-spb.ru/'
GECKO_PATH = '/Users/abarnett/Documents/geckodriver'
# GECKO_PATH = 'C:/Users/iljus/Desktop/Actual code/Trying selenium/geckodriver.exe'


def fix_title(title):
    # fixing two-words titles
    if len(title.split(' ')) >= 2:
        # defining final variable
        fixed_title = ''

        # making all letters after the first lowercase
        for word in title.split(' '):
            fixed_title += word[0]
            fixed_title += word[1:].lower()
            fixed_title += ' '

        # get rid of the last space
        fixed_title = 'Мост ' + fixed_title[:-1]

    # fixing one-word titles
    else:
        fixed_title = title[0]
        fixed_title += title[1:].lower()

        fixed_title = fixed_title + ' мост'

    return fixed_title


def fix_time(raw):
    return datetime.strptime(raw, '%H:%M').time()


def fix_schedule(wrong_schedule):
    result = {}

    # fixing schedules with small time intervals
    if len(wrong_schedule) > 2:
        # adding bridge opening time
        result[fix_time(wrong_schedule[-2])] = fix_time(wrong_schedule[0])

        # adding small time intervals
        if len(wrong_schedule) > 4:
            result[fix_time(wrong_schedule[2])] = fix_time(wrong_schedule[3])

        # adding bridge closing time
        result[fix_time(wrong_schedule[-3])] = fix_time(wrong_schedule[-1])

    elif len(wrong_schedule) == 2:
        result[fix_time(wrong_schedule[0])] = fix_time(wrong_schedule[1])

    # if argument is too short
    else:
        result = {}

    return [result]


def configure_the_browser():
    fo = webdriver.FirefoxOptions()

    fo.add_argument('--headless')  # enable silent mode

    fp = webdriver.FirefoxProfile()  # disable images load
    fp.set_preference('permissions.default.image', 2)
    fp.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    fp.update_preferences()

    driver = webdriver.Firefox(executable_path=GECKO_PATH,
                               firefox_profile=fp,
                               options=fo)
    return driver


def get_schedule():
    driver = configure_the_browser()
    bridge_dict = {}
    try:
        driver.get(URL)
        time.sleep(2)
        driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[1]/div[3]'
        ).click()  # selecting full schedule
        time.sleep(2)
        # finding tag <div> with all bridges tags
        bridges_divs = driver.find_elements_by_class_name('bridge')
        # iterating throw each bridge tag and filling the dict
        for bridge in bridges_divs:
            bridge_name = bridge.find_element_by_class_name('name').text
            bridge_name = fix_title(bridge_name)
            bridge_time = []
            for half_time_p in bridge.find_elements_by_tag_name('span'):
                bridge_time.append(half_time_p.text)
            bridge_time = fix_schedule(bridge_time)  # fixing the bridge time
            bridge_dict[bridge_name] = bridge_time  # filling the dict
    except Exception as ex:
        print(ex)
    driver.close()
    driver.quit()
    return bridge_dict


data = get_schedule()
pprint(data)
