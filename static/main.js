function start_long_task() {
    run_task('longtask', function(data) {
        // update UI
        percent = parseInt(data.current * 100 / data.total);
        var elm = document.getElementById('progress');
        elm.innerHTML = percent + '%';
        var elm2 = document.getElementById('progressStatus');
        elm2.innerHTML = data.status;
        var elm3 = document.getElementById('progressState');
        elm3.innerHTML = data.State;
        return true; // continue running
    });
}
