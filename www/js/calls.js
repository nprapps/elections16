var $nprCall = null;
var $nprUncall = null;
var $toggleAP = null;

var onDocumentReady = function() {
    $nprCall = $('.npr-call');
    $nprUncall = $('.npr-uncall');
    $toggleAP = $('.ap-call .btn');

    $nprCall.on('click', onCallClick);
    $nprUncall.on('click', onUncallClick);
    $toggleAP.on('click', onToggleAPClick);
}

$(onDocumentReady);

/*
 * When PR call button is clicked.
 */
var onCallClick = function() {
    var $this = $(this);
    var $parent = $this.parent('span');
    var $row = $this.closest('tr');
    var race_slug = $row.data('state-slug');

    $row.find('.npr-uncall,.npr-call,.npr-winner').addClass('hidden');

    $this.addClass('hidden');

    $this.siblings('.npr-uncall,.npr-winner').removeClass('hidden');

    var data = {
        race_slug: race_slug,
        first_name: $parent.attr('data-first-name'),
        last_name: $parent.attr('data-last-name')
    };

    $.post(window.location.href + 'call/', data);
}

/*
 * When NPR uncall button is clicked.
 */
var onUncallClick = function() {
    var $this = $(this);
    var $row = $this.closest('tr');
    var race_slug = $row.data('state-slug');

    $this.addClass('hidden');

    $row.find('.npr-call').removeClass('hidden');
    $row.find('.npr-winner').addClass('hidden');

    var data = {
        race_slug: race_slug,
        clear_all: true
    };

    $.post(window.location.href + 'call/', data);
}

/*
 * When AP toggle button is clicked.
 */
var onToggleAPClick = function() {
    var $this = $(this);
    var $row = $this.closest('tr');
    var race_slug = $(this).attr('id');

    // Accept AP calls
    if ($this.hasClass('btn-success')) {
        var data = {
            race_slug: race_slug,
            accept_ap_call: false
        };

        $.post(window.location.href + 'call/', data);

        $this.removeClass('btn-success');
        $this.addClass('btn-warning');
        $this.html('Not accepting AP calls');

        $row.find('.npr-call').removeClass('hidden');
    // Deny AP calls
    } else {
        var data = {
            race_slug: race_slug,
            accept_ap_call: true
        };

        $.post(window.location.href + 'call/', data);

        $this.removeClass('btn-warning');
        $this.addClass('btn-success');
        $this.html('Accepting AP calls');

        $row.find('.npr-call,.npr-uncall,.npr-winner').addClass('hidden');
    }
}
