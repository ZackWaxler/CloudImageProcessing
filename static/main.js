$(() => {
	let clouds = [];

	let canvas = document.getElementById('overlayCanvas');
	canvas.width = window.innerWidth;
	canvas.height = window.innerHeight;

	const anyBoxesChecked = () => {
		if ($(':checked').length !== 0) {
			return true;
		}

		return false;
	}

	$('#overlay-error').hide();

	$(window).resize((e) => {
		canvas.width = window.innerWidth;
		canvas.style.width = window.innerWidth;
		canvas.height = window.innerHeight;
		canvas.style.height = window.innerHeight;

		addAllClouds(clouds, 10);
	});

	// Display error message when no file is selected.
	$('form').submit((e) => {
		if (!$("form input[type=file]").val() || !anyBoxesChecked()) {
			e.preventDefault();

			let oldImageFormLabel = $('#image-form-label').text();
			let oldFilterFormLabel = $('#filter-form-label').text();

			if (!$("form input[type=file]").val()) { 
				$('#image-form-label').text('Error: No file chosen.');
			}

			if (!anyBoxesChecked()) {
				$('#filter-form-label').text('Error: No filters chosen.');
			}

			$('#overlay-error').fadeIn(750, () => {
				$('#overlay-error').fadeOut(500, () => {
					$('#image-form-label').text(oldImageFormLabel);
					$('#filter-form-label').text(oldFilterFormLabel);
				});
			});
		} 
	});

	let ctx = canvas.getContext('2d');

	let cloudImage = new Image();
	cloudImage.src = 'static/cloud.png';

	class Cloud {
		constructor() {
			const imageRatio = 1280 / 654;

			this.size = 100 + Math.random() * 75
			this.width = imageRatio * this.size;
			this.height = this.size;

			this.dir = (Math.random() > 0.5 ? 1 : -1);
			this.x = (this.dir === -1 ? canvas.width : -this.width)
			this.y = Math.random() * canvas.height;
			this.velocity = this.dir * (Math.random() + 1);
		}

		update(clouds, i) {
			this.x += this.velocity;

			if (this.outOfBounds()) {
				clouds.push(new Cloud());
				clouds.splice(i, 1);
			} 
		}

		draw(ctx) {
			ctx.drawImage(cloudImage, 0, 0, 1280, 654, this.x, this.y, this.width, this.height);
		}

		outOfBounds() {
			if (this.x + this.width < 0) {
				return true;
			} else if (this.x > canvas.width) {
				return true;
			} else {
				return false;
			}			
		}
	}

	const numClouds = 3;
	const FPS = 20;

	const addClouds = (num, time, clouds) => {
		setTimeout(function() {
			for (let i = 0; i < num; i++) {
				clouds.push(new Cloud());
			}			
		}, time);
	}

	const addAllClouds = (clouds, numBursts) => {
		if (clouds.length > 0) {
			clouds = [];
		}

		for (let i = 0; i < numBursts; i++) {
			addClouds(numClouds, 3500 * i, clouds);		
		}
	}

	addAllClouds(clouds, 10);

	let animationLoop = setInterval(() => {
		ctx.clearRect(0, 0, canvas.width, canvas.height);

		for (let i = 0; i < clouds.length; i++) {
			clouds[i].update(clouds, i);
			clouds[i].draw(ctx);
		}
	}, (1000 / FPS));
});
