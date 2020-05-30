"use strict";

let stage = 'prepare';

const particles = [];
let startTime;

let settings = {};
settings.cameraMargin = settings.cameraMargin || 30;
settings.starDensity = settings.starDensity || 0.003;
settings.starSizes = settings.starSizes || [1, 4];
settings.starLifeTime = settings.starLifeTime || 700;
settings.canvasWidth = settings.canvasWidth || "100%";
settings.canvasHeight = settings.canvasHeight || "500px";
settings.velocity = settings.velocity || 2;

let targetCanvas;
let canvasHeight;
let canvasWidth;

function lightSpeed(canvas) {
	targetCanvas = canvas;
	// canvas.width = window.innerWidth;
	// canvas.height = 500;


	canvas.classList.remove('starting');
	canvas.innerHTML = '';

	// let ctx = canvas.getContext("2d");
	// ctx.clearRect(0, 0, canvas.width, canvas.height);
	//
	//
	canvasWidth = canvas.width.animVal.value;
	canvasHeight = canvas.height.animVal.value;

	let freeSpaceSize = canvasWidth * canvasHeight - Math.PI * settings.cameraMargin * settings.cameraMargin;
	console.log(freeSpaceSize);

	startTime = performance.now();
	let starCount = freeSpaceSize * settings.starDensity;
	starCount = 5;
	//
	//
	for (let i = 0; i < starCount; i++) {
		let x = getRandomInt(0, canvasWidth);
		let y = getRandomInt(0, canvasHeight);

		if (Math.pow(Math.abs(x - canvasWidth / 2), 2) + Math.pow(Math.abs(y - canvasHeight / 2), 2) <= settings.cameraMargin * settings.cameraMargin) {
			i--;
			continue;
		}

		let size = getRandomInt(settings.starSizes[0], settings.starSizes[1]);
		// particles.push({
		// 	x: x,
		// 	y: y,
		// 	size: size,
		// 	birth: ,
		// });

		let line = document.createElementNS("http://www.w3.org/2000/svg", 'line');
		line.setAttribute('stroke-width', size);
		line.setAttribute('x1', x);
		line.setAttribute('y1', y);
		line.setAttribute('x2', x);
		line.setAttribute('y2', y);
		line.setAttribute('birth', startTime - getRandomInt(0, settings.starLifeTime - 1));
		canvas.appendChild(line);
	}

	for (const p of particles) {

	}
	canvas.classList.add('starting');

	// window.requestAnimationFrame(draw);
}

function animateTrail(timeDiff) {
	let lines = targetCanvas.querySelectorAll('line');

	let centerX = canvasWidth / 2;
	let centerY = canvasHeight / 2;

	for (const line of lines) {
		let x1 = line.x1.animVal.value;
		let y1 = line.y1.animVal.value;

		let x2;
		let y2;
		if (x1 === centerX) {
			x2 = x1;
			y2 = y1 + timeDiff * settings.velocity;
		}
		else {
			let op1 = Math.sqrt(Math.pow(Math.abs(x1 - centerX), 2) + Math.pow(Math.abs(y1 - centerY), 2));
			let op2 = op1 + timeDiff * settings.velocity;

			x2 = op2 * (x1 - centerX) / op1 + centerX;
			y2 = op2 * (y1 - centerY) / op1 + centerY;
		}

		line.setAttribute('x2', x2);
		line.setAttribute('y2', y2);
	}
}

function draw() {
	let d = performance.now() - startTime;
	if (d < 1000) {
		animateTrail(10);

		// window.requestAnimationFrame(draw);
	}
}

function getRandomInt(min, max) {
	min = Math.ceil(min);
	max = Math.floor(max);
	return Math.floor(Math.random() * (max - min)) + min; //The maximum is exclusive and the minimum is inclusive
}