/**
 * input_zone.js -- Merge input zone with hero card
 * ESG Provenance Auditor
 *
 * Walks up the DOM from Streamlit's file-uploader widget to the
 * nearest direct child of .block-container and applies the
 * .esg-input-zone CSS class. This visually merges the input area
 * (file upload + framework selector) with the hero card above it
 * into one continuous bordered panel.
 *
 * Uses a MutationObserver to re-apply after Streamlit re-renders.
 */
(function () {
    var pd = window.parent.document;

    function applyZone() {
        var blockContainer = pd.querySelector('.main .block-container');
        if (!blockContainer) return;
        var fileUploader = pd.querySelector('[data-testid="stFileUploader"]');
        if (!fileUploader) return;

        /* Walk up from the file uploader to a direct child of block-container */
        var el = fileUploader;
        while (el && el.parentElement !== blockContainer) {
            el = el.parentElement;
        }
        if (el && !el.classList.contains('esg-input-zone')) {
            el.classList.add('esg-input-zone');
        }
    }

    applyZone();
    setTimeout(applyZone, 300);

    var _t;
    new MutationObserver(function () {
        clearTimeout(_t);
        _t = setTimeout(applyZone, 80);
    }).observe(pd.body, { childList: true, subtree: true });
})();
