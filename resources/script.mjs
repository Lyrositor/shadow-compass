import Fuse from 'https://cdn.jsdelivr.net/npm/fuse.js@7.1.0/dist/fuse.basic.min.mjs'

window.onload = function () {
    const cardIllustrations = document.getElementById('card-illustrations')
    let cardIllustrationActive = 0

    function rotateCardIllustrations(event, step) {
        event.preventDefault()

        const numCardIllustrations = cardIllustrations.children.length;
        cardIllustrationActive = (cardIllustrationActive + step) % numCardIllustrations
        if (cardIllustrationActive < 0) {
            cardIllustrationActive += numCardIllustrations
        }
        for (let i = 0; i < numCardIllustrations; i++) {
            const cardIllustration = cardIllustrations.children[i]
            console.log(i, cardIllustrationActive)
            if (i === cardIllustrationActive) {
                cardIllustration.classList.add('open')
            } else {
                cardIllustration.classList.remove('open')
            }
        }
    }

    const cardIllustrationControlsLeft = document.getElementById('card-illustration-controls-left')
    if (cardIllustrationControlsLeft) {
        cardIllustrationControlsLeft.addEventListener('click', (event) => rotateCardIllustrations(event, -1))
    }
    const cardIllustrationControlsRight = document.getElementById('card-illustration-controls-right')
    if (cardIllustrationControlsRight) {
        cardIllustrationControlsRight.addEventListener('click', (event) => rotateCardIllustrations(event, 1))
    }

    const fuse = new Fuse(SEARCH_RESULTS, {ignoreDiacritics: true, keys: ['label', 'description']})
    const search = document.getElementById('search')
    const searchResults = document.getElementById('search-results')
    search.addEventListener('focusin', function () {
        if (search.value.length > 0) {
            searchResults.style.display = 'block'
        }
    })
    search.addEventListener('focusout', function (e) {
        if (e.relatedTarget != null && !e.relatedTarget.classList.contains('search-result')) {
            searchResults.style.display = 'none'
        }
    })
    search.addEventListener('input', function (e) {
        if (search.value.length === 0) {
            searchResults.style.display = 'none'
            return
        }
        searchResults.style.display = 'block'
        searchResults.innerHTML = '';
        const results = fuse.search(e.target.value, {limit: 5})
        for (const result of results) {
            const resultEntry = document.createElement('a')
            resultEntry.classList.add('search-result')
            resultEntry.href = `${ROOT_URL}${LANG}/${result.item.key}/`
            resultEntry.innerHTML = `${result.item.label}<br /><small>${result.item.description}</small>`
            searchResults.appendChild(resultEntry)
        }
    })
}