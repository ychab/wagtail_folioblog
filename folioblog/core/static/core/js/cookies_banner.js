/**
 * Cookie banner
 */

// Global scope attributes to play with later.
let cookiesBanner = null;
let cookiesBannerAlert = null;

// Global scope function to accept cookies.
function cookiesBannerAccept(closeModal = false) {
    if (closeModal) {
        cookiesBannerAlert.close();
    }
    cookiesBanner.setConsent(true);
    cookiesBanner.launchFunction();
}

(() => {
    // Init cookie banner plugin
    cookiesBanner = new CookiesEuBanner(function () {
        // Called once cookies are accepted
        // Inject GA scripts
        bannerInitGoogleAnalytics(this);
        // If available, prepare video player (not loaded until user click)
        if (window.bannerInitYoutube !== undefined) {
            bannerInitYoutube();
        }
    }, true);

    // Ugly hack to also delete specific GA tracker!
    let ga_id = JSON.parse(document.getElementById('google-analytics-id').textContent);
    cookiesBanner.trackingCookiesNames.push('_ga_' + ga_id.replace('G-', ''));

    // Init alert JS banner
    let bannerElem = document.body.querySelector('#cookies-eu-banner');
    cookiesBannerAlert = bootstrap.Alert.getOrCreateInstance(bannerElem);

    // Bind close event banner to accept cookies (only if closed directly).
    bannerElem.addEventListener('closed.bs.alert', function() {
        if (!cookiesBanner.hasConsent()) {
            cookiesBannerAccept();
        }
    });
})();
