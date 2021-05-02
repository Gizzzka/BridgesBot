import time
import random
import json
from typing import List, Any
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
    return time.strptime(raw, '%H:%M')


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

    return result


def configure_the_browser():
    # creating a webdriver object
    options = webdriver.FirefoxOptions()

    # setting a random user-agent
    user_agent_lst = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 '
                      'YaBrowser/17.3.1.840 Yowser/2.5 Safari/537.36',
                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/61.0.3163.100 Safari/537.36 '
                      'OPR/48.0.2685.52',
                      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.59.10 (KHTML, like Gecko) '
                      'Version/5.1.9 Safari/534.59.10',
                      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) '
                      'AppleWebKit/601.7.8 (KHTML, like Gecko) Version/9.1.3 '
                      'Safari/537.86.7',
                      'Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) '
                      'Gecko/20100101 Firefox/7.0.1']

    random_index = random.randint(0, len(user_agent_lst) - 1)
    random_user_agent = user_agent_lst[random_index]

    options.set_preference('general-useragent.override', random_user_agent)

    # setting a random proxy
    proxy_lst = ['194.67.78.220:80', '188.120.246.81:8118', '87.249.217.57:3128', '185.189.135.17:4045',
                 '78.153.159.205:4045']
    random_index = random.randint(0, len(proxy_lst) - 1)
    random_proxy = proxy_lst[random_index]

    firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
    firefox_capabilities['marionette'] = True
    firefox_capabilities['proxy'] = {'proxyType': 'MANUAL', 'httpProxy': random_proxy, 'ftpProxy': random_proxy,
                                     'sslProxy': random_proxy}

    # making the browser headless
    options.set_preference('dom.webdriver.enabled', False)
    options.headless = True

    # creating a webdriver object
    driver = webdriver.Firefox(executable_path=GECKO_PATH,
                               options=options, proxy=random_proxy)
    return driver


def get_schedule():
    # configuring the browser

    # driver = configure_the_browser()
    driver = webdriver.Firefox(executable_path=GECKO_PATH)

    # creating the final dict
    bridge_dict = {}

    try:
        # going to the website
        driver.get(URL)
        time.sleep(4)

        # going to the full schedule
        driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[3]').click()
        time.sleep(4)

        # finding tag <div> with all bridges tags
        bridges_divs = driver.find_elements_by_class_name('bridge')

        # iterating throw each bridge tag and filling the dict
        for bridge in bridges_divs:
            # getting bridge name
            bridge_name = bridge.find_element_by_class_name('name').text
            bridge_name = fix_title(bridge_name)

            # getting bridge time
            bridge_time: List[Any] = []

            for half_time_p in bridge.find_elements_by_tag_name('span'):
                bridge_time.append(half_time_p.text)

            # fixing the bridge time
            bridge_time = fix_schedule(bridge_time)

            # filling the dict
            bridge_dict[bridge_name] = bridge_time

    except Exception as ex:
        print(ex)

    finally:
        driver.close()
        driver.quit()

    return bridge_dict


# data = get_schedule()
# pprint(data)
