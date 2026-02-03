const apiUrls = document.getElementById('api-urls').dataset;
const personDetailBase = apiUrls.personDetailUrl.replace(/\/0\/?$/, '/');

$(document).ready(function() {
    $('#search').on('input', function() {
        let query = $(this).val();
        if (query.length > 1) {  // Only search after 2 characters
            $.get(apiUrls.personSearch, {q: query}, function(data) {
                let results = $('#results');
                results.empty();
                data.forEach(function(person) {
                    personDetailUrl = personDetailBase + person.id;
                    results.append(`<li><a href="${personDetailUrl}">${person.display_name}</a> b.${person.birth_year}</li>`);
                });
            });
        } else {
            $('#results').empty();
        }
    });
});