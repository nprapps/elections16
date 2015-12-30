describe('app.js', function() {
    it('should render a JST', function() {
        renderExampleTemplate();
        var text = $('#template-example').text();

        expect(text).not.toBeNull();
    })
});