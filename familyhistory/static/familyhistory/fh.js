$(document).ready(function() {
    $('#search').on('input', function() {
        let query = $(this).val();
        if (query.length > 2) {  // Only search after 3 characters
            $.get('/api/person/search', {q: query}, function(data) {
                let results = $('#results');
                results.empty();
                data.forEach(function(person) {
                    results.append(`<li>${person.first_name} ${person.current_surname}</li>`);
                });
            });
        } else {
            $('#results').empty();
        }
    });
});