describe('candidates.json', function() {
    var candidates = [];
    beforeEach(function() {
        jasmine.getJSONFixtures().fixturesPath='base/data/';
        candidates = getJSONFixture('candidates.json')
    });

    it('should have 60 candidates', function() {
        expect(candidates.length).toBe(60);
    });

    it('the first candidate should be Carly Fiorina', function() {
        expect(candidates[0]['first'] + ' ' + candidates[0]['last']).toBe('Carly Fiorina');
    });
});