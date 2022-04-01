(() => {
    let lightbox = null;
    let pictureElem = document.querySelector('.page-image picture');

    // Main image
    let imageXS = pictureElem.getAttribute('data-image-first-xs');
    let imageLG = pictureElem.getAttribute('data-image-first-lg');

    // Alternative image (if any).
    let imageAltXS = pictureElem.getAttribute('data-image-second-xs');
    let imageAltLG = pictureElem.getAttribute('data-image-second-lg');

    function pictureToggle(event) {
        let sourceElem = pictureElem.querySelector('source');
        let imgElem = event.target;

        let current = pictureElem.getAttribute('data-image-current');
        let next = current === 'first' ? 'second': 'first';

        if (next === 'second') {
            sourceElem.setAttribute('srcset', imageAltXS);
            imgElem.setAttribute('src', imageAltLG);
        } else {
            sourceElem.setAttribute('srcset', imageXS);
            imgElem.setAttribute('src', imageLG);
        }
        pictureElem.setAttribute('data-image-current', next);
    }

    window.addEventListener('DOMContentLoaded', () => {
        lightbox = GLightbox();

        if (imageAltXS && imageAltLG) {
            // Init tooltip
            let tipElem = document.getElementById('image-switch-tooltip');
            new bootstrap.Tooltip(tipElem);
            // and bind click event to switch src
            pictureElem.addEventListener('click', pictureToggle);
        }
    });

})();
