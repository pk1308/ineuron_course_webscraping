import time
import os 
import fake_useragent
import requests
import selenium_stealth 
from selenium import common
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager 

import SRC.constants as constants


"""
Class contains all the functions to scrape courses info from https://ineuron.ai/
"""


class CourseInfo(webdriver.Chrome):
    def __init__(self,driver_path=ChromeDriverManager().install(), teardown: bool = False):
        self.driver_path = driver_path
        self.teardown = teardown
        options = Options()
        user_agent = fake_useragent.UserAgent
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-gpu")
        
        # options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
                 
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'user-agent={user_agent}')
        super(CourseInfo, self).__init__(executable_path=self.driver_path, options=options)
        self.implicitly_wait(15)
        self.maximize_window()

    def __enter__(self):
        super(CourseInfo, self).__enter__()
        selenium_stealth.stealth(self,
                                 languages=["en-US", "en"],
                                 vendor="Google Inc.",
                                 platform="Win32",
                                 webgl_vendor="Intel Inc.",
                                 renderer="Intel Iris OpenGL Engine",
                                 fix_hairline=True, )
        return self

    @staticmethod
    def check_page_exist(url: str):

        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            print('[WARNING] link does not exist')
            return False

    def goto_page(self, url: str = constants.BASE_URL) -> bool:
        if self.check_page_exist(url=url):
            self.get(url)
            return True
        return False

    def scroll_down(self):
        scroll_pause_time_sec = 2  # to copy human behaviour
        # get scroll height
        last_height = self.execute_script("return document.body.scrollHeight")

        while True:
            # scroll down to bottom
            time.sleep(scroll_pause_time_sec)
            self.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # wait to load page
            time.sleep(scroll_pause_time_sec)

            # calculate new scroll height and compare with last scroll height
            new_height = self.execute_script("return document.body.scrollHeight")
            # print(new_height)
            
            if new_height == last_height:  # last_height: remove comment
                # if you want to get all the courses link from category page
                break
            last_height = new_height

    def fetch_courses_links_list_with_category(self) -> dict:
        # finding course tab and hover over it to get list of field
        # courses_elem = self.find_element(by=By.ID, value='course-dropdown')
        courses_elem = WebDriverWait(self, 30).until(
            EC.element_to_be_clickable((By.ID, 'course-dropdown')))
        time.sleep(2)

        hover = ActionChains(self).move_to_element(courses_elem)
        hover.perform()

        # find categories
        category_elem = WebDriverWait(self, 30).until(
            EC.presence_of_element_located((By.ID, 'category')))

        # get categories name and links
        categories_info = WebDriverWait(category_elem, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul a[href]')))
        categories_dict = {}
        for category in categories_info:
            categories_dict[category.text] = category.get_attribute('href')

        print(categories_dict)
        return categories_dict

    def get_courses_links_from_category_link(self, course_link: str) -> list:
        self.goto_page(url=course_link)

        # scroll down until end of the page
        self.scroll_down()

        # get list of courses links on the page
        course_links = WebDriverWait(self, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.Course_right-area__1XUfi a[href]')))
        links_list = []

        for links in course_links:
            links_list.append(links.get_attribute('href'))

        return links_list

    def get_course_name(self) -> str:
        course_name = self.find_element(by=By.CSS_SELECTOR, value='.Hero_course-title__1a-Hg').text
        print(course_name)
        return course_name

    def get_course_description(self) -> str:
        try:
            course_description = self.find_element(by=By.CSS_SELECTOR, value='.Hero_course-desc__26_LL').text
            print(course_description)
            return course_description
        except common.exceptions.StaleElementReferenceException:
            print('[WARNING] No course description found')
        return ''

    def get_course_price(self) -> str:
        try:
            course_price = self.find_element(by=By.CSS_SELECTOR, value='.CoursePrice_dis-price__3xw3G span').text
            print(course_price)
            return str(course_price)
        except common.exceptions.StaleElementReferenceException:
            print('[WARNING] No course price description found')
        return ''

    def get_course_features(self) -> list:
        features_list = []
        try:
            course_features = WebDriverWait(self, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                     'div.CoursePrice_course-features__2qcJp ul li')))

            for feature in course_features:
                features_list.append(feature.text)
            print(features_list)
            return features_list
        except common.exceptions.StaleElementReferenceException:
            print('[WARNING] No course features description found')

        return features_list

    def get_what_youll_learn(self) -> list:
        topics_list = []
        try:
            what_youll_learn = WebDriverWait(self, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                     'div.CourseLearning_card__WxYAo ul li')))

            for topics in what_youll_learn:
                topics_list.append(topics.text)
            print(topics_list)
            return topics_list
        except common.exceptions.StaleElementReferenceException:
            print("[WARNING] No What you'll learn description found")

        return topics_list

    def get_course_timings(self) -> list:
        class_list = []
        try:
            timings = WebDriverWait(self, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                     'div div.CoursePrice_time__1I6dT')))
            if timings:
                if len(timings) == 2:
                    class_list.append(f'class time: {timings[0].text}')
                    class_list.append(f'doubt session: {timings[1].text}')
                elif len(timings) == 1:
                    class_list.append(f'class time: {timings[0].text}')
            print(class_list)
            return class_list
        except common.exceptions.StaleElementReferenceException:
            print("[WARNING] No class timing found found")
        except Exception as e:
            print(e)

        return class_list

    def get_requirements(self) -> list:
        requirements_list = []
        try:
            requirements = WebDriverWait(self, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                     "div.CourseRequirement_card__3g7zR ul li")))

            for requirement in requirements:
                requirements_list.append(requirement.text)
            print(requirements_list)
            return requirements_list
        except common.exceptions.StaleElementReferenceException:
            print("[WARNING] No class timing found found")
        return requirements_list

    def get_click_view_more_button_curriculum(self) -> None:
        # find view more button and click in course curriculum
        try:
            # view_more_button = self.find_element(by=By.CSS_SELECTOR,
            #                                      value='span.CurriculumAndProjects_view-more-btn__3ggZL')
            view_more_button = WebDriverWait(self, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            'span.CurriculumAndProjects_view-more-btn__3ggZL')))
            view_more_button.click()
        except Exception as e:
            print(e)
            print('[INFO] no click view button found on course curriculum')

    def get_curriculum_data(self) -> list:
        retries = 3
        while retries != 0:
            course_curriculum = WebDriverWait(self, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                'div.CurriculumAndProjects_course-curriculum__Rlhvu')))

            if course_curriculum.find_elements(By.CSS_SELECTOR, 'h4')[0].text != 'Course Curriculum':
                print('[ERROR] course curriculum not found')
                return []
            time.sleep(3)

            course_curriculum_chapters = WebDriverWait(course_curriculum, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div div')))
            time.sleep(3)

            try:
                ignored_exceptions = (
                    common.exceptions.NoSuchElementException, common.exceptions.StaleElementReferenceException)
                headings = WebDriverWait(course_curriculum_chapters, 30, ignored_exceptions).until(
                    EC.presence_of_all_elements_located((By.XPATH, './/div/div/span')))
                time.sleep(3)

                # removing 'preview' from headings
                clean_heading = [heading.text for heading in headings if heading.text != 'Preview']
                print(f'clean curriculum headings {clean_heading}')

                plus_buttons = course_curriculum_chapters.find_elements(by=By.CSS_SELECTOR, value='.fas.fa-plus')
                break

            except common.exceptions.StaleElementReferenceException:
                print(f'[WARNING] curriculum headings could not found, retrying...[{retries}/3]')
                self.refresh()
                retries -= 1

        if retries == 0:
            print(f'[ERROR] could not find curriculum headings')
            print("[WARNING] No course curriculum found found")
            return []

        course_curriculum_list = []
        for cnt, heading in enumerate(clean_heading, start=1):
            print(cnt)

            try:
                plus_buttons[cnt].click()
                print('[INFO] plus button clicked')
            except Exception as e:
                print(e)
                print('[INFO] NO plus button found')

            sub_chapter_list = []

            sub_chapters = course_curriculum_chapters.find_elements(
                by=By.XPATH,
                value=f'.//div[{cnt}]/div/ul/li')

            self.implicitly_wait(3)
            time.sleep(3)

            for sub_chapter in sub_chapters:
                sub_chapter_str = sub_chapter.text

                sub_chapter_list.append(sub_chapter_str.replace('\nPreview', ''))
            join_chapter_list = "\n".join(sub_chapter_list)
            course_curriculum_list.append(f'{heading.upper()} \n {join_chapter_list}')
            print(course_curriculum_list)

        return course_curriculum_list

    def get_mentor_name(self) -> list:
        mentor_names_list = []
        try:
            mentor_names = self.find_elements(by=By.CSS_SELECTOR,
                                              value="div.InstructorDetails_mentor__2hmG8.InstructorDetails_card__14MoH.InstructorDetails_flex__2ePsQ.card.flex div h5")
            for mentor_name in mentor_names:
                mentor_names_list.append(mentor_name.text)
            print(mentor_names_list)
            return mentor_names_list
        except common.exceptions.StaleElementReferenceException:
            print("[WARNING] No mentors found found")
        return mentor_names_list

    def get_all_info_from_page(self) ->dict:
        course_info_dict = {}
        course_info_dict['course_name'] = self.get_course_name()
        course_info_dict['description'] = self.get_course_description()
        course_info_dict['price']= self.get_course_price()
        course_info_dict['course_features'] = self.get_course_features()
        course_info_dict['what_youll_learn'] = self.get_what_youll_learn()
        course_info_dict['timings'] = self.get_course_timings()
        course_info_dict['requirements'] = self.get_requirements()
        self.get_click_view_more_button_curriculum()
        course_info_dict['course_curriculum']= self.get_curriculum_data()
        course_info_dict['mentor_name'] = self.get_mentor_name()
       

        return course_info_dict

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            super(CourseInfo, self).__exit__()
            self.quit()
