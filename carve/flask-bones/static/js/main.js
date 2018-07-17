d3.select('.phimages').on('click', function(){
	var mouse = d3.mouse(this);
	var bbox = this.getBoundingClientRect();

	var x = mouse[0] / bbox.width;
	var y = 1 - mouse[1] / bbox.height;


	var lat = coords[0][0] + x * (coords[0][1] - coords[0][0]);
	var lon = coords[1][0] + y * (coords[1][1] - coords[1][0]);

	var irow = Math.floor(x * ndvishp[0]);
	var icol = Math.floor(y * ndvishp[1]);

	var tndvi = ndvi[irow][icol];


	var label = d3.select('#ndvi-label');

	label.select('.lat').text(lat.toFixed(5));
	label.select('.lon').text(lon.toFixed(5));
	label.select('.ndvi').text(tndvi.toFixed(4));

	if(tndvi < 0.1) {
		label.select('.health').text('');
		label.style('background', 'black');
	}
	else if(tndvi < 0.3) {
		label.select('.health').text('poor');
		label.style('background', 'crimson');
	}
	else if(tndvi < 0.6) {
		label.select('.health').text('fair');
		label.style('background', 'darkorange');
	}
	else {
		label.select('.health').text('good');
		label.style('background', 'lime');
	}

	
});
