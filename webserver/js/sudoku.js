$(document).ready(function(){
	$("p").each(function(index) {
		if($(this).text() == "") {
			$(this).hide();
		}
	});

	function validateRect(rect) {
		var arr = [],
		$this = $(rect),
		error = false;

		$this.children('.cell').each(function(){$(this).removeClass('rectError');});
		$this.children('.cell').each(function(){$(this).removeClass('rectCorrect');});

		$this.children().each(function(){
			var num = $(this).children('p').text();

			if (num == "") {
				arr.push(0);
			} else {
				arr.push(parseInt(num));
			}
		});

		var compareArray = [];
		for (var i = 0; i <= 8; i++) {
			if (($.inArray(arr[i], compareArray) != -1) && (arr[i] != 0)) {
				error = true;
				break;
			} else {
				compareArray.push(arr[i]);
			}
		}

		$this.children().each(function(){
			if (error) {
				$(this).addClass('rectError');
			} else {
				if ($.inArray(0, arr) != -1) {
					return;
				}
				$(this).addClass('rectCorrect');
			}
		});
	}

	function validateLine(i) {
		var arr = [],
			error = false;

		$('.cell[data-i='+i+']').each(function(){$(this).removeClass('lineError');});
		$('.cell[data-i='+i+']').each(function(){$(this).removeClass('lineCorrect');});

		$('.cell[data-i='+i+']').each(function(){
			var num = $(this).children('p').text();

			if (num == "") {
				arr.push(0);
			} else {
				arr.push(parseInt(num));
			}
		});

		var compareArray = [];
		for (var k = 0; k <= 8; k++) {
			if (($.inArray(arr[k], compareArray) != -1) && (arr[k] != 0)) {
				error = true;
				break;
			} else {
				compareArray.push(arr[k]);
			}
		}

		$('.cell[data-i='+i+']').each(function(){
			if (error) {
				$(this).addClass('lineError');
			} else {
				if ($.inArray(0, arr) != -1) {
					return;
				}
				$(this).addClass('lineCorrect');
			}
		});

	}

	function validateRow(j) {
		var arr = [],
			error = false;

		$('.cell[data-j='+j+']').each(function(){$(this).removeClass('rowError');});
		$('.cell[data-j='+j+']').each(function(){$(this).removeClass('rowCorrect');});

		$('.cell[data-j='+j+']').each(function(){
			var num = $(this).children('p').text();

			if (num == "") {
				arr.push(0);
			} else {
				arr.push(parseInt(num));
			}
		});
	
		

		var compareArray = [];
		for (var k = 0; k <= 8; k++) {
			if (($.inArray(arr[k], compareArray) != -1) && (arr[k] != 0)) {
				error = true;
				break;
			} else {
				compareArray.push(arr[k]);
			}
		}

		$('.cell[data-j='+j+']').each(function(){
			if (error) {
				$(this).addClass('rowError');
			} else {
				if ($.inArray(0, arr) != -1) {
					return;
				}
				$(this).addClass('rowCorrect');
			}
		});

	}

	function validation() {
		// Check the Rects:
		$('.rect').each(function(){
			validateRect($(this));
		});

		// Check the Lines:
		for (var i=0;i<9;i++) {
			validateLine(i);
		}

		// Check the Rows:
		for (var i=0;i<9;i++) {
			validateRow(i);
		}
		
	}

	$(".cell").click(function(){
		var $this = $(this),
			$p = $this.children('p'),
			$num;

		if ($this.hasClass('fixed')) {
			return;
		}
		
		if ($p.text() == "") {
			$num = 0;
		} else {
			$num = $p.text();
		}

		var num = parseInt($num) + 1;

		if (num == 10) {
			num = 0;
			$p.hide();
		} else {
			$p.show();
		}

		$p.text(num); 	

		validation();	
	});

	$("#upload").change(function() {
		$(this).parent().submit();
	});

	$("#solve").click(function() {
		$(this).parent().submit();
	});

	$("#new").click(function() {
		$(this).parent().submit();
	});

});