var loadingICO;
var lock = false;
var lockDesc = "";

function onload() {
    document.getElementById("Cache").checked = true;
    document.getElementById("Force").checked = false;
    document.getElementById("graphSelect").addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            e.preventDefault();
            checkGraphInp();
            var btn = document.getElementById("GraphConfirm");
            if (!btn.disabled) {
                btn.click();
            }
        }
    });
    loadingICO = document.getElementById("LoadingToCopy").innerHTML;
    updateCacheStatus();
    updateTheme();
    load_BG();
}

function Toast(text, type=0) {
    // type 0 = normal, 1 = warn, 2 = error
    var toast = document.createElement('div');
    toast.classList.add('toast');
    if (type === 1) {
        toast.classList.add('warnToast');
    } else if (type === 2) {
        toast.classList.add('errorToast');
    }
    toast.innerText = text;
    document.body.appendChild(toast);
    setTimeout(function() { // Give it enough time to relax so it can animate
        toast.style.opacity = 1;
        toast.style.bottom = '30px';
        setTimeout(function() {
            toast.style.opacity = 0;
            toast.style.bottom = '10px';
            setTimeout(function() {
                document.body.removeChild(toast);
            }, 500);
        }, 3000);
    }, 10);
}

function UpdateLock(desc) {
    if (lock) {
        Toast(`Lock is set - "${lockDesc}" is in progress. Please wait for that to finish before continuing.`, 1);
        return false;
    }
    lock = true;
    lockDesc = desc;
    return true;
}

function ReleaseLock() {
    lock = false;
    lockDesc = "";
}

function updateTheme() {
    var cnt;
    if (document.getElementById("themeSwitch").checked) {
        cnt = "'☀'";
    } else {
        cnt = "'☾'";
    }
    document.getElementById("ThemeSwitchPar").children[1].style.setProperty('--content', cnt)
}

function toggleSide() {
    var side = document.getElementById('Side');
    if (side.classList.contains('closed')) {
        openSide()
    } else if (side.classList.contains('opened')) {
        closeSide()
    }
}

function openSide() {
    var side = document.getElementById('Side');
    side.classList.remove('closed', 'opened');
    side.style.width = '0';
    side.style.display = 'block';
    setTimeout(function() {
        side.style.width = '650px';
        setTimeout(function() {
            side.classList.add('opened');
        }, 500);
    }, 10);
}

function closeSide() {
    var side = document.getElementById('Side');
    side.classList.remove('closed', 'opened');
    side.style.width = '0';
    setTimeout(function() {
        side.style.display = 'none';
        side.classList.add('closed');
    }, 500);
}

function scrollDown() {
    setTimeout(function() {
        var area = document.getElementById('DownloadSelectSection');
        area.scrollTop = area.scrollHeight;
    }, 100);
}

function Download() {
    if (!UpdateLock("Downloading quick-save")) {return;}
    var thisLI = document.getElementById("downloadLoadingIco");
    thisLI.innerHTML = loadingICO;
    fetch('/quicksave/download').then(resp => {
        document.getElementById("Load").disabled = false;
        thisLI.innerHTML = "";
        ReleaseLock();
    });
}

function loadLI() {
    if (!UpdateLock("Loading quick-save")) {return true;}
    document.getElementById("loadLoadingIco").innerHTML = loadingICO;
    return false;
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
                        ReleaseLock();
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
            openSide();
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
