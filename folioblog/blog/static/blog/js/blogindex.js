/**
 * Infinite scroll on Blog index page
 */
(() => {
    let grid = document.querySelector('#blog-index .grid');
    let filters = document.querySelector('#filters-dropdown');
    let infScroll;

    function getPath() {
        let href = '?ajax=1&page=' + (this.pageIndex + 1);
        let cat = document.querySelector('#filters-dropdown .active').getAttribute('data-filter');
        if (cat !== '*') {
            href = href.concat('&category=', cat.substring('category-'.length));
        }
        return href;
    }

    function refreshLayout() {
        infScroll.destroy(); // And yes, this is needed too!!
        initLayout();
    }

    function initLayout() {
        infScroll = new InfiniteScroll(grid, {
            path: getPath,
            append: '.grid-item',
            history: false,
            status: '.page-load-status',
            hideNav: '.pagination'
        });

        filters.addEventListener('click', function (event) {
            event.preventDefault();

            let url = '?ajax=1&page=1';
            let category = event.target.getAttribute('data-filter');
            if (category !== '*') {
                url = url + '&category=' + category.substring('category-'.length);
            }

            if (window.fetch) {
                fetch(url, {headers: new Headers({"X-Requested-With": "XMLHttpRequest"})})
                    .then(function (response) {
                        return response.text();
                    })
                    .then(function (html) {
                        grid.innerHTML = html;  // I know, very ugly way!
                        refreshLayout();

                        filters.querySelector('.active').classList.remove('active');
                        event.target.classList.add('active');
                    });
            } else {
                window.alert(gettext("Désolé, ce navigateur Web a bien besoin d'être mis à jour !"));
            }
        });
    }

    // Init layout only when document is fully loaded
    window.addEventListener('DOMContentLoaded', () => {
        if (grid && filters) {
            initLayout();
        }
    });
})();
