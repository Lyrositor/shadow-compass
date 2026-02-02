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

    function hasParent(element, parent) {
        let currentElement = element
        while (currentElement && currentElement.parentNode) {
            if (currentElement === parent) {
                return true
            }
            currentElement = currentElement.parentNode
        }
        return false
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
        if (!hasParent(e.relatedTarget, searchResults)) {
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
        const results = fuse.search(e.target.value, {limit: 10})
        for (const result of results) {
            const row = document.createElement('div')
            row.classList.add('search-result')
            searchResults.appendChild(row)

            const link = document.createElement('a')
            link.href = `${ROOT_URL}${LANG}/${result.item.key}/`
            link.innerText = result.item.label
            row.appendChild(link)

            const description = document.createElement('small')
            description.innerText = result.item.description
            row.appendChild(description)
        }
    })
}