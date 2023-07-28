import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
import time
from numpy import random


CHROMEDRIVER_PATH = "/executables/chromedriver.exe"
STACKOVERFLOW_LOGIN_URL = "https://stackoverflow.com/users/login"


def sleeprandom(minimum=0.5, maximum=1):
    st = random.rand() * (maximum - minimum) + minimum
    while st > 0:
        time.sleep(0.1)
        st -= 0.1


class Webdriver_Handler:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        options.add_experimental_option('useAutomationExtension', False)

        self.timeout = 10       

        service = Service(executable_path=CHROMEDRIVER_PATH)
        self.wd = webdriver.Chrome(service=service, options=options)
        
        self.wd.implicitly_wait(self.timeout)

        stealth(
            self.wd,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
    
    def login(self, username, password):
        self.wd.get(STACKOVERFLOW_LOGIN_URL)
        sleeprandom()
        self.try_disabling_cookies()
        sleeprandom()
        self.wd.find_element(By.ID, "email").send_keys(username)
        sleeprandom()
        self.wd.find_element(By.ID, "password").send_keys(password)
        sleeprandom()
        self.wd.find_element(By.ID, "submit-button").click()
        sleeprandom()
    
    def try_disabling_cookies(self):
        try:
            self.wd.find_elements(By.XPATH, """//button[contains(text(), "Necessary cookies only")]""")[0].click()
            return True
        except:
            return False
    
    def is_logged_in(self):
        try: 
            username = self.wd.find_element(By.XPATH, """//a[@class="s-topbar--item s-user-card s-user-card__small m0 px12 js-gps-track"]/span""").text
            reputation = self.wd.find_element(By.XPATH,"""//li[contains(@title, "reputation")]""").text.split("\n")[0].replace(" ","")
            print(f"Logged in as {username} with {reputation} reputation")
            return True
        except:
            print("Not logged in")
            return False
    
    def upvote_questions(self, num_upvotes=3):
        self.wd.get("https://stackoverflow.com/questions/tagged/python")
        question_links = [a.get_attribute("href") for a in self.wd.find_elements(By.XPATH, """//div[@id="questions"]/div/div/h3/a""")]
        print(question_links)
        sleeprandom()

        upvotes_given = 0
        for question_link in question_links:
            self.wd.get(question_link)
            sleeprandom()
            vote_count = int(self.wd.find_element(By.XPATH, """//div[@id="question"]/div/div/div/div[contains(@class,"vote-count")]""").text.replace(" ",""))
            if vote_count < 0:
                print("Skipping question with negative votes")
                continue

            upvote_button = self.wd.find_element(By.XPATH, """//div[@id="question"]/div/div/div/button[contains(@class,"vote-up")]""")

            if upvote_button.get_attribute("aria-pressed") == "false":
                upvote_button.click()
                upvotes_given += 1
                print(f"Upvoted {question_link}")
                sleeprandom()
            else:
                print("Already upvoted")
            
            if upvotes_given >= num_upvotes:
                break
        
        print(f"Upvoted {upvotes_given} questions")
    
    def answer_questions(self, num_answers=3, answer_question_if_open=True, tagged="python"):
        if answer_question_if_open and "stackoverflow.com/questions/" in self.wd.current_url and f"tagged/" not in self.wd.current_url:
            print("Question already opened. Answering...")
            self.answer_question()
            return True
        self.wd.get(f"https://stackoverflow.com/questions/tagged/{tagged}?sort=Newest&filters=NoAnswers")
        question_links = [a.get_attribute("href") for a in self.wd.find_elements(By.XPATH, """//div[@id="questions"]/div/div/h3/a""")]
        print(question_links)
        sleeprandom()

        answers_given = 0
        for question_link in question_links:
            self.wd.get(question_link)
            sleeprandom()
            if self.answer_question():
                answers_given += 1
    
    def answer_question(self):
        t1 = time.time()
        num_answers_on_question = int(self.wd.find_element(By.XPATH, """//h2[@class="mb0"]""").get_attribute("data-answercount"))
        if num_answers_on_question > 0:
            print("Already answered")
            return False
        vote_count = int(self.wd.find_element(By.XPATH, """//div[@id="question"]/div/div/div/div[contains(@class,"vote-count")]""").text.replace(" ",""))
        if vote_count < 0:
            print("Skipping question with negative votes")
            return False
        sleeprandom()
        question_title = self.wd.find_element(By.XPATH, """//a[@class="question-hyperlink"]""").text
        question_body = self.wd.find_element(By.XPATH, """//div[@id="question"]/div/div[2]/div[1]""").text

        answer = ask_for_stackoverflow_answer(question_title, question_body)
        print(answer)

        answer_area = self.wd.find_element(By.XPATH, """//textarea[@id="wmd-input"]""")
        sleeprandom()
        for c in answer:
            answer_area.send_keys(c)
        sleeprandom()

        answer_button = self.wd.find_element(By.XPATH, """//button[@id="submit-button"]""")
        sleeprandom(10,10)
        answer_button.click()

        print("Time taken to answer:", time.time() - t1)
        answer_is_posted = len(self.wd.find_elements(By.XPATH, """//div[@id="answers"]//span[text()="Quantum"]""")) > 0
        if not answer_is_posted:
            print("Answer not posted")
            if input("Your answer is not posted, type anything to interrupt. Press enter to continue") == "":
                return False
            else:
                raise Exception("Answer not posted.")
        return True
    
    def edit_questions(self, num_answers=3, edit_question_if_open=True, tagged="python"):
        if edit_question_if_open and "stackoverflow.com/questions/" in self.wd.current_url and f"tagged/" not in self.wd.current_url:
            print("Question already opened. Editing...")
            self.edit_question()
            return True
        self.wd.get(f"https://stackoverflow.com/questions/tagged/{tagged}?sort=Newest&filters=NoAnswers")
        question_links = [a.get_attribute("href") for a in self.wd.find_elements(By.XPATH, """//div[@id="questions"]/div/div/h3/a""")]
        print(question_links)
        sleeprandom()

        edits_made = 0
        for question_link in question_links:
            self.wd.get(question_link)
            sleeprandom()
            if self.edit_question():
                edits_made += 1
    
    def edit_question(self):
        t1 = time.time()
        edits_on_this_question = len(self.wd.find_elements(By.XPATH, """//div[@id="question"]//a[@title="show all edits to this post"]""")) > 0
        if edits_on_this_question:
            print("Already edited")
            return False
        vote_count = int(self.wd.find_element(By.XPATH, """//div[@id="question"]/div/div/div/div[contains(@class,"vote-count")]""").text.replace(" ",""))
        if vote_count < 0:
            print("Skipping question with negative votes")
            return False
        sleeprandom()
        question_title = self.wd.find_element(By.XPATH, """//a[@class="question-hyperlink"]""").text
        question_body = self.wd.find_element(By.XPATH, """//div[@id="question"]/div/div[2]/div[1]""").text

        # click edit button
        self.wd.find_element(By.XPATH, """//div[@id="question"]//*[@title="Revise and improve this post"]""").click()
        sleeprandom()

        (edited_title, edited_body) = ask_for_stackoverflow_edit(question_title, question_body)

        title_area = self.wd.find_element(By.XPATH, """//div[contains(@id, "post-editor")]//input[@id="title"]""")
        title_area.clear()
        sleeprandom()
        for c in edited_title:
            title_area.send_keys(c)
        sleeprandom()

        body_area = self.wd.find_element(By.XPATH, """//div[contains(@id, "post-editor")]//textarea[contains(@id,"wmd-input")]""")
        body_area.clear()
        sleeprandom()
        for c in edited_body:
            body_area.send_keys(c)
        sleeprandom()

        edit_comment_area = self.wd.find_element(By.XPATH, """//input[@id="edit-comment"]""")
        for c in "Improved conciseness and formatting":
            edit_comment_area.send_keys(c)
        sleeprandom()

        submit_button = self.wd.find_element(By.XPATH, """//button[@id="submit-button"]""")
        sleeprandom(10,10)
        submit_button.click()

        print("Time taken to edit:", time.time() - t1)
        answer_is_edited = len(self.wd.find_elements(By.XPATH, """//a[contains(@href,"suggested-edits")]""")) > 0
        if not answer_is_edited:
            print("Edit not posted")
            if input("Your edit is not posted, type anything to interrupt. Press enter to continue") == "":
                return False
            else:
                raise Exception("Edit not posted.")
        return True


wh = Webdriver_Handler()
wh.login("l-b-n.02@gmx.de","HomoDeus55Ch=?")
wh.upvote_questions(50)
