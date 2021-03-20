$(function() {
	var clouds = [];

	var canvas = document.getElementById('overlayCanvas');
	canvas.width = window.innerWidth;
	canvas.height = window.innerHeight;

	$('#overlay-error').hide();

	$(window).resize(function(e) {
		canvas.width = window.innerWidth;
		canvas.style.width = window.innerWidth;
		canvas.height = window.innerHeight;
		canvas.style.height = window.innerHeight;

		addAllClouds(clouds, 10);
		console.log('resized')
	});

	// Display error message when no file is selected.
	$('form').submit(function(e) {
		if (!$("form input[type=file]").val()) {
			e.preventDefault();
			var oldText = $('#image-form-label').text();
			$('#image-form-label').text('Error: No file chosen.');
			$('#overlay-error').fadeIn(1000, function() {
				$('#overlay-error').fadeOut(600, function() {
					$('#image-form-label').text(oldText);
				});
			});
		}
	});

	var ctx = canvas.getContext('2d');

	var cloudImage = new Image();
	cloudImage.src = 'static/cloud.png';

	var Cloud = function() {
		var imageRatio = 1280 / 654;

		this.size = 100 + Math.random() * 75
		this.width = imageRatio * this.size;
		this.height = this.size;

		this.dir = (Math.random() > 0.5 ? 1 : -1);
		this.x = (this.dir === -1 ? canvas.width : -this.width)
		this.y = Math.random() * canvas.height;
		this.velocity = this.dir * (Math.random() + 1);
	}

	Cloud.prototype.update = function(clouds, i) {
		this.x += this.velocity;

		if (this.outOfBounds()) {
			clouds.push(new Cloud());
			clouds.splice(i, 1);
		} 
	}

	Cloud.prototype.draw = function(ctx) {
		ctx.drawImage(cloudImage, 0, 0, 1280, 654, this.x, this.y, this.width, this.height);
	}

	Cloud.prototype.outOfBounds = function() {
		if (this.x + this.width < 0) {
			return true;
		} else if (this.x > canvas.width) {
			return true;
		} else {
			return false;
		}
	}

	var numClouds = 3;
	var FPS = 20;

	var addClouds = function(num, time, clouds) {
		setTimeout(function() {
			for (var i = 0; i < num; i++) {
				clouds.push(new Cloud());
			}			
		}, time);
	}

	var addAllClouds = function(clouds, numBursts) {
		if (clouds.length > 0) {
			clouds = [];
		}

		for (var i = 0; i < numBursts; i++) {
			addClouds(numClouds, 3500 * i, clouds);		
		}
	}

	addAllClouds(clouds, 10);

	var animationLoop = setInterval(function() {
		ctx.clearRect(0, 0, canvas.width, canvas.height);

		for (var i = 0; i < clouds.length; i++) {
			clouds[i].update(clouds, i);
			clouds[i].draw(ctx);
		}
	}, (1000 / FPS));
});
