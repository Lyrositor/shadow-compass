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
}