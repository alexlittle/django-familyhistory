const apiUrls = document.getElementById('api-urls').dataset;
const personDetailBase = apiUrls.personDetailUrl.replace(/\/0\/?$/, '/');
const searchInput = document.getElementById('search');
const results = document.getElementById('results');

let controller;
let timer;

searchInput.addEventListener('input', () => {
    clearTimeout(timer);
    const query = searchInput.value;

    if (query.length <= 1) {
        results.replaceChildren();
        return;
    }

    timer = setTimeout(async () => {
        controller?.abort();
        controller = new AbortController();

        const url = new URL(apiUrls.personSearch, window.location.origin);
        url.searchParams.set('q', query);

        try {
            const response = await fetch(url, {signal: controller.signal});
            if (!response.ok) return;
            const data = await response.json();

            results.replaceChildren(...data.map(person => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = personDetailBase + person.id;
                a.textContent = person.display_name;
                li.append(a, ` ${person.birth_death_date}`);
                return li;
            }));
        } catch (err) {
            if (err.name !== 'AbortError') throw err;
        }
    }, 250);
});