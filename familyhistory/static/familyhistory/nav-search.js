const navApiUrls = document.getElementById('api-urls').dataset;
const navPersonDetailBase = navApiUrls.personDetailUrl.replace(/\/0\/?$/, '/');
const navSearchInput = document.getElementById('navSearchPerson');
const navSearchResults = document.getElementById('navSearchResults');

let navSearchController;
let navSearchTimer;

function clearNavSearchResults() {
    navSearchResults.replaceChildren();
}

navSearchInput.addEventListener('input', () => {
    clearTimeout(navSearchTimer);
    const query = navSearchInput.value;

    if (query.length <= 1) {
        clearNavSearchResults();
        return;
    }

    navSearchTimer = setTimeout(async () => {
        navSearchController?.abort();
        navSearchController = new AbortController();

        const url = new URL(navApiUrls.personSearch, window.location.origin);
        url.searchParams.set('q', query);

        try {
            const response = await fetch(url, {signal: navSearchController.signal});
            if (!response.ok) return;
            const data = await response.json();

            navSearchResults.replaceChildren(...data.map(person => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = navPersonDetailBase + person.id;
                a.textContent = `${person.display_name} ${person.birth_death_date}`;
                li.append(a);
                return li;
            }));
        } catch (err) {
            if (err.name !== 'AbortError') throw err;
        }
    }, 250);
});

document.addEventListener('click', (event) => {
    if (!event.target.closest('.nav-search')) {
        clearNavSearchResults();
    }
});

navSearchInput.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        clearNavSearchResults();
    }
});
