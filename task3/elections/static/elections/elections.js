$(document).ready(function() {
    // google.charts.load('current', {packages: ['geochart', 'corechart', 'bar']});
    // google.charts.setOnLoadCallback(drawChart);
    function drawChart(candidateResults) {
        var data = google.visualization.arrayToDataTable(candidateResults);
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

    // google.charts.setOnLoadCallback(drawMap);
    function drawMap() {
        var data = google.visualization.arrayToDataTable(voivodeshipResults);
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
            'PL-DS': 'dolnoslaskie',
            'PL-KP': 'kujawsko-pomorskie',
            'PL-LU': 'lubelskie',
            'PL-LB': 'lubuskie',
            'PL-LD': 'lodzkie',
            'PL-MA': 'malopolskie',
            'PL-MZ': 'mazowieckie',
            'PL-OP': 'opolskie',
            'PL-PK': 'podkarpackie',
            'PL-PD': 'podlaskie',
            'PL-PM': 'pomorskie',
            'PL-SL': 'slaskie',
            'PL-SK': 'swietokrzyskie',
            'PL-WN': 'warminsko-mazurskie',
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

    // $(window).resize(function() {
    //     drawChart();
    //     drawMap();
    // });

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
        $('#results-title').text('Wyniki wyborów w ' + response['results_title']);
        $('#children-title').text('Wyniki wyborów w ' + response['children_title']);
        var resultsHereTable = '';
        var validBallots = 0;
        for (var i = 0; i < response['results_here'].length; ++i) {
            validBallots += response['results_here'][i]['votes'];
        }
        for (i = 0; i < response['results_here'].length; ++i) {
            resultsHereTable += '<tr><th>' + response['results_here'][i]['name'] + '</th>'
                              + '<td>' + response['results_here'][i]['votes'] + '</td>'
                              + '<td>' + (100.0 * response['results_here'][i]['votes'] / validBallots).toFixed(2) + '%</td></tr>';
        }
        $('#results-here').html(resultsHereTable);
        $('#eligible-voters').text(response['stats_here']['eligible_voters']);
        $('#issued-ballots').text(response['stats_here']['issued_ballots']);
        $('#casted-ballots').text(validBallots + response['stats_here']['spoilt_ballots']);
        $('#valid-ballots').text(validBallots);
        $('#spoilt-ballots').text(response['stats_here']['spoilt_ballots']);
    }

    getResults('http://127.0.0.1:8000/wybory/api/kraj/');

    $('a').click(function() {
        getResults(this.href);
        return false;
    });
});
