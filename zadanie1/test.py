from selenium import webdriver
import random
import time

SLEEP_TIME = 0  # seconds
TESTS = 10


def check(condition, text):
    if condition:
        print('OK: {}'.format(text))
    else:
        print('FAILED: {}'.format(text))
        raise AssertionError


browser = webdriver.Chrome()

for i in range(TESTS):
    print('TEST #{}\n'.format(i))
    browser.get('http://students.mimuw.edu.pl/~lr371594/wybory/')
    selected_results = None
    selected_title = None
    for j in range(4):  # 4 = [kraj, województwo, okręg, gmina]
        if selected_title is not None:
            check(selected_title in browser.title, 'selected_title in browser.title')

        this_results = []
        for row in browser.find_element_by_id('stats').find_elements_by_tag_name('tr')[:-1]:
            this_results.append(int(row.find_element_by_tag_name('td').text))
        for row in browser.find_element_by_id('parent-results').find_elements_by_tag_name('tr'):
            this_results.append(int(row.find_element_by_tag_name('td').text))
        print('this_results ({}): {}'.format(browser.title.split(' - ')[0], this_results))
        if selected_results is not None:
            check(selected_results == this_results, 'selected_results == this_results')

        children_table = browser.find_element_by_id('children-results')
        children_sum = [0] * len(this_results)
        for child in children_table.find_elements_by_tag_name('tr')[1:]:
            child_results = [int(x.text) for x in child.find_elements_by_tag_name('td')[(2 if j == 3 else 1):]]
            for k in range(len(child_results)):
                children_sum[k] += child_results[k]
        print('children_sum: {}'.format(children_sum))
        check(this_results == children_sum, 'this_results == children_sum')

        selected_row = None
        if j < 3:
            selected_row = random.choice(children_table.find_elements_by_tag_name('tr')[1:])
            selected_results = [int(x.text) for x in selected_row.find_elements_by_tag_name('td')[(2 if j == 3 else 1):]]
            selected_title = selected_row.find_element_by_tag_name('td').text
            print('selected_title: {}'.format(selected_title))
            print('selected_results: {}'.format(selected_results))

        print('sleep {}'.format(SLEEP_TIME))
        time.sleep(SLEEP_TIME)

        if j < 3:
            selected_row.find_element_by_tag_name('td').find_element_by_tag_name('a').click()

        print('')
