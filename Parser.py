import Envs
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from timeit import timeit


class Parser:
    def __init__(self):
        self.bridge_dict = {}
        fo = webdriver.FirefoxOptions()

        fo.add_argument('--headless')  # enable silent mode

        fp = webdriver.FirefoxProfile()  # disable images load
        fp.set_preference(envs_demo.FF_PREF_IMG, 2)
        fp.set_preference(envs_demo.FF_PREF_FLASH, 'false')
        fp.update_preferences()

        self.driver = webdriver.Firefox(executable_path=envs_demo.FF_GECKO_PATH,
                                        firefox_profile=fp,
                                        options=fo)
        self.url = envs_demo.URL

    @staticmethod
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

    @staticmethod
    def fix_time(raw):
        try:
            return datetime.strptime(raw, envs_demo.TIME_TEMPLATE).time()
        except Exception as ex:
            return datetime.strptime(raw, envs_demo.ALT_TIME_TEMPLATE).time()

    @staticmethod
    def fix_schedule(wrong_schedule):
        result = {}

        # fixing schedules with small time intervals
        if len(wrong_schedule) > 2:
            # adding bridge opening time
            result[Parser.fix_time(wrong_schedule[-2])] = Parser.fix_time(wrong_schedule[0])

            # adding small time intervals
            if len(wrong_schedule) > 4:
                result[Parser.fix_time(wrong_schedule[2])] = Parser.fix_time(wrong_schedule[3])

            # adding bridge closing time
            result[Parser.fix_time(wrong_schedule[-3])] = Parser.fix_time(wrong_schedule[-1])

        elif len(wrong_schedule) == 2:
            result[Parser.fix_time(wrong_schedule[0])] = Parser.fix_time(wrong_schedule[1])

        # if argument is too short
        else:
            result = {}

        return result

    def get_schedule(self):
        try:
            self.driver.get(self.url)
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, envs_demo.SEL_DETAILS))).click()
            # finding tag <div> with all bridges tags
            bridges_divs = self.driver.find_elements_by_class_name('bridge')
            # iterating throw each bridge tag and filling the dict
            for bridge in bridges_divs:
                bridge_name = bridge.find_element_by_class_name('name').text
                bridge_name = Parser.fix_title(bridge_name)
                bridge_time = []
                for half_time_p in bridge.find_elements_by_tag_name('span'):
                    bridge_time.append(half_time_p.text)
                bridge_time = Parser.fix_schedule(bridge_time)  # fixing the bridge time
                self.bridge_dict[bridge_name] = bridge_time  # filling the dict

        except Exception as ex:
            print(ex)

        finally:
            self.driver.close()
            self.driver.quit()


def main():
    test = Parser()
    test.get_schedule()


if __name__ == '__main__':
    print(timeit(main, number=1))

