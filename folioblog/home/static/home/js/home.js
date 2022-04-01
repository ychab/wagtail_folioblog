/**
 * Glue code between youtube player and Flickity carousel
 */
(() => {
    let flktyPost = null;
    let flktyVideo = null;

    let carouselPost = document.querySelector('.carousel-posts');
    let carouselVideo = document.querySelector('.carousel-videos');

    let playerWrapper = document.querySelector('.video-youtube-player-wrapper');

    function initFlickityPost() {
        flktyPost = new Flickity(carouselPost, {
            imagesLoaded: true,
            percentPosition: true,
            wrapAround: true
        });
    }

    function initFlickityVideo() {
        flktyVideo = new Flickity(carouselVideo, {
            imagesLoaded: true,
            percentPosition: true,
            freeScroll: true,
            contain: true,
            pageDots: false
        });
    }

    function initVideosCarousel() {
        let links = carouselVideo.querySelectorAll('.carousel-video-item');
        for (let link of links) {
            link.addEventListener('click', function (event) {
                event.preventDefault();

                // First of all, update title element.
                let titleElem = document.querySelector('.video-title-link');
                titleElem.setAttribute('href', this.getAttribute('data-page-url'));
                titleElem.firstElementChild.textContent = this.getAttribute('data-page-title');

                // Then update wrapper attributes.
                let newVideoId = link.getAttribute('data-video-id');
                let oldVideoId = playerWrapper.getAttribute('data-video-id');
                playerWrapper.setAttribute('data-video-id', newVideoId);

                let playerThumbnail = document.querySelector('.video-youtube-thumbnail');
                // If player is not yet launched, update thumbnail for preview.
                if (playerThumbnail) {
                    let oldImg = playerThumbnail.querySelector('img');
                    let newImg = link.querySelector('img');
                    let newImgXs = link.getAttribute('data-img-xs-url');
                    let newImgLg = link.getAttribute('data-img-lg-url');
                    playerThumbnail.setAttribute('data-video-id', newVideoId);
                    oldImg.setAttribute('src', newImgXs);
                    oldImg.setAttribute('srcset', `${newImgLg} 700w, ${newImgXs} 940w`);
                    oldImg.setAttribute('alt', newImg.getAttribute('alt'));
                // Otherwise, player is running (or maybe broken) so just load the new video.
                } else {
                    // Destroy current player if any (video broken?)
                    if (oldVideoId in youtubePlayers) {
                        youtubePlayers[oldVideoId].destroy();
                        delete youtubePlayers[oldVideoId];
                    }
                    // Mark video as ready to be played
                    playerWrapper.setAttribute('data-ready-to-play', 1);
                    // Finally create a new player directly.
                    initYoutubeScript();
                }
            });
        }
    }

    window.addEventListener('DOMContentLoaded', () => {
        if (carouselPost) {
            initFlickityPost();
        }
        if (carouselVideo) {
            initFlickityVideo();
        }
        if (carouselVideo && playerWrapper) {
            initVideosCarousel();
        }
    });
})();
