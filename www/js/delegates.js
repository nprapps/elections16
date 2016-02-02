// settings
var DELEGATE_DATA = {
    "republicans": {
        "del_needed": 1237,
        "last_updated": "Feb. 1, 2016, 11:56 p.m. EST",
        "candidates": [
            { "name_last": "Bush", "del_total": 0 },
            { "name_last": "Carson", "del_total": 2 },
            { "name_last": "Christie", "del_total": 0 },
            { "name_last": "Cruz", "del_total": 8 },
            { "name_last": "Fiorina", "del_total": 0 },
            { "name_last": "Gilmore", "del_total": 0 },
            { "name_last": "Huckabee", "del_total": 0 },
            { "name_last": "Kasich", "del_total": 0 },
            { "name_last": "Paul", "del_total": 1 },
            { "name_last": "Rubio", "del_total": 6 },
            { "name_last": "Santorum", "del_total": 0 },
            { "name_last": "Trump", "del_total": 7 }
        ]
    },
    "democrats": {
        "del_needed": 2382,
        "last_updated": "Feb. 1, 2016, 11:56 p.m. EST",
        "candidates": [
            { "name_last": "Clinton", "del_total": 384 },
            { "name_last": "Sanders", "del_total": 29 },
            { "name_last": "O'Malley", "del_total": 2 },
            { "name_last": "Uncommitted", "del_total": 207 }
        ]
    }
};

// objects/vars
var $delegatesDemSlide = $('#delegates-dem');
var $delegatesGOPSlide = $('#delegates-gop');

// don't run any of this unless the slide actually exists
if ($delegatesDemSlide || $delegatesGOPSlide) {
    // load/process delegate json
    var formatDelegateData = function() {
        var parties = Object.keys(DELEGATE_DATA);

        parties.forEach(function(d, i) {
            DELEGATE_DATA[d]['candidates'].forEach(function(a, b) {
                a['name_slug'] = a['name_last'].toLowerCase();
                a['amt_pct'] = ((a['del_total'] / DELEGATE_DATA[d]['del_needed']) * 100).toFixed(1);
            });

            // sort list by # of delegates
            DELEGATE_DATA[d]['candidates'] = _.sortBy(DELEGATE_DATA[d]['candidates'], 'del_total');
            DELEGATE_DATA[d]['candidates'].reverse();
        });

        if ($delegatesDemSlide) {
            renderDelegates('democrats');
        }
        if ($delegatesGOPSlide) {
            renderDelegates('republicans');
        }
    }

    // display delegate info
    var renderDelegates = function(party) {
        var $delegateSlide = null;
        switch(party) {
            case 'democrats':
                $delegateSlide = $delegatesDemSlide;
                break;
            case 'republicans':
                $delegateSlide = $delegatesGOPSlide;
                break;
        }

        var $delegatesNeeded = $delegateSlide.find('.needed');
        var $delegateChart = $delegateSlide.find('ul.delegates');
        var $delegateTimestamp = $delegateSlide.find('.timestamp');

        var delsNeeded = DELEGATE_DATA[party]['del_needed'];
        var candidates = DELEGATE_DATA[party]['candidates'];
        var delegateHTML = '';

        $delegateChart.empty();

        candidates.forEach(function(d, i) {
            delegateHTML += JST.delegate({ candidate: d });
        });

        $delegateChart.append(delegateHTML);

        // show delegates needed
        $delegatesNeeded.empty().text(commaFormat(delsNeeded) + ' needed to win');

        // update timestamp
        $delegateTimestamp.empty().text('As of ' + DELEGATE_DATA[party]['last_updated']);
    }

    // comma formatter: http://stackoverflow.com/questions/1990512/add-comma-to-numbers-every-three-digits-using-jquery
    var commaFormat = function(val) {
        var v = val.toString();
        v = v.replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
        return v;
    }

    // initialize and set interval
    formatDelegateData();
}
