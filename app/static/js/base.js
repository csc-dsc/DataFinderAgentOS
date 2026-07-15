/**
 * base.js — 瞭望与问数系统基础脚本
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('DataFinderAgentOS v0.2 已启动');

    // 渲染 COD·陌 水印
    var layer = document.getElementById('watermark');
    if (!layer) return;
    var text = 'COD·陌';
    var w = window.innerWidth;
    var h = window.innerHeight;
    var cols = Math.ceil(w / 200) + 2;
    var rows = Math.ceil(h / 100) + 2;
    var frag = document.createDocumentFragment();
    for (var r = 0; r < rows; r++) {
        for (var c = 0; c < cols; c++) {
            var span = document.createElement('span');
            span.textContent = text;
            span.style.left = (c * 200 - 40) + 'px';
            span.style.top  = (r * 100) + 'px';
            frag.appendChild(span);
        }
    }
    layer.appendChild(frag);
});
