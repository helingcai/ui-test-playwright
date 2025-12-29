function show(id) {
    document.querySelectorAll('.card').forEach(e => e.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(e => e.classList.remove('active'));
    document.getElementById('attempt-' + id).classList.add('active');
    document.getElementById('tab-' + id).classList.add('active');
}

function togglePanel(id) {
    const panel = document.getElementById('panel-' + id);
    panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
}

/* 👇 页面加载完成后，自动展示最后一次失败的 Attempt */
window.onload = function () {
    show({{last_failed}});
}

function copyTraceCmd(button) {
    const cmd = document.getElementById('trace-cmd');

    navigator.clipboard.writeText(cmd.innerText).then(() => {
        //按钮状态
        const original = button.innerText;
        button.innerText = '✅ Copied';
        button.classList.add('copied');
        button.disabled = true;

        //命令闪光
        cmd.classList.add('flash');

        setTimeout(() => {
            button.innerText = original;
            button.classList.remove('copied');
            button.disabled = false;
            button.classList.remove('flash');
        }, 2000);
    }).catch(err => {
        alert('❌ Copy failed: ' + err);
    });
}