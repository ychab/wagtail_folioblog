/**
 * Youtube players
 */

let youtubeInitScript = false;
let youtubePlayers = {};

function initYoutubeScript() {
    if (youtubeInitScript) {
        // If already loaded, mimic the behaviour by executing the callback manually.
        onYouTubeIframeAPIReady();
        return;
    }

    // Otherwise, create and insert script tag to load asynchronusly youtube js lib.
    let tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    let firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    // Of course, don't forgot to set the flag!
    youtubeInitScript = true;
}

function initYoutubePlayers() {

    let thumbnailElems = document.querySelectorAll('.video-youtube-thumbnail');
    for (let thumbnailElem of thumbnailElems) {
        let videoId = thumbnailElem.getAttribute('data-video-id');
        let playerWrapperElem = document.querySelector(`.video-youtube-player-wrapper[data-video-id="${videoId}"]`);
        // Wrapper is already ready??
        if (playerWrapperElem.getAttribute('data-click-bind')) {
            continue;  // Skip it!
        }
        // Otherwise, mark it as ready and bind button click.
        playerWrapperElem.setAttribute('data-click-bind', 1);

        // Bind click on thumbnail button to init and launch the player
        let button = thumbnailElem.querySelector('.youtube-player-button');
        button.addEventListener('click', function (event) {
            // Always check on the fly if changed
            if (cookiesBanner.hasConsent()) {
                // hara-kiri!
                thumbnailElem.remove();
                // Then mark player wrapper as ready to play.
                playerWrapperElem.setAttribute('data-ready-to-play', 1);
                // And finally init player!
                initYoutubeScript();
            }
        });
    }
}

// Global scope callback for banner when cookies are accepted.
function bannerInitYoutube() {
    let cookieConsentElems = document.querySelectorAll('.youtube-cookies-consent');
    for (let cookieConsentElem of cookieConsentElems) {
        cookieConsentElem.remove();
    }
}

// Default callback triggered by YT lib when it is ready (hardcoded funcname?)
function onYouTubeIframeAPIReady() {
    let playerWrapperElems = document.querySelectorAll(`.video-youtube-player-wrapper[data-ready-to-play="1"]`);

    // Build a player for each videos on the page.
    for (let playerWrapperElem of playerWrapperElems) {
        let videoId = playerWrapperElem.getAttribute('data-video-id');
        let width = playerWrapperElem.getAttribute('data-video-width');
        let height = playerWrapperElem.getAttribute('data-video-height');
        let lang = playerWrapperElem.getAttribute('data-video-lang');

        playerWrapperElem.style.display = 'block';

        // Create player div/iframe if it doesn't exists
        let playerElem = playerWrapperElem.firstElementChild;
        if (!playerElem) {
            playerElem = document.createElement('div');
            playerWrapperElem.appendChild(playerElem);
        }
        playerElem.id = `youtube-video-${videoId}`;

        // And finally, instanciate the player!
        youtubePlayers[videoId] = new YT.Player(playerElem.id, {
            videoId: videoId,
            width: width,
            height: height,
            playerVars: {
                hl: lang,
                modestbranding: 1,
                rel: 0,
                autoplay: 1  // Because we already click on thumbnail... let's go on!!
            }
        });

        // Finally remove marker to don't redo it!
        playerWrapperElem.removeAttribute('data-ready-to-play');
    }
}

(() => {
    initYoutubePlayers();
})();
