$(document).ready(function() {
    var loadedCharts = false;
    var chartData = [];
    var mapData = [];
    var showChart = false;
    var showMap = false;
    google.charts.load('current', {packages: ['geochart', 'corechart', 'bar']});
    google.charts.setOnLoadCallback(function() {
        loadedCharts = true;
        drawChart();
        drawMap();
    });
    function drawChart() {
        if (!loadedCharts || !showChart) {
            return;
        }
        var data = google.visualization.arrayToDataTable(chartData);
        var formatter = new google.visualization.NumberFormat({pattern: '#.##%'});
        formatter.format(data, 1);
        var options = {
            hAxis: {
                minValue: 0,
                maxValue: 1,
                format: 'percent'
            },
            legend: {
                position: 'none'
            },
            series: [
                {
                    color: '#49A5FB'
                }
            ],
            bars: 'horizontal',
            height: $("#chart").width() / 2.5
        };
        var chart = new google.charts.Bar(document.getElementById('chart'));
        chart.draw(data, google.charts.Bar.convertOptions(options));
    }

    function drawMap() {
        if (!loadedCharts || !showMap) {
            return;
        }
        var mapDataNew = [['województwo', 'frekwencja']];
        for (var i = 0; i < mapData.length; ++i) {
            mapDataNew.push([mapData[i][1], mapData[i][2]]);
        }
        var data = google.visualization.arrayToDataTable(mapDataNew);
        var formatter = new google.visualization.NumberFormat({pattern: '#.##%'});
        formatter.format(data, 1);
        var options = {
            region: 'PL',
            resolution: 'provinces',
            legend: {
                numberFormat: '#.##%'
            },
            colorAxis: {
                colors: ['#71B9FC', '#2191FB']
            }
        };
        var map_element = $('#map');
        map_element.show();
        map_element.height(map_element.width() * 0.624101);
        var chart = new google.visualization.GeoChart(document.getElementById('map'));
        chart.draw(data, options);
        var d = {
            'PL-DS': 'dolnośląskie',
            'PL-KP': 'kujawsko-pomorskie',
            'PL-LU': 'lubelskie',
            'PL-LB': 'lubuskie',
            'PL-LD': 'łódzkie',
            'PL-MA': 'małopolskie',
            'PL-MZ': 'mazowieckie',
            'PL-OP': 'opolskie',
            'PL-PK': 'podkarpackie',
            'PL-PD': 'podlaskie',
            'PL-PM': 'pomorskie',
            'PL-SL': 'śląskie',
            'PL-SK': 'świętokrzyskie',
            'PL-WN': 'warmińsko-mazurskie',
            'PL-WP': 'wielkopolskie',
            'PL-ZP': 'zachodniopomorskie'
        };
        function getURL(v) {
            for (var i = 0; i < mapData.length; ++i) {
                if (mapData[i][1] === v) {
                    return '/wybory/api/wojewodztwo/' + mapData[i][0] + '/';
                }
            }
        }
        google.visualization.events.addListener(chart, 'regionClick', function(e) {
            if (d[e['region']]) {
                getFromAPI(getURL(d[e['region']]));
            }
        });
    }

    $(window).resize(function() {
        drawChart();
        drawMap();
    });

    function hideEverything() {
        $('#breadcrumb-container').hide();
        $('#results-div').hide();
        $('#map').hide();
        $('#search-container').hide();
        $('#login-container').hide();
        $('#login-error').hide();
        $('#place-container').hide();

        $('#search-input').val('');
        $('#id_username').val('');
        $('#id_password').val('');
    }

    function showResults(response) {
        $('#breadcrumb-container').show();
        $('#results-div').show();
        $('title').text(response['title'] + ' - Wybory Prezydenta Rzeczypospolitej Polskiej 2000');
        var breadcrumb = '';
        for (var i = 0; i < response['breadcrumb'].length - 1; ++i) {
            breadcrumb += '<li>';
            for (var j = 0; j < response['breadcrumb'][i].length; ++j) {
                if (j > 0) {
                    breadcrumb += ', ';
                }
                breadcrumb += '<a href="' + response['breadcrumb'][i][j][1] + '">' + response['breadcrumb'][i][j][0] + '</a>';
            }
            breadcrumb += '</li>';
        }
        breadcrumb += '<li class="active">' + response['breadcrumb'][response['breadcrumb'].length - 1] + '</li>';
        $('#breadcrumb').html(breadcrumb);
        $('#results-title').text('Wyniki wyborów w ' + response['results_title']);
        $('#children-title').text('Wyniki wyborów w ' + response['children_title']);
        var resultsHereTable = '';
        var validBallots = 0;
        for (i = 0; i < response['results_here'].length; ++i) {
            validBallots += response['results_here'][i]['votes'];
        }
        chartData = [['', '']];
        for (i = 0; i < response['results_here'].length; ++i) {
            resultsHereTable += '<tr><th>' + response['results_here'][i]['name'] + '</th>'
                              + '<td>' + response['results_here'][i]['votes'] + '</td>'
                              + '<td>' + (100.0 * response['results_here'][i]['votes'] / validBallots).toFixed(2) + '%</td></tr>';
            chartData.push([response['results_here'][i]['name'], response['results_here'][i]['votes'] / validBallots]);
        }
        if ($.inArray(response['type'], ['country', 'voivodeship', 'municipality', 'district']) !== -1) {
            showChart = true;
            drawChart(chartData);
        }
        $('#results-here').html(resultsHereTable);

        $('#eligible-voters').text(response['stats_here']['eligible_voters']);
        $('#issued-ballots').text(response['stats_here']['issued_ballots']);
        $('#casted-ballots').text(validBallots + response['stats_here']['spoilt_ballots']);
        $('#valid-ballots').text(validBallots);
        $('#spoilt-ballots').text(response['stats_here']['spoilt_ballots']);
        $('#turnout-percent').text((100.0 * (validBallots + response['stats_here']['spoilt_ballots'])
            / response['stats_here']['eligible_voters']).toFixed(2) + '%');

        var big_table_headers = '';
        switch(response['type']) {
            case 'country':
                big_table_headers += '<th>Województwo</th>';
                break;
            case 'voivodeship':
                big_table_headers += '<th>Okręg</th>';
                break;
            case 'district':
                big_table_headers += '<th>Nr</th><th>Gmina</th>';
                break;
            case 'municipality':
                big_table_headers = '<th>Nr</th><th>Adres obwodu</th>';
                break;
        }
        big_table_headers += '<th>Uprawnieni</th><th>Wydane karty</th><th>Głosy oddane</th><th>Głosy ważne</th><th>Głosy nieważne</th>';
        for (i = 0; i < response['candidates'].length; ++i) {
            big_table_headers += '<th>' + response['candidates'][i]['first_name'] + ' ' + response['candidates'][i]['last_name'] + '</th>';
        }
        $('#big-table-headers').html(big_table_headers);
        var big_table_body = '';
        var votes_index = 0;
        var votes_row = '';
        var votes_sum = 0;
        if (response['type'] === 'country') {
            mapData = [];
            showMap = true;
        } else {
            showMap = false;
        }
        for (i = 0; i < response['children'].length; ++i) {
            big_table_body += '<tr>';
            switch (response['type']) {
                case 'country':
                    big_table_body += '<td class="text-nowrap"><a href="/wybory/api/wojewodztwo/' + response['children'][i]['id'] + '/">' + response['children'][i]['name'] + '</a></td>';
                    break;
                case 'voivodeship':
                    big_table_body += '<td class="text-nowrap"><a href="/wybory/api/okreg/' + response['children'][i]['district__id'] + '/">Okręg nr ' + response['children'][i]['district__id'] + '</a></td>';
                    break;
                case 'district':
                    big_table_body += '<td class="text-nowrap"><a href="/wybory/api/gmina/' + response['children'][i]['municipality__id'] + '/">' + response['children'][i]['municipality__id'] + '</a></td>';
                    big_table_body += '<td class="text-nowrap"><a href="/wybory/api/gmina/' + response['children'][i]['municipality__id'] + '/">' + response['children'][i]['municipality__name'] + '</a></td>';
                    break;
                case 'municipality':
                    big_table_body += '<td class="text-nowrap"><a href="/wybory/api/obwod/' + response['children'][i]['id'] + '/">' + response['children'][i]['number'] + '</a></td>';
                    big_table_body += '<td><a href="/wybory/api/obwod/' + response['children'][i]['id'] + '/">' + response['children'][i]['address'] + '</a></td>';
                    break;
            }
            votes_row = '';
            votes_sum = 0;
            for (j = 0; j < response['candidates'].length; ++j) {
                votes_row += '<td>' + response['children_votes'][votes_index]['amount'] + '</td>';
                votes_sum += response['children_votes'][votes_index]['amount'];
                ++votes_index;
            }
            if (response['type'] === 'country') {
                mapData.push([response['children'][i]['id'], response['children'][i]['name'],
                             (votes_sum + response['children_stats'][i]['spoilt_ballots']) / response['children_stats'][i]['eligible_voters']]);
            }
            big_table_body += '<td>' + response['children_stats'][i]['eligible_voters'] + '</td>';
            big_table_body += '<td>' + response['children_stats'][i]['issued_ballots'] + '</td>';
            big_table_body += '<td>' + (votes_sum + response['children_stats'][i]['spoilt_ballots']) + '</td>';
            big_table_body += '<td>' + votes_sum + '</td>';
            big_table_body += '<td>' + response['children_stats'][i]['spoilt_ballots'] + '</td>';
            big_table_body += votes_row;
            big_table_body += '</tr>';
        }
        drawMap(mapData);
        $('#big-table-body').html(big_table_body);
    }

    function showSearchResults(response) {
        $('#search-input').val(response['query']);
        $('#search-container').show();
        $('#search-title').text('Wyniki wyszukiwania gmina dla "' + response['query'] + '"');
        if (response['search_results'].length === 0) {
            $('#search-not-found').show();
            $('#search-results').hide();
            return;
        } else {
            $('#search-results').show();
            $('#search-not-found').hide();
        }
        var results_html = '';
        for (var i = 0; i < response['search_results'].length; ++i) {
            results_html += '<a href="' + response['search_results'][i][1] + '" class="list-group-item">' + response['search_results'][i][0] + '</a>';
        }
        $('#search-results').html(results_html);
    }

    function showPlace(response) {
        $('#breadcrumb-container').show();
        var breadcrumb = '';
        for (var i = 0; i < response['breadcrumb'].length - 1; ++i) {
            breadcrumb += '<li>';
            for (var j = 0; j < response['breadcrumb'][i].length; ++j) {
                if (j > 0) {
                    breadcrumb += ', ';
                }
                breadcrumb += '<a href="' + response['breadcrumb'][i][j][1] + '">' + response['breadcrumb'][i][j][0] + '</a>';
            }
            breadcrumb += '</li>';
        }
        breadcrumb += '<li class="active">' + response['breadcrumb'][response['breadcrumb'].length - 1] + '</li>';
        $('#breadcrumb').html(breadcrumb);

        $('#place-container').show();
        $('#place-form').replaceWith(placeFormClone.clone());
        var validBallots = 0;
        var formCandidates = '';
        for (i = 0; i < response['results_here'].length; ++i) {
            validBallots += response['results_here'][i]['votes'];
            formCandidates += '<div class="form-group"><label for="id_candidate_' + response['results_here'][i]['candidate_id'] + '" class="col-md-5 control-label">' + response['results_here'][i]['name'] + '</label>';
            formCandidates += '<div class="col-md-7"><input type="number" name="candidate_' + response['results_here'][i]['candidate_id'] + '" value="' + response['results_here'][i]['votes'] + '" class="form-control" required id="id_candidate_' + response['results_here'][i]['candidate_id'] + '"/></div></div>';
        }
        $('#place-form').append(formCandidates);
        $('#place-form').append('<input type="hidden" name="place_id" value="' + response['place_id'] + '">');
        $('#place-form').append('<button type="submit" class="btn btn-primary" id="place-form-submit">Zapisz</button>');
        if (!response['is_authenticated']) {
            $('#place-form input').prop('disabled', true);
        }
        $('#id_eligible_voters').val(response['stats_here']['eligible_voters']);
        $('#id_issued_ballots').val(response['stats_here']['issued_ballots']);
        $('#id_casted_ballots').val(validBallots + response['stats_here']['spoilt_ballots']);
        $('#id_valid_ballots').val(validBallots);
        $('#id_spoilt_ballots').val(response['stats_here']['spoilt_ballots']);
    }

    function getFromAPI(url) {
        var req = new XMLHttpRequest();
        req.open('GET', url, true);
        req.onreadystatechange = function() {
            if (req.readyState !== 4)
                return;

            if (req.status === 200)
                var response = JSON.parse(req.responseText);
            else {
                $('html').css('cursor', 'default');
                alert(req.status);
                return;
            }
            console.log(response);

            showLoggedIn(response);
            if (response['type'] === 'country') {
                localStorage.setItem('lastCountryResponse', JSON.stringify(response));
            }
            if ($.inArray(response['type'], ['country', 'voivodeship', 'municipality', 'district']) !== -1) {
                hideEverything();
                showResults(response);
            } else if (response['type'] === 'search_results') {
                hideEverything();
                showSearchResults(response);
            } else if (response['type'] === 'place_get') {
                hideEverything();
                showPlace(response);
            } else if (response['type'] === 'logout' && !response['is_authenticated']) {
                $('#place-form input').prop('disabled', true);
            }

            setOnClicks();

            $('html').css('cursor', 'default');
        };
        $('html').css('cursor', 'progress');
        req.send();
    }

    function login(data) {
        var req2 = new XMLHttpRequest();
        req2.open('POST', '/wybory/api/login/', true);
        req2.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        req2.onreadystatechange = function() {
            if (req2.readyState !== 4)
                return;

            if (req2.status === 200)
                var response = JSON.parse(req2.responseText);
            else {
                $('html').css('cursor', 'default');
                alert(req2.status);
                return;
            }
            console.log(response);
            if (!response['success']) {
                $('#login-error').show();
                showLoggedIn(response);
                setOnClicks();
            } else {
                getFromAPI('/wybory/api/kraj/');
            }

            $('html').css('cursor', 'default');
        };
        $('html').css('cursor', 'progress');
        req2.send(data);
    }

    function editPlace(data, place_id, municipality_url) {
        var req2 = new XMLHttpRequest();
        req2.open('POST', '/wybory/api/edytuj_obwod/', true);
        req2.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        req2.onreadystatechange = function() {
            if (req2.readyState !== 4)
                return;

            if (req2.status !== 200) {
                $('html').css('cursor', 'default');
                alert(req2.status);
                return;
            }
            getFromAPI(municipality_url);

            $('html').css('cursor', 'default');
        };
        $('html').css('cursor', 'progress');
        req2.send(data);
    }

    function showLoginPage() {
        hideEverything();
        $('#auth-link').trigger('blur');
        $('#login-container').show();
    }

    function showLoggedIn(response) {
        var auth_link = $('#auth-link');
        auth_link.trigger('blur');
        if (response['is_authenticated']) {
            auth_link.html('<span class="glyphicon glyphicon-user"></span> Wyloguj (' + response['username'] + ')');
            auth_link.attr('href', '/wybory/api/logout/');
        } else {
            auth_link.html('<span class="glyphicon glyphicon-user"></span> Zaloguj');
            auth_link.attr('href', '/wybory/api/login/');
        }
    }

    function setOnClicks() {
        $('a').off('click').on('click', function(e) {
            e.preventDefault();
            if (this.href.match('login/$')) {
                showLoginPage();
            } else {
                getFromAPI(this.href);
            }
            return false;
        });

        $('#search-form').off('submit').on('submit', function(e) {
            e.preventDefault();
            getFromAPI(this.action + '?' + $('#search-form').serialize());
            return false;
        });

        $('#login-form').off('submit').on('submit', function(e) {
            e.preventDefault();
            login($('#login-form').serialize());
            return false;
        });

        $('#place-form').off('submit').on('submit', function(e) {
            e.preventDefault();
            editPlace($('#place-form').serialize(), $('#place-form input[name=place_id]')[0].value, $('#breadcrumb a:last')[0].href);
            return false;
        });
    }

    hideEverything();

    var lastCountryResponse = localStorage.getItem('lastCountryResponse');
    if (lastCountryResponse !== null) {
        console.log('Loading index from localStorage.');
        lastCountryResponse = JSON.parse(lastCountryResponse);
        console.log(lastCountryResponse);
        hideEverything();
        showLoggedIn(lastCountryResponse);
        showResults(lastCountryResponse);
        setOnClicks();
    }

    var placeFormClone = $('#place-form').clone();

    console.log('Loading index from server.');
    getFromAPI('/wybory/api/kraj/');
});
