/**
 * Aucomplete and infinite scroll on search page
 */
(() => {
    let resultElem = document.querySelector('#search-results');
    let pagerElem = document.querySelector('#search-page .pagination');
    let queryElem = document.querySelector('#search-query');
    let tagInput = document.querySelector('#search-page [name=tags]');

    let infScroll;
    let autoCompleteJS;

    function initInfiniteScroll() {
        infScroll = new InfiniteScroll( resultElem, {
            path: '.page-next',
            append: '.search-results-item',
            status: '.page-load-status',
            hideNav: '.pagination'
        });
    }

    function initAutocomplete() {
        let autocompleteUrl = JSON.parse(document.getElementById('autocomplete-url').textContent);

        autoCompleteJS = new autoComplete({
            selector: () => {
                return queryElem;
            },
            wrapper: false,
            threshold: 3,
            debounce: 300,
            searchEngine: 'loose',  // or 'strict'
            data: {
                src: async (query) => {
                    try {
                        const source = await fetch(autocompleteUrl.replace('__QUERY__', query));
                        const data = await source.json();
                        return data;
                    } catch (error) {
                        return error;
                    }
                },
                keys: ['title']
            },
            resultsList: {
                class: 'list-group',
                destination: '#autocomplete-results',
                position: 'afterbegin',
                tabSelect: true,
                maxResults: 5
            },
            resultItem: {
                class: 'list-group-item fs-6',
                element: (item, data) => {
                    if (data.value.href) {
                        item.innerHTML = `
                            <button type="button" class="btn btn-link btn-sm text-black">${data.value.title}</button>
                             -
                            <a href="${data.value.href}">${gettext('voir')}</a>`;
                    }
                },
                selected: 'active',
            },
            events: {
                input: {
                    selection: (event) => {
                        const selection = event.detail.selection.value;
                        autoCompleteJS.input.value = selection.title;
                    }
                }
            }
        });
    }

    function initTagify() {
        let tagWhitelist = JSON.parse(document.getElementById('tags-options').textContent);
        let tagDefaults = JSON.parse(document.getElementById('tags-defaults').textContent);

        let tagify = new Tagify(tagInput, {
            whitelist: tagWhitelist,
            enforceWhitelist: true,
            autoComplete: {
                rightKey: true
            },
            dropdown: {
                enabled: 2,  // Minimum length for suggestions
                maxItems: 5,
                closeOnSelect : true,
                sortby: 'startsWith',
                position: 'all',
                highlightFirst: true
            },
            originalInputValueFormat: valuesArr => valuesArr.map(item => item.value).join(','),
            maxTags: 5,
            editTags: false,
            createInvalidTags: false
        });

        if (tagDefaults) {
            tagify.addTags(tagDefaults)
        }
    }

    window.addEventListener('DOMContentLoaded', () => {
        if (queryElem) {
            initAutocomplete();
        }
        if (tagInput) {
            initTagify();
        }
        if (resultElem && pagerElem) {
            initInfiniteScroll();
        }
    });
})();
