/**
 * fingerprint.js — 浏览器指纹采集
 * 采集浏览器特征并上报到服务端。
 */

(function() {
    'use strict';

    function hash(str) {
        var h1 = 0xdeadbeef, h2 = 0x41c6ce57;
        for (var i = 0; i < str.length; i++) {
            var ch = str.charCodeAt(i);
            h1 = Math.imul(h1 ^ ch, 2654435761);
            h2 = Math.imul(h2 ^ ch, 1597334677);
        }
        h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507);
        h1 = Math.imul(h1 ^ (h1 >>> 13), 3266489909);
        h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507);
        h2 = Math.imul(h2 ^ (h2 >>> 13), 3266489909);
        return (h1 >>> 0).toString(16) + (h2 >>> 0).toString(16);
    }

    function getCanvasFingerprint() {
        try {
            var c = document.createElement('canvas');
            c.width = 280; c.height = 60;
            var ctx = c.getContext('2d');
            ctx.textBaseline = 'top';
            ctx.font = '14px "Arial"';
            ctx.fillStyle = '#f60';
            ctx.fillRect(10, 5, 50, 20);
            ctx.fillStyle = '#069';
            ctx.fillText('COD·陌', 2, 22);
            ctx.fillStyle = 'rgba(102,204,0,0.7)';
            ctx.fillText('CxO@!', 4, 40);
            ctx.strokeStyle = '#f0f';
            ctx.lineWidth = 1;
            ctx.arc(50, 30, 20, 0, Math.PI * 2, true);
            ctx.stroke();
            return hash(c.toDataURL());
        } catch (e) { return ''; }
    }

    function getWebGLFingerprint() {
        try {
            var c = document.createElement('canvas');
            var gl = c.getContext('webgl') || c.getContext('experimental-webgl');
            if (!gl) return '';
            var dbg = gl.getExtension('WEBGL_debug_renderer_info');
            var vendor = dbg ? gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL) : '';
            var renderer = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : '';
            return hash(vendor + '|' + renderer);
        } catch (e) { return ''; }
    }

    function getAudioFingerprint() {
        try {
            var ctx = new (window.OfflineAudioContext || window.webkitOfflineAudioContext)(1, 44100, 44100);
            var osc = ctx.createOscillator();
            var ana = ctx.createAnalyser();
            osc.type = 'triangle';
            osc.frequency.value = 10000;
            ana.fftSize = 256;
            osc.connect(ana);
            ana.connect(ctx.destination);
            osc.start(0);
            return ctx.startRendering ? '' : '';
        } catch (e) { return ''; }
    }

    function getFontFingerprint() {
        var base = ['monospace', 'sans-serif', 'serif'];
        var test = 'mmmmmmmmmmlli';
        var sizes = {};
        var c = document.createElement('canvas');
        var ctx = c.getContext('2d');
        for (var i = 0; i < base.length; i++) {
            ctx.font = '72px ' + base[i];
            sizes[base[i]] = ctx.measureText(test).width;
        }
        return hash(JSON.stringify(sizes));
    }

    function collect() {
        var nav = window.navigator;
        var screen = window.screen;

        var data = {
            userAgent: nav.userAgent,
            platform: nav.platform,
            language: nav.language,
            languages: JSON.stringify(nav.languages || []),
            cookieEnabled: nav.cookieEnabled,
            doNotTrack: nav.doNotTrack || 'unspecified',
            hardwareConcurrency: nav.hardwareConcurrency || 'unknown',
            deviceMemory: nav.deviceMemory || 'unknown',
            maxTouchPoints: nav.maxTouchPoints || 0,
            vendor: nav.vendor || '',
            screenW: screen.width,
            screenH: screen.height,
            colorDepth: screen.colorDepth,
            pixelRatio: window.devicePixelRatio || 1,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            timezoneOffset: new Date().getTimezoneOffset(),
            canvas: getCanvasFingerprint(),
            webgl: getWebGLFingerprint(),
            fonts: getFontFingerprint(),
            productSub: nav.productSub || '',
            appVersion: nav.appVersion || '',
            pdfViewer: !!nav.pdfViewerEnabled,
            webdriver: nav.webdriver || false,
            sessionStorage: !!window.sessionStorage,
            localStorage: !!window.localStorage,
            indexedDB: !!window.indexedDB,
            openDatabase: !!window.openDatabase,
            url: location.href,
            referrer: document.referrer || ''
        };

        data.fingerprint = hash(JSON.stringify(data));

        return data;
    }

    function send(data) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/fp', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        // 获取 XSRF token
        var xsrf = document.cookie.match(/"_xsrf"=([^;]+)/);
        if (xsrf) {
            xhr.setRequestHeader('X-XSRFToken', decodeURIComponent(xsrf[1]));
        }
        xhr.send(JSON.stringify(data));
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() { send(collect()); });
    } else {
        send(collect());
    }
})();
