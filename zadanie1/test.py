from selenium import webdriver

browser = webdriver.Chrome()
browser.get('http://students.mimuw.edu.pl/~lr371594/wybory/')

big_table = browser.find_element_by_class_name('big-table')
print([x.text for x in big_table.find_elements_by_tag_name('th')])
print([x.text for x in big_table.find_elements_by_tag_name('td')])