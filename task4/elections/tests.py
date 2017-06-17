from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.support.select import Select
from time import sleep


# czas sleepa przy przechodzeniu pomiędzy stronami admina
SLEEP_TIME_CREATION = 1
# czas sleepa przy przechodzeniu pomiędzy stronami klienta
SLEEP_TIME_BROWSING = 1  # nie powinno być 0
# czas sleepa przed zamknięciem przeglądarki po zakończeniu testowania
SLEEP_TIME_EXIT = 2


class SeleniumTestCase(StaticLiveServerTestCase):
    def setUp(self):
        User.objects.create_superuser('admin', 'admin@admin.com', 'admin123')
        self.browser = webdriver.Chrome()
        super(SeleniumTestCase, self).setUp()

    # Test rozpoczyna się z pustą bazą danych.
    # Tworzę przykładowe dane przeklikując się przez panel admina.
    # Później sprawdzam, czy dane wyświetlone w kliencie się zgadzają.
    def testEverything(self):
        # Loguję się do django-admin.
        browser = self.browser
        browser.get(self.live_server_url + '/admin/')
        browser.find_element_by_id('id_username').send_keys('admin')
        browser.find_element_by_id('id_password').send_keys('admin123')
        browser.find_element_by_css_selector('input[type=\'submit\']').click()

        # W django-admin tworzę: województwo, okręg, gminę, obwód, dwóch kandydatów i wypełniam wyniki.
        browser.find_element_by_link_text('Voivodeships').click()
        browser.find_element_by_class_name('addlink').click()
        browser.find_element_by_id('id_name').send_keys('kujawsko-pomorskie')
        sleep(SLEEP_TIME_CREATION)
        browser.find_element_by_name('_save').click()
        browser.find_element_by_link_text('Home').click()

        browser.find_element_by_link_text('Districts').click()
        browser.find_element_by_class_name('addlink').click()
        browser.find_element_by_id('id_id').send_keys('1')
        sleep(SLEEP_TIME_CREATION)
        browser.find_element_by_name('_save').click()
        browser.find_element_by_link_text('Home').click()

        browser.find_element_by_link_text('Municipalities').click()
        browser.find_element_by_class_name('addlink').click()
        browser.find_element_by_id('id_id').send_keys('123456')
        browser.find_element_by_id('id_name').send_keys('Włocławek')
        sleep(SLEEP_TIME_CREATION)
        browser.find_element_by_name('_save').click()
        browser.find_element_by_link_text('Home').click()

        browser.find_element_by_link_text('Places').click()
        browser.find_element_by_class_name('addlink').click()
        browser.find_element_by_id('id_number').send_keys('1')
        browser.find_element_by_id('id_address').send_keys('Jakiś adres')
        Select(browser.find_element_by_id('id_voivodeship')).select_by_index(1)
        Select(browser.find_element_by_id('id_district')).select_by_index(1)
        Select(browser.find_element_by_id('id_municipality')).select_by_index(1)
        sleep(SLEEP_TIME_CREATION)
        browser.find_element_by_name('_save').click()
        browser.find_element_by_link_text('Home').click()

        browser.find_element_by_link_text('Candidates').click()
        browser.find_element_by_class_name('addlink').click()
        browser.find_element_by_id('id_first_name').send_keys('Janusz')
        browser.find_element_by_id('id_last_name').send_keys('Korwin-Mikke')
        sleep(SLEEP_TIME_CREATION)
        browser.find_element_by_name('_save').click()
        browser.find_element_by_link_text('Home').click()

        browser.find_element_by_link_text('Candidates').click()
        browser.find_element_by_class_name('addlink').click()
        browser.find_element_by_id('id_first_name').send_keys('Lech')
        browser.find_element_by_id('id_last_name').send_keys('Wałęsa')
        sleep(SLEEP_TIME_CREATION)
        browser.find_element_by_name('_save').click()
        browser.find_element_by_link_text('Home').click()

        browser.find_element_by_link_text('Results').click()
        browser.find_element_by_link_text('1').click()
        browser.find_element_by_id('id_eligible_voters').clear()
        browser.find_element_by_id('id_eligible_voters').send_keys('33333')
        browser.find_element_by_id('id_issued_ballots').clear()
        browser.find_element_by_id('id_issued_ballots').send_keys('22222')
        browser.find_element_by_id('id_spoilt_ballots').clear()
        browser.find_element_by_id('id_spoilt_ballots').send_keys('111')
        browser.find_element_by_id('id_votes_set-0-amount').clear()
        browser.find_element_by_id('id_votes_set-0-amount').send_keys('4242')
        browser.find_element_by_id('id_votes_set-1-amount').clear()
        browser.find_element_by_id('id_votes_set-1-amount').send_keys('1234')
        sleep(SLEEP_TIME_CREATION)
        browser.find_element_by_name('_save').click()

        sleep(SLEEP_TIME_BROWSING)
        # Wchodzę na stronę główną.
        browser.get(self.live_server_url)
        # Sprawdzam poprawność wyświetlonych wyników, następnie przechodzę do dziecka i tam robię to samo.
        # Kończę w gminie.
        levels = 4
        for i in range(levels):
            sleep(SLEEP_TIME_BROWSING)

            # Sprawdzam wyniki kandydatów.
            results_here_rows = browser.find_element_by_id('results-here').find_elements_by_tag_name('tr')
            results_here = {}
            for row in results_here_rows:
                results_here[row.find_element_by_tag_name('th').text] = int(row.find_elements_by_tag_name('td')[0].text)
            assert(len(results_here) == 2)
            assert(results_here['Janusz Korwin-Mikke'] == 4242)
            assert(results_here['Lech Wałęsa'] == 1234)

            # Sprawdzam statystyki.
            stats_here_rows = browser.find_element_by_id('stats-here').find_elements_by_tag_name('tr')
            stats_here = {}
            for row in stats_here_rows:
                try:
                    stats_here[row.find_element_by_tag_name('th').text] = int(row.find_element_by_tag_name('td').text)
                except ValueError:  # frekewncja nie jest intem
                    pass
            assert(stats_here['Uprawnieni'] == 33333)
            assert(stats_here['Wydane karty'] == 22222)
            assert(stats_here['Głosy oddane'] == 4242 + 1234 + 111)
            assert(stats_here['Głosy ważne'] == 4242 + 1234)
            assert(stats_here['Głosy nieważne'] == 111)

            # Sprawdzam tabelę z dziećmi.
            child_results = dict(zip(
                [e.text for e in browser.find_element_by_id('big-table-headers').find_elements_by_tag_name('th')],
                [e.text for e in browser.find_element_by_id('big-table-body').find_element_by_tag_name('tr')
                                        .find_elements_by_tag_name('td')]
            ))
            assert(child_results['Janusz Korwin-Mikke'] == '4242')
            assert(child_results['Lech Wałęsa'] == '1234')
            assert(child_results['Uprawnieni'] == '33333')
            assert(child_results['Wydane karty'] == '22222')
            assert(child_results['Głosy oddane'] == str(4242 + 1234 + 111))
            assert(child_results['Głosy ważne'] == str(4242 + 1234))
            assert(child_results['Głosy nieważne'] == '111')

            # O ile nie jestem już w gminie, to przechodzę do dziecka.
            if i != levels - 1:
                browser.find_element_by_id('big-table-body').find_element_by_tag_name('a').click()

        sleep(SLEEP_TIME_EXIT)
