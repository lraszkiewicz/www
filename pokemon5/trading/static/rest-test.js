$(document).ready(function() {
    $('#send').click(function() {
        var req = new XMLHttpRequest();

        req.addEventListener('error', function() {
            alert("Error!");
        });
        req.addEventListener('load', function() {
            if (this.status !== 200) {
                alert('Error!');
                return;
            }

            var response;
            try {
                response = JSON.parse(this.responseText);
            } catch(e) {
                alert('Error!');
                return;
            }

            if ((!('evolved1' in response)) || (!('evolved2' in response))) {
                alert('Error!');
                return;
            }

            $('#evolved1').text(response['evolved1']);
            $('#evolved2').text(response['evolved2']);
            $('#output').show();
        });

        var pokemon1 = $('#pokemon1').val();
        var pokemon2 = $('#pokemon2').val();

        if ((!pokemon1) || (!pokemon2)) {
            alert('Please enter Pokemon IDs.');
            return false;
        }

        var data = 'pokemon1=' + pokemon1 + '&pokemon2=' + pokemon2;

        req.open('POST', 'http://127.0.0.1:8000/api/trade/');
        req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        req.send(data);

        return false;
    })
});