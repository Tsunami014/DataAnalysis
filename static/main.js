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

function updateCacheStatus() {
    fetch("cache_status?cache="+document.getElementById("Cache").checked.toString()+"&force="+document.getElementById("Force").checked.toString()).then(resp => {
        data = resp.text().then(function(data) {
            var elm = document.getElementById('CacheStatus');
            elm.innerHTML = "<h3 style='display: inline'>Cache Status:</h3><br>" + data;
        });
    });
}

function DeleteCache() {
    if(confirm('Are you sure you want to delete the cache?')) {
        fetch("delete_cache").then(resp => {updateCacheStatus();})
    }
}