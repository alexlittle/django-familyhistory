const apiUrls = document.getElementById('api-urls').dataset;
const treeUrlBase = apiUrls.treeUrl;

const personDetailTemplate = apiUrls.personDetailUrl;
const personUrl = id => personDetailTemplate.replace(/0(?=\/?$)/, id);

let treeUrl
if (typeof personId !== 'undefined' && personId !== null){
  treeUrl = `${treeUrlBase}/${personId}`;
} else {
  treeUrl = treeUrlBase
}

fetch(treeUrl)
    .then(res => res.json())
    .then(data => create(data))
    .catch(err => console.error(err))

function addPersonLinks(container) {
  container.querySelectorAll('.card').forEach(card => {
    if (card.querySelector('.card-person-link')) return;

    // datum may be on the card or on an ancestor wrapper
    let el = card, node = null;
    while (el && el !== container) {
      if (el.__data__) { node = el.__data__; break; }
      el = el.parentElement;
    }

    const person = node && node.data;
    if (!person || !person.id || person.to_add) return;

    if (getComputedStyle(card).position === 'static') {
      card.style.position = 'relative';
    }

    const a = document.createElement('a');
    a.className = 'card-person-link';
    a.href = personUrl(person.id);
    a.textContent = '↗';
    a.title = 'Open person page';
    a.addEventListener('click', e => e.stopPropagation());

    card.appendChild(a);
  });
}


function create(data) {
  const f3Chart = f3.createChart('#FamilyChart', data)
    .setTransitionTime(500)
    .setCardXSpacing(250)
    .setCardYSpacing(200)
    .setSingleParentEmptyCard(true, {label: 'Unknown'})

  f3Chart.setCardHtml()
      .setCardDisplay([d => d.data.label || '', d => d.data.desc || ''])
    //.setCardDisplay([["label",'desc']])
    .setCardDim({h:80})

  const chartEl = document.getElementById('FamilyChart');
  new MutationObserver(() => addPersonLinks(chartEl))
    .observe(chartEl, {childList: true, subtree: true});

  const mainPerson = data.find(node => node.main === true);
  if (mainPerson) {
    f3Chart.updateMainId(mainPerson.id);
  }

  f3Chart.updateTree({initial: true})

}