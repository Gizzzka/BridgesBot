import envs_demo
from time import sleep
from selenium import webdriver
from datetime import datetime


class BridgesDict:
    def __init__(self):
        self.bridge_dict = {}
        fo = webdriver.FirefoxOptions()

        fo.add_argument('--headless')  # enable silent mode

        fp = webdriver.FirefoxProfile()  # disable images load
        fp.set_preference('permissions.default.image', 2)
        fp.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
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
            result[BridgesDict.fix_time(wrong_schedule[-2])] = BridgesDict.fix_time(wrong_schedule[0])

            # adding small time intervals
            if len(wrong_schedule) > 4:
                result[BridgesDict.fix_time(wrong_schedule[2])] = BridgesDict.fix_time(wrong_schedule[3])

            # adding bridge closing time
            result[BridgesDict.fix_time(wrong_schedule[-3])] = BridgesDict.fix_time(wrong_schedule[-1])

        elif len(wrong_schedule) == 2:
            result[BridgesDict.fix_time(wrong_schedule[0])] = BridgesDict.fix_time(wrong_schedule[1])

        # if argument is too short
        else:
            result = {}

        return [result]

    def get_schedule(self):
        bridge_dict = {}
        try:
            self.driver.get(self.url)
            sleep(2)
            self.driver.find_element_by_xpath(envs_demo.SEL_DETAILS).click()  # selecting full schedule
            sleep(2)
            # finding tag <div> with all bridges tags
            bridges_divs = self.driver.find_elements_by_class_name('bridge')
            # iterating throw each bridge tag and filling the dict
            for bridge in bridges_divs:
                bridge_name = bridge.find_element_by_class_name('name').text
                bridge_name = BridgesDict.fix_title(bridge_name)
                bridge_time = []
                for half_time_p in bridge.find_elements_by_tag_name('span'):
                    bridge_time.append(half_time_p.text)
                bridge_time = BridgesDict.fix_schedule(bridge_time)  # fixing the bridge time
                bridge_dict[bridge_name] = bridge_time  # filling the dict
        except Exception as ex:
            print(ex)

        self.driver.close()
        self.driver.quit()
        self.bridge_dict = bridge_dict

        return bridge_dict
