// settings
var DELEGATE_DATA_URL = './delegates.json';
var DELEGATE_UPDATE_INTERVAL = 120000;

// objects/vars
var dataDelegates = null;
var $delegateSlide = $('#delegates')

// don't run any of this unless the slide actually exists
if ($delegateSlide) {
    var $delegatesNeeded = $delegateSlide.find('.needed');
    var $delegateChart = $delegateSlide.find('ul.delegates');
    var $delegateTimestamp = $delegateSlide.find('.timestamp');
    var delegateInterval = null;

    // load/process delegate json
    var loadDelegateData = function() {
        console.log('refresh delegate data');
        $.getJSON(DELEGATE_DATA_URL, function(data) {
            var parties = Object.keys(data);

            dataDelegates = data;

            parties.forEach(function(d, i) {
                dataDelegates[d]['candidates'].forEach(function(a, b) {
                    a['name_slug'] = a['name_last'].toLowerCase();
                    a['amt_pct'] = ((a['del_total'] / dataDelegates[d]['del_needed']) * 100).toFixed(1);
                });

                // sort list by # of delegates
                dataDelegates[d]['candidates'] = _.sortBy(dataDelegates[d]['candidates'], 'del_total');
                dataDelegates[d]['candidates'].reverse();
            });

            // TODO: filling in the republican delegate card as an example
            renderDelegates('republicans');
        })
    }

    // display delegate info
    var renderDelegates = function(party) {
        var delsNeeded = dataDelegates[party]['del_needed'];
        var candidates = dataDelegates[party]['candidates'];
        var delegateHTML = '';

        $delegateChart.empty();

        candidates.forEach(function(d, i) {
            delegateHTML += JST.delegate({ candidate: d });
        });

        $delegateChart.append(delegateHTML);

        // show delegates needed
        $delegatesNeeded.empty().text(commaFormat(delsNeeded) + ' needed to win');

        // update timestamp
        var d = new Date(dataDelegates[party]['last_updated']);
        var timestamp = moment(d).format('MMM D, YYYY [at] h:mm a');
        $delegateTimestamp.empty().text('As of ' + timestamp);
    }

    // comma formatter: http://stackoverflow.com/questions/1990512/add-comma-to-numbers-every-three-digits-using-jquery
    var commaFormat = function(val) {
        var v = val.toString();
        v = v.replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
        return v;
    }

    // initialize and set interval
    loadDelegateData();
    delegateInterval = setInterval(loadDelegateData, DELEGATE_UPDATE_INTERVAL);
}
