var dataDelegates = null;
var $delegateSlide = $('#delegates')
var $delegateChart = $delegateSlide.find('ul.delegates');

var loadDelegateData = function(url) {
    $.getJSON(url, function(data) {
        var parties = Object.keys(data);

        dataDelegates = data;

        parties.forEach(function(d, i) {
            // cast delegate totals as numbers
            dataDelegates[d]['candidates'].forEach(function(a, b) {
                a['del_total'] = Number(a['del_total']);
            });

            // sort list by # of delegates
            dataDelegates[d]['candidates'] = _.sortBy(dataDelegates[d]['candidates'], 'del_total');
            dataDelegates[d]['candidates'].reverse();
        });

        // TODO: filling in the republican delegate card as an example
        renderDelegates('republicans');
    })
}

var renderDelegates = function(party) {
    var delegatesNeeded = dataDelegates[party]['del_needed'];
    var candidates = dataDelegates[party]['candidates'];
    var delegateHTML = '';

    $delegateChart.empty();

    candidates.forEach(function(d, i) {
        delegateHTML += JST.delegate({ candidate: d });
    });

    $delegateChart.append(delegateHTML);
}

loadDelegateData('/delegates.json');
