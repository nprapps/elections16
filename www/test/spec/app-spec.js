describe('app.js', function() {
    var candidates = [];
    beforeEach(function() {
        jasmine.getJSONFixtures().fixturesPath='base/data/';

        candidates = getJSONFixture('candidates.json')
        console.log(candidates.length);
    });

    it('should have 60 candidates', function() {
        expect(candidates.length).toBe(60);
    });
});