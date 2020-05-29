let stage = 'prepare';

const particles = [];

function lightSpeed(canvas) {
	let settings = {};
	settings.cameraMargin = settings.cameraMargin || 30;
	settings.starDensity = settings.starDensity || 0.003;
	settings.starSizes = settings.starSizes || [1, 4];
	settings.starLifeTime = settings.starLifeTime || 700;
	settings.canvasWidth = settings.canvasWidth || "100%";
	settings.canvasHeight = settings.canvasHeight || "500px";

	canvas.width = window.innerWidth;
	canvas.height = 500;

	// window.requestAnimationFrame(callback);

	let ctx = canvas.getContext("2d");
	ctx.clearRect(0, 0, canvas.width, canvas.height);


	let freeSpaceSize = canvas.width * canvas.height - Math.PI * settings.cameraMargin * settings.cameraMargin;
	console.log(freeSpaceSize);

	let starCount = freeSpaceSize * settings.starDensity;
	// starCount=10;


	var time = performance.now();
	for (let i = 0; i < starCount; i++) {
		let x = getRandomInt(0, canvas.width);
		let y = getRandomInt(0, canvas.height);

		if (Math.pow(Math.abs(x - canvas.width / 2), 2) + Math.pow(Math.abs(y - canvas.height / 2), 2) <= settings.cameraMargin * settings.cameraMargin) {
			i--;
			continue;
		}

		let size = getRandomInt(settings.starSizes[0], settings.starSizes[1]);
		particles.push({
			x: x,
			y: y,
			size: size,
			birth: time - getRandomInt(0, settings.starLifeTime - 1),
		});


		ctx.fillStyle = "blue";
		ctx.strokeStyle = 'blue';
		ctx.lineWidth = size;
		ctx.beginPath();
		// ctx.arc(x, y, size, 0, 2 * Math.PI);
		// ctx.fill();
		// ctx.strokeRect(x, y, 30, 30);
		// ctx.beginPath();
		ctx.moveTo(x, y);
		ctx.lineTo(x+1, y+1);
		ctx.stroke();

	}
}

function draw() {
	if (stage === 'prepare') {

	}
}

function getRandomInt(min, max) {
	min = Math.ceil(min);
	max = Math.floor(max);
	return Math.floor(Math.random() * (max - min)) + min; //The maximum is exclusive and the minimum is inclusive
}