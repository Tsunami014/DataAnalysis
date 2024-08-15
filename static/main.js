var loadingICO;
var lock = false;
var lockDesc = "";
var AITrained = "";
var dots = 0;

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

function trainAI() {
    if (!UpdateLock("Training AI")) {return;}
    Toast("We tooooooootaly trained an AI in half a millisecond. Aren't we so cool?");
    ReleaseLock();
}

function Download() {
    if (!UpdateLock("Downloading quick-save")) {return;}
    var thisLI = document.getElementById("downloadLoadingIco");
    thisLI.innerHTML = loadingICO;
    fetch('/quicksave/download').then(resp => {
        if (!resp.ok) {
            resp.json().then(function(data) {
                Toast("Error downloading quick-save: "+JSON.stringify(data), 2);
            }).catch(function() {
                Toast("Error downloading quick-save: Unknown reason.", 2);
            });
        }
        document.getElementById("Load").disabled = false;
        thisLI.innerHTML = "";
        ReleaseLock();
    });
}

function loadLI() {
    if (!UpdateLock("Loading quick-save")) {return;}
    var thisLI = document.getElementById("loadLoadingIco");
    thisLI.innerHTML = loadingICO;
    fetch('/quicksave/upload').then(resp => {
        if (!resp.ok) {
            resp.json().then(function(data) {
                Toast("Error restoring quick-save: "+JSON.stringify(data), 2);
            }).catch(function() {
                Toast("Error restoring quick-save: Unknown reason.", 2);
            });
        }
        document.getElementById("Load").disabled = false;
        thisLI.innerHTML = "";
        ReleaseLock();
    });
}

async function file_status_check() {
    // send GET request to status URL
    var data = await (await fetch("status/get_data")).json();
    var textarea = document.getElementById('FilesStatus');
    if ('txt' in data) {
        dots ++;
        if (dots > 3) {
            dots = 0;
        }
        var replacements = ["   ", ".  ", ".. ", "..."][dots];
        // Can use [. ]{3}\\.* if one day we want to use regex
        textarea.innerHTML = data.txt.replace("...", replacements);// + "&#13;&#10;";
        textarea.scrollTop = textarea.scrollHeight;
    }
    if (data.State == 'ERROR') {
        document.getElementById("FilesInfo").innerHTML = "<b>Status: </b>ERROR IN FILE HANDLING!";
        textarea.innerHTML = data.Error.toString();
        Toast("ERROR IN FILE PROCESSING! See file status panel for more info.", 2);
        return;
    }
    if (data.State != 'FINISHED') {
        setTimeout(file_status_check, 500);
    } else {
        textarea.innerHTML = "Done!";
        textarea.scrollTop = textarea.scrollHeight;
        document.getElementById("FilesInfo").innerHTML = "<b>Status: </b>FILES STORED :)";
        document.getElementById('StoredStyle').innerHTML = "";
        select = document.getElementById('GraphOpts');
        select.innerHTML = "";
        var data = await (await fetch('/stations')).json();
        for (let i in data) {
            for (let j in data[i]) {
                select.innerHTML += `<option value="${i}_${j.padStart(6, '0')}">${data[i][j].padStart(6, '0')}</option>`
            }
        }
        var item = (await fetch('/stations/plot')).json();
        Bokeh.embed.embed_item(item);
        scrollDown();
        ReleaseLock();
    }
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
