var canvas;
var bg;
var ctx;
function tick() {
    bg.size = [canvas.getBoundingClientRect().width, canvas.getBoundingClientRect().height];
    bg.update(0.1);
    bg.draw(ctx);
}
window.onload = function() { // We initialise the variables in the onload function so it is asserted they exist in the website.
    canvas = document.getElementById("game_canvas");
    bg = new BG_Anxiety([canvas.getBoundingClientRect().width, canvas.getBoundingClientRect().height]);
    ctx = canvas.getContext("2d");
    setInterval(tick, 100);
    changeTheme(document.getElementById("themeSwitch").checked);
}

function changeTheme(newTheme) {
    bg.whiteMode = newTheme;
    document.body.style = 'color-scheme: ' + (newTheme ? 'light' : 'dark');
}

function start_long_task() {
    // send a POST request to start background job
    fetch('/longtask',{method: "POST"}).then(request => {
            update_progress('longtask');
        });
}

function update_progress(status_url) {
    // send GET request to status URL
    fetch("get_task/"+status_url).then(resp => {
        data = resp.json().then(function(data) {
            // update UI
            percent = parseInt(data.current * 100 / data.total);
            var elm = document.getElementById('progress');
            elm.innerHTML = percent + '%';
            var elm2 = document.getElementById('progressStatus');
            elm2.innerHTML = data.status;
            var elm3 = document.getElementById('progressState');
            elm3.innerHTML = data.state;
            if (data.state != 'FINISHED') {
                // rerun in 1 second
                setTimeout(function() {
                    update_progress(status_url);
                }, 1000);
            }
        })
    });
}