describe('app.js', function() {
    var candidates = [];
    beforeEach(function() {
        jasmine.getJSONFixtures().fixturesPath='base/data/';
        candidates = getJSONFixture('candidates.json')
    });

    describe('candidates.json', function() {
        it('the first candidate should be Carly Fiorina', function() {
            expect(candidates[0]['first'] + ' ' + candidates[0]['last']).toBe('Carly Fiorina');
        });
    });

    it('should build a complete list of candidate names', function() {
        var candidateList = makeListOfCandidates(candidates);
        expect(candidateList.length).toBe(candidates.length);
    });



});