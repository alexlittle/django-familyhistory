const apiUrls = document.getElementById('api-urls').dataset;
const treeUrlBase = apiUrls.treeUrl;
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


  const mainPerson = data.find(node => node.main === true);
  if (mainPerson) {
    f3Chart.updateMainId(mainPerson.id);
  }

  f3Chart.updateTree({initial: true})

}