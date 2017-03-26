from selenium import webdriver
import random
import time

browser = webdriver.Chrome()
browser.get('http://students.mimuw.edu.pl/~lr371594/wybory/')

for i in range(3):
    row = random.choice(browser.find_element_by_class_name('big-table').find_elements_by_tag_name('tr')[1:])
    print(row.find_elements_by_tag_name('td')[0].text)
    time.sleep(2)
    row.find_element_by_tag_name('td').find_element_by_tag_name('a').click()
    time.sleep(2)
