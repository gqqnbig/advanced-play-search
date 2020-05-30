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
settings.stopVelocity = settings.stopVelocity || 2;

settings.startDuration = settings.startDuration || 2000;
settings.stopDuration = settings.stopDuration || 2000;

let targetCanvas;
let canvasHeight;
let canvasWidth;
let desiredStarCount;
let lastTick;
let stopRequestTime;

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

function enterLightSpeed(canvas) {
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
	desiredStarCount = freeSpaceSize * settings.starDensity;
	// desiredStarCount = 5;
	//
	//
	for (let i = 0; i < desiredStarCount; i++) {
		spawnStar(startTime - getRandomInt(0, settings.starLifeTime * 4), ['initial']);
	}
	canvas.classList.add('starting');
	lastTick = startTime;

	window.requestAnimationFrame(draw);
}

function animateTrail(now, velocityProgress) {
	let lines = targetCanvas.querySelectorAll('line');

	let centerX = canvasWidth / 2;
	let centerY = canvasHeight / 2;

	let currentVelocity = velocityProgress * settings.velocity;

	let diedStars = 0;
	for (const line of lines) {
		let birth = parseInt(line.getAttribute('birth'));
		if (birth + settings.starLifeTime / velocityProgress < now) {
			targetCanvas.removeChild(line);
			diedStars++;
		}
		else {

			let x1 = line.x1.animVal.value;
			let y1 = line.y1.animVal.value;

			let timeDiff = now - lastTick;
			let x2 = line.x2.animVal.value;
			let y2 = line.y2.animVal.value;
			if (x1 === centerX) {
				x2 = x1;
				if (y1 > centerY)
					y2 = y2 + timeDiff * currentVelocity;
				else
					y2 = y2 - timeDiff * currentVelocity;
			}
			else {
				let op2 = Math.sqrt(Math.pow(Math.abs(x2 - centerX), 2) + Math.pow(Math.abs(y2 - centerY), 2));
				let op3 = op2 + timeDiff * currentVelocity;

				x2 = op3 * (x2 - centerX) / op2 + centerX;
				y2 = op3 * (y2 - centerY) / op2 + centerY;
			}

			line.setAttribute('x2', x2);
			line.setAttribute('y2', y2);
		}
	}

	let addStarCount = 0;
	let spawnProbability = Math.max(0.1, 1 - (lines.length - diedStars) / desiredStarCount);
	addStarCount = spawnProbability * (desiredStarCount - (lines.length - diedStars));
	for (let i = 0; i < addStarCount; i++)
		spawnStar(now);


	console.log(`diedStars=${diedStars}, new stars=${addStarCount}`);
}

function animateTrailStopping(now, velocityProgress) {
	let lines = targetCanvas.querySelectorAll('line');

	let centerX = canvasWidth / 2;
	let centerY = canvasHeight / 2;

	let currentVelocity = velocityProgress * settings.velocity;

	let diedStars = 0;
	for (const line of lines) {
		let birth = parseInt(line.getAttribute('birth'));
		if (birth + settings.starLifeTime / velocityProgress < now) {
			targetCanvas.removeChild(line);
			diedStars++;
		}
		else {

			let x1 = line.x1.animVal.value;
			let y1 = line.y1.animVal.value;

			let timeDiff = now - Math.max(birth, startTime);
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

	console.log(`diedStars=${diedStars}, new stars=${addStarCount}`);
}


function draw() {
	let now = performance.now();
	if (targetCanvas.classList.contains('stopping')) {
		let d = now - stopRequestTime;
		animateTrailStopping(now, 1 - timingQuad(d / settings.stopDuration) / timingQuad(1))
	}
	else {
		let d = now - startTime;
		if (d < settings.startDuration) {
			animateTrail(now, timingQuad(d / settings.startDuration) / timingQuad(1));
		}
		else //if (d < 10000)
		{
			if (!targetCanvas.classList.contains('running'))
				targetCanvas.classList.add('running');
			animateTrail(now, 1);
		}
		lastTick = now;
		window.requestAnimationFrame(draw);
	}
}

function getRandomInt(min, max) {
	min = Math.ceil(min);
	max = Math.floor(max);
	return Math.floor(Math.random() * (max - min)) + min; //The maximum is exclusive and the minimum is inclusive
}

function exitLightSpeed() {
	targetCanvas.classList.add('stopping');
	stopRequestTime = performance.now();

}