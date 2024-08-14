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

function Download() {
    fetch('/quicksave/download').then(resp => {
        document.getElementById("Load").disabled = false;

    });
}

function file_status_check() {
    // send GET request to status URL
    fetch("status/get_data").then(resp => {
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
                select = document.getElementById('GraphOpts');
                select.innetHTML = "";
                fetch('/stations').then(resp => {
                    resp.json().then(function(data) {
                        for (i in data) {
                            for (j in data[i]) {
                                select.innerHTML += `<option value="${i}_${j.padStart(6, '0')}">${data[i][j].padStart(6, '0')}</option>`
                            }
                        }
                    });
                });
                fetch('/stations/plot')
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
    fetch('/stations/plot/'+value.replace('_',"/"))
        .then(function(response) { return response.json(); })
        .then(function(item) {
            document.getElementById('myplot').innerHTML = "";
            Bokeh.embed.embed_item(item);
            scrollDown();
        })
}

function updateCacheStatus() {
    fetch("/cache?cache="+document.getElementById("Cache").checked.toString()+"&force="+document.getElementById("Force").checked.toString()).then(resp => {
        data = resp.text().then(function(data) {
            var elm = document.getElementById('CacheStatus');
            elm.innerHTML = "<h3 style='display: inline'>Cache Status:</h3><br>" + data;
        });
    });
}

function DeleteCache() {
    if(confirm('Are you sure you want to delete the cache?')) {
        fetch("/cache/delete").then(resp => {updateCacheStatus();})
    }
}

function checkGraphInp() {
    const currentValue = document.getElementById('graphSelect').value;
    document.getElementById("GraphConfirm").disabled =
        currentValue.length === 0 ||
        document.querySelector('option[value="' + currentValue + '"]') === null;
}
