const searchPerson = document.getElementById('searchPerson');
const apiUrls = document.getElementById('api-urls').dataset;

searchPerson.addEventListener('input', function () {
    const query = this.value;
    if (query.length > 1) {
        fetch(`${apiUrls.personSearch}?q=${query}`)
            .then(response => response.json())
            .then(data => {
                const resultsDiv = document.getElementById('searchResults');
                resultsDiv.innerHTML = '';
                data.forEach(person => {
                    const div = document.createElement('div');
                    div.textContent = person.display_name + " " + person.birth_death_date;
                    div.onclick = () => {
                        document.getElementById(searchPerson.dataset.targetInput).value = person.id;
                        document.getElementById('selectedPerson').textContent =
                            "Selected: " + person.display_name + " " + person.birth_death_date;
                        resultsDiv.innerHTML = '';
                    };
                    resultsDiv.appendChild(div);
                });
            });
    }
});
