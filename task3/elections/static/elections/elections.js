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
        var data = google.visualization.arrayToDataTable(mapData);
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
            switch (v) {
                case '{{ slug }}':
                    return '{{ id }}';
            }
        }
        google.visualization.events.addListener(chart, 'regionClick', function(e) {
            if (d[e['region']]) {
                window.location.href = getURL(d[e['region']]);
            }
        });
    }

    $(window).resize(function() {
        drawChart();
        drawMap();
    });

    function getResults(url) {
        var req = new XMLHttpRequest();
        req.open('GET', url, false);
        req.send();
        if (req.status === 200)
            var response = JSON.parse(req.responseText);
        else
            alert(req.status);
        console.log(response);

        $('title').text(response['title'] + ' - Wybory Prezydenta Rzeczypospolitej Polskiej 2000');
        var breadcrumb = "";
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
        mapData = [['województwo', 'frekwencja']];
        for (i = 0; i < response['children'].length; ++i) {
            big_table_body += '<tr>';
            switch (response['type']) {
                case 'country':
                    big_table_body += '<td class="text-nowrap"><a href="/wybory/api/wojewodztwo/' + response['children'][i]['id'] + '/">' + response['children'][i]['name'] + '</a></td>';
                    break;
            }
            votes_row = '';
            votes_sum = 0;
            for (j = 0; j < response['candidates'].length; ++j) {
                votes_row += '<td>' + response['children_votes'][votes_index]['amount'] + '</td>';
                votes_sum += response['children_votes'][votes_index]['amount'];
                ++votes_index;
            }
            mapData.push([response['children'][i]['name'], (votes_sum + response['children_stats'][i]['spoilt_ballots']) / response['children_stats'][i]['eligible_voters']]);
            big_table_body += '<td>' + response['children_stats'][i]['eligible_voters'] + '</td>';
            big_table_body += '<td>' + response['children_stats'][i]['issued_ballots'] + '</td>';
            big_table_body += '<td>' + (votes_sum + response['children_stats'][i]['spoilt_ballots']) + '</td>';
            big_table_body += '<td>' + votes_sum + '</td>';
            big_table_body += '<td>' + response['children_stats'][i]['spoilt_ballots'] + '</td>';
            big_table_body += votes_row;
            big_table_body += '</tr>';
        }
        showMap = true;
        drawMap(mapData);
        $('#big-table-body').html(big_table_body);
    }

    getResults('http://127.0.0.1:8000/wybory/api/kraj/');

    $('a').click(function() {
        getResults(this.href);
        return false;
    });
});
