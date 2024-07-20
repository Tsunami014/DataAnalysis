/******************************

A cool floating-squares background, dark and light theme
Borrowed off of https://github.com/ncase/anxiety :)

******************************/

function BG_Anxiety(size, whiteMode){

	var self = this;

	self.whiteMode = whiteMode;

	// Moving white boxes
    self.size = size;
	self.boxes = [];
	self.resetBox = function(box, startInView){
		
		// Random size
		box.w = box.h = Math.random()*100 + 50;

		// Start in view?
		if(startInView){
			// Random position
			box.x = Math.random()*(self.size[0]+box.w*2) - box.w;
			box.y = Math.random()*(self.size[1]+box.h*2) - box.h;
		}

		// Move horizontal-only or vertical-only
		if(Math.random()<0.5){
			box.velX = (Math.random()>0.5 ? -1 : 1) * (Math.random()*0.8+0.2);
			box.velY = 0;
		}else{
			box.velX = 0;
			box.velY = (Math.random()>0.5 ? -1 : 1) * (Math.random()*0.8+0.2);
		}

		// If NOT start in view, use Velocity to determine where to put box
		if(!startInView){

			// Horizontal
			if(box.velY==0){
				box.y = Math.random()*(self.size[1]+box.h*2) - box.h;
				if(box.velX>0){ // ltr
					box.x = -box.w;
				}else{ // rtl
					box.x = self.size[0];
				}
			}

			// Vertical
			if(box.velX==0){
				box.x = Math.random()*(self.size[0]+box.w*2) - box.w;
				if(box.velY>0){ // utd
					box.y = -box.h;
				}else{ // dtu
					box.y = self.size[1];
				}
			}

		}

	};

	self.isBoxOutOfSight = function(box){
		if(box.x < -box.w) return true;
		if(box.y < -box.h) return true;
		if(box.x > self.size[0]) return true;
		if(box.y > self.size[1]) return true;
		return false;
	};

	self.updateBox = function(box, delta){
		// Move it
		const speedMultiplier = 60;
		box.x += box.velX * delta * speedMultiplier;
		box.y += box.velY * delta * speedMultiplier;

		// If it's out of sight, reset it
		if(self.isBoxOutOfSight(box)) self.resetBox(box);
	};
	
	var boxLayerAlpha = 1;
	self.updateAlpha = function(alpha){
		boxLayerAlpha = alpha;
	};

	self.update = function(delta){
		for(const box of self.boxes) self.updateBox(box, delta);
	};

	self.drawBox = function(box, ctx){
		ctx.fillRect(box.x, box.y, box.w, box.h);
	};

	self.draw = function(ctx){

		// A big ol' black box
		ctx.fillStyle = self.whiteMode ? "#dddddd" : "#111111";
		ctx.fillRect(0,0, self.size[0], self.size[1]);

		// Moving white boxes
		ctx.globalAlpha = boxLayerAlpha * (self.whiteMode ? 0.11 : 0.03);
		ctx.fillStyle = "#fff";
		for(const box of self.boxes) self.drawBox(box, ctx);
		ctx.globalAlpha = 1;

	};

	for(var i=0; i<80; i++){
		var box = {};
		self.resetBox(box, true);
		self.boxes.push(box);
	}
}

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