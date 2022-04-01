/**
 * Google Analytics integration.
 */

function bannerInitGoogleAnalytics() {
    let ga_id = JSON.parse(document.getElementById('google-analytics-id').textContent);

    let tag = document.createElement('script');
    tag.src = `https://www.googletagmanager.com/gtag/js?id=${ ga_id }`;

    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    window.dataLayer = window.dataLayer || [];
    function gtag() {
        dataLayer.push(arguments);
    }
    gtag('js', new Date());
    gtag('config', ga_id);
}
