/**
 * Packery on Gallery page
 */
(() => {
    let grid = document.querySelector('#gallery-packery .grid');
    let filterElem = document.querySelector('#gallery-filters');
    let buttonShuffle = document.querySelector('#button-shuffle');

    let pckry = null;
    let lightbox = null;

    function initPackery() {
        pckry = new Packery(grid, {
            columnWidth: '.grid-sizer',
            gutter: '.gutter-sizer',
            itemSelector: '.grid-item',
            percentPosition: true
        });
        toggleZoomFeature();
    }

    function initGLightbox() {
        lightbox = GLightbox({loop: true});
    }

    function bindDragFeature() {
        let formElem = document.querySelector('#grid-button-action');
        let toogleDrag = formElem.querySelector('#draggable-switch');

        let draggies = [];
        toogleDrag.addEventListener('change', function () {
            if (this.checked) {
                draggies = [];
                pckry.getItemElements().forEach(function (itemElem) {
                    let draggie = new Draggabilly(itemElem);
                    pckry.bindDraggabillyEvents(draggie);
                    draggies.push(draggie);
                    itemElem.classList.add('is-draggable');
                });
            } else {
                for (let draggie of draggies) {
                    draggie.disable();  // pckry.unbindDraggabillyEvents(draggie) is not enough
                    draggie.element.classList.remove('is-draggable');
                }
            }
        });
    }

    function toggleZoomFeature() {

        function replaceIcon(zoomButton, iconElem, is_plus) {
            let newIconElem = document.createElement('i');
            newIconElem.classList.add("fa-solid");
            newIconElem.classList.add("fa-magnifying-glass-" + (is_plus ? 'plus': 'minus'));
            zoomButton.appendChild(newIconElem);
            iconElem.remove();
        }

        let zoomButtons = grid.querySelectorAll('.grid-item-zoom-button');
        for (let zoomButton of zoomButtons) {

            zoomButton.addEventListener('click', function (event) {
                let iconElem = zoomButton.querySelector('svg');
                let gridItemElem = event.target.closest('.grid-item');
                gridItemElem.classList.toggle('grid-item--width2');

                if (gridItemElem.classList.contains('grid-item--width2')) {
                    replaceIcon(zoomButton, iconElem, false);
                    updatePicture(gridItemElem, true);
                    pckry.fit(gridItemElem);
                } else {
                    replaceIcon(zoomButton, iconElem, true);
                    updatePicture(gridItemElem);
                    pckry.shiftLayout();
                }
            });
        }
    }

    function updatePicture(gridItemElem, zoom=false) {
        let elems = {
            lg: gridItemElem.querySelector('picture source'),
            xs: gridItemElem.querySelector('picture img'),
        };

        for (let device in elems) {
            let elem = elems[device];
            let prefix = 'data-img-' + (zoom ? 'zoom-' : '') + device;
            let attrSrc = device === 'lg' ? 'srcset' : 'src';

            elem.setAttribute(attrSrc, elem.getAttribute(prefix));
            elem.setAttribute('width', elem.getAttribute(`${prefix}-width`));
            elem.setAttribute('height', elem.getAttribute(`${prefix}-height`));
        }
    }

    function bindShuffle() {
        buttonShuffle.addEventListener('click', function(event) {
            // Randomly reorder items.
            // @see https://github.com/metafizzy/packery/issues/312
            let m = pckry.items.length, t, i;
            while (m) {
                i = Math.floor(Math.random() * m--);
                t = pckry.items[m];
                pckry.items[m] = pckry.items[i];
                pckry.items[i] = t;
            }
            pckry.layout();
        });
    }

    function bindFilters() {
        let links = filterElem.querySelectorAll('a.dropdown-item');
        for (let link of links) {

            link.addEventListener('click', function (event) {
                event.preventDefault();

                let url = link.getAttribute('href');
                if (window.fetch) {
                    fetch(url, {headers: new Headers({"X-Requested-With": "XMLHttpRequest"})})
                        .then(function (response) {
                            return response.text();
                        })
                        .then(function (html) {
                            // Update the DOM with fresh HTML!
                            let gridItems = grid.querySelector('.grid-items');
                            grid.removeChild(gridItems);
                            grid.insertAdjacentHTML('beforeend', html);

                            // Reload and attach behaviours
                            pckry.reloadItems();
                            pckry.layout();
                            toggleZoomFeature();
                            lightbox.reload();

                            // Finally mark filter as active
                            filterElem.querySelector('a.dropdown-item.active').classList.remove('active');
                            link.classList.add('active');
                        });
                } else {
                    window.alert(gettext("Oula, ce navigateur Web a bien besoin d'être mis à jour !"));
                }
            });
        }
    }

    window.addEventListener('DOMContentLoaded', () => {
        if (grid && buttonShuffle && filterElem) {
            initPackery();
            bindDragFeature();
            bindShuffle();
            bindFilters();
            initGLightbox();
        }
    });
})();
