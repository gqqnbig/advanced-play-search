"use strict";

let stage = 'prepare';

const particles = [];
let startTime;

let settings = {};
settings.cameraMargin = settings.cameraMargin || 30;
settings.starDensity = settings.starDensity || 0.0025;
settings.starSizes = settings.starSizes || [1, 4];
settings.starLifeTime = settings.starLifeTime || 700;
settings.canvasWidth = settings.canvasWidth || "100%";
settings.canvasHeight = settings.canvasHeight || "500px";
settings.velocity = settings.velocity || 1;
settings.startDuration = settings.startDuration || 2000;

let targetCanvas;
let canvasHeight;
let canvasWidth;

function timingQuad(timeFraction) {
	return Math.pow(timeFraction, 5)
}

function spawnStar(birthDate, classes) {
	while (true) {
		let x = getRandomInt(0, canvasWidth);
		let y = getRandomInt(0, canvasHeight);

		if (Math.pow(Math.abs(x - canvasWidth / 2), 2) + Math.pow(Math.abs(y - canvasHeight / 2), 2) <= settings.cameraMargin * settings.cameraMargin) {
			continue;
		}

		let size = getRandomInt(settings.starSizes[0], settings.starSizes[1]);

		let line = document.createElementNS("http://www.w3.org/2000/svg", 'line');
		line.setAttribute('stroke-width', size);
		line.setAttribute('x1', x);
		line.setAttribute('y1', y);
		line.setAttribute('x2', x);
		line.setAttribute('y2', y);
		line.setAttribute('birth', birthDate);
		if (classes && classes.length > 0)
			line.classList.add(...classes);
		targetCanvas.appendChild(line);
		break;
	}
}

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
	// starCount = 1;
	//
	//
	for (let i = 0; i < starCount; i++) {
		spawnStar(startTime - getRandomInt(0, settings.starLifeTime * 4), ['initial']);
	}
	canvas.classList.add('starting');

	window.requestAnimationFrame(draw);
}

function animateTrail() {
	let now = performance.now();
	let timeDiff = now - startTime;
	let lines = targetCanvas.querySelectorAll('line');

	let centerX = canvasWidth / 2;
	let centerY = canvasHeight / 2;


	let velocityProgress = timingQuad(timeDiff / settings.startDuration) / timingQuad(1);
	let currentVelocity = velocityProgress * settings.velocity;

	let diedStars = 0;
	for (const line of lines) {
		if (parseInt(line.getAttribute('birth')) + settings.starLifeTime / velocityProgress < now) {
			targetCanvas.removeChild(line);
			spawnStar(now);
			diedStars++;
		}
		else {

			let x1 = line.x1.animVal.value;
			let y1 = line.y1.animVal.value;

			let x2;
			let y2;
			if (x1 === centerX) {
				x2 = x1;
				if (y1 > centerY)
					y2 = y1 + timeDiff * currentVelocity;
				else
					y2 = y1 - timeDiff * currentVelocity;
			}
			else {
				let op1 = Math.sqrt(Math.pow(Math.abs(x1 - centerX), 2) + Math.pow(Math.abs(y1 - centerY), 2));
				let op2 = op1 + timeDiff * currentVelocity;

				x2 = op2 * (x1 - centerX) / op1 + centerX;
				y2 = op2 * (y1 - centerY) / op1 + centerY;
			}

			line.setAttribute('x2', x2);
			line.setAttribute('y2', y2);
		}
	}
	console.log('diedStars=' + diedStars);
}

function draw() {
	let d = performance.now() - startTime;
	if (d < settings.startDuration) {
		animateTrail();

		window.requestAnimationFrame(draw);
	}
}

function getRandomInt(min, max) {
	min = Math.ceil(min);
	max = Math.floor(max);
	return Math.floor(Math.random() * (max - min)) + min; //The maximum is exclusive and the minimum is inclusive
}