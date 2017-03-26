from selenium import webdriver
import random
import time

browser = webdriver.Chrome()

SLEEP_TIME = 3  # seconds
TESTS = 10
DEPTH = 3  # 3 = [województwo, okręg, gmina]

for i in range(TESTS):
    print('Test #{}'.format(i))
    browser.get('http://students.mimuw.edu.pl/~lr371594/wybory/')
    for j in range(DEPTH):
        this_results = []
        for row in browser.find_element_by_id('stats').find_elements_by_tag_name('tr')[:-1]:
            this_results.append(int(row.find_element_by_tag_name('td').text))
        for row in browser.find_element_by_id('parent-results').find_elements_by_tag_name('tr'):
            this_results.append(int(row.find_element_by_tag_name('td').text))
        # print("Results in this_results)
        print('Results in {}: {}'.format(browser.title.split(' - ')[0], this_results))

        time.sleep(SLEEP_TIME)

        children_table = browser.find_element_by_id('children-results')
        children_sum = [0] * len(this_results)
        for child in children_table.find_elements_by_tag_name('tr')[1:]:
            child_results = [int(x.text) for x in child.find_elements_by_tag_name('td')[1:]]
            for k in range(len(child_results)):
                children_sum[k] += child_results[k]
        print('Sum of results in children: {}'.format(children_sum))
        assert this_results == children_sum

        random_row = random.choice(children_table.find_elements_by_tag_name('tr')[1:])
        print('Selected {}'.format(random_row.find_elements_by_tag_name('td')[0].text))
        random_row.find_element_by_tag_name('td').find_element_by_tag_name('a').click()
