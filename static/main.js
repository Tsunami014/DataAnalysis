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
    bg = new BG_Anxiety([canvas.getBoundingClientRect().width, canvas.getBoundingClientRect().height], true);
    ctx = canvas.getContext("2d");
    setInterval(tick, 100);
}