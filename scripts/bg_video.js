/**
 * bg_video.js -- Background video injection
 * ESG Provenance Auditor
 *
 * Injects a fullscreen looping video element directly onto the parent
 * document's <body>, bypassing Streamlit's stacking-context containers
 * that would otherwise trap a position:fixed element.
 *
 * Idempotent: checks for an existing #esg-bg element so Streamlit
 * script re-runs don't duplicate the video.
 *
 * Loaded via components.html() -- runs inside an iframe that can
 * access window.parent.document.
 */
(function () {
    var pd = window.parent.document;

    /* Run once only -- survives Streamlit re-runs */
    if (pd.getElementById("esg-bg")) return;

    /* ── CSS injected into the parent page head ── */
    var s = pd.createElement("style");
    s.id = "esg-bg-style";
    s.textContent = [
        "html{background:#040d1f!important}",
        "body{background:transparent!important}",
        "#root,.stApp,[data-testid='stAppViewContainer']",
        ",[data-testid='stAppViewContainer']>.main",
        ",[data-testid='stHeader']+div,[data-testid='stBottom']",
        ",.main,.block-container{background:transparent!important}",
        "#root{position:relative!important;z-index:1!important}",
        "#esg-bg{position:fixed;inset:0;z-index:0;overflow:hidden;pointer-events:none}",
        "#esg-vid{width:100%;height:100%;object-fit:cover;",
        "opacity:.35;filter:saturate(.6) brightness(.75)}",
        "#esg-veil{position:absolute;inset:0;background:linear-gradient(",
        "150deg,rgba(4,13,31,.45) 0%,rgba(4,13,31,.32) 5%,rgba(2,10,28,.50) 100%)}"
    ].join("");
    pd.head.appendChild(s);

    /* ── Video element prepended to body ── */
    var bg = pd.createElement("div");
    bg.id = "esg-bg";
    var vid = pd.createElement("video");
    vid.id = "esg-vid";
    vid.autoplay = true;
    vid.muted = true;
    vid.loop = true;
    vid.setAttribute("playsinline", "");
    var src = pd.createElement("source");
    src.src = window.parent.location.origin + "/app/static/bg-video.mp4";
    src.type = "video/mp4";
    vid.appendChild(src);
    var veil = pd.createElement("div");
    veil.id = "esg-veil";
    bg.appendChild(vid);
    bg.appendChild(veil);
    pd.body.insertBefore(bg, pd.body.firstChild);
    vid.play().catch(function(){});
})();
