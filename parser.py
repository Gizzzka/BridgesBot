# -*- coding: utf-8 -*-
from selenium import webdriver
from datetime import datetime
import time
import envs


def fix_title(title):
    if len(title.split(' ')) >= 2:
        fixed_title = ''
        for word in title.split(' '):
            fixed_title += word[0]
            fixed_title += word[1:].lower()
            fixed_title += ' '
        fixed_title = 'Мост ' + fixed_title[:-1]
    else:
        fixed_title = title[0]
        fixed_title += title[1:].lower()
        fixed_title = fixed_title + ' мост'
    return fixed_title


def fix_time(raw):
    return datetime.strptime(raw, envs.TIME_TEMPLATE).time()


def fix_schedule(wirings):
    result = {}
    if len(wirings) > 2:
        result[fix_time(wirings[-2])] = fix_time(wirings[0])
        if len(wirings) > 4:
            result[fix_time(wirings[2])] = fix_time(wirings[3])
        result[fix_time(wirings[-3])] = fix_time(wirings[-1])
    elif len(wirings) == 2:
        result[fix_time(wirings[0])] = fix_time(wirings[1])
    return [result]


def configure_the_browser():
    fo = webdriver.FirefoxOptions()
    fo.add_argument('--headless')

    fp = webdriver.FirefoxProfile()
    fp.set_preference(envs.FF_PREF_IMG, 2)
    fp.set_preference(envs.FF_PREF_FLASH, 'false')
    fp.update_preferences()

    driver = webdriver.Firefox(executable_path=envs.FF_GECKO_PATH,
                               firefox_profile=fp, options=fo)
    return driver


def get_schedule():
    driver = configure_the_browser()
    bridge_dict = {}
    try:
        driver.get(envs.URL)
        time.sleep(2)
        driver.find_element_by_xpath(envs.SEL_DETAILS).click()
        time.sleep(2)
        for bridge in driver.find_elements_by_class_name('bridge'):
            bridge_name = bridge.find_element_by_class_name('name').text
            bridge_name = fix_title(bridge_name)
            bridge_time = []
            for half_time_p in bridge.find_elements_by_tag_name('span'):
                bridge_time.append(half_time_p.text)
            bridge_dict[bridge_name] = fix_schedule(bridge_time)
    except Exception as e:
        print(e)
    driver.close()
    driver.quit()
    return bridge_dict


# data = get_schedule()
# print(data)
