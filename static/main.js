function onload() {
    document.getElementById("Cache").checked = true;
    document.getElementById("Force").checked = false;
    updateCacheStatus();
    load_BG();
}

function scrollDown() {
    setTimeout(function() {
        var area = document.getElementById('centreSection');
        area.scrollTop = area.scrollHeight;
    }, 100);
}

function file_status_check() {
    // send GET request to status URL
    fetch("status/get_files").then(resp => {
        data = resp.json().then(function(data) {
            var textarea = document.getElementById('FilesStatus');
            if ('txt' in data) {
                document.getElementById('FilesStatus').innerHTML = data.txt;// + "&#13;&#10;";
                textarea.scrollTop = textarea.scrollHeight;
            }
            if (data.State != 'FINISHED' && data.state != 'ERROR') {
                setTimeout(file_status_check, 500);
            } else {
                document.getElementById('FilesStatus').innerHTML = "Done!";
                textarea.scrollTop = textarea.scrollHeight;
                document.getElementById("FilesInfo").innerHTML = "<b>Status: </b>FILES STORED :)";
                document.getElementById('StoredStyle').innerHTML = "";
                select = document.getElementById('graphSelect');
                select.innetHTML = "";
                fetch('/get_names').then(resp => {
                    resp.json().then(function(data) {
                        for (i in data) {
                            var group = "";
                            for (j in data[i]) {
                                group += `<option value="${i}_${j}">${data[i][j]}</option>`
                            }
                            select.innerHTML += `<optgroup label="${i}">${group}</optgroup>`
                        }
                        graph(document.getElementById("graphSelect").value);
                    });
                });
                fetch('/plot_name_map')
                    .then(function(response) { return response.json(); })
                    .then(function(item) {
                        Bokeh.embed.embed_item(item);
                        scrollDown();
                    })
            }
        })
    });
}

function graph(value) {
    fetch('/plot/'+value.replace('_',"/"))
        .then(function(response) { return response.json(); })
        .then(function(item) {
            document.getElementById('myplot').innerHTML = "";
            Bokeh.embed.embed_item(item);
            scrollDown();
        })
}


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
