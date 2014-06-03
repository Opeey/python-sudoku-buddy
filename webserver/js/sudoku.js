$(document).ready(function(){
	$("p").each(function(index) {
		if($(this).text() == "") {
			$(this).hide();
		}
	});

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