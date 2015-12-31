// Global jQuery references

//
var candidates = {}

/*
 * Run on page load.
 */
var onDocumentLoad = function(e) {
    // Cache jQuery references
    candidates = getCandidates();
    SHARE.setup();
}

var getCandidates = function() {
    $.getJSON('assets/candidates.json', function(data) {
        return data;
    });
}


$(onDocumentLoad);
