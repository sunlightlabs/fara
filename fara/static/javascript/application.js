$(document).ready(function() {
	

	// Hide toggleable tables on page load depending on setting in cookies

	$.cookie.json = true;
	var cookie = $.cookie();

	$('.table_title').each(function(){
		var e = $(this);
		
		if ($.cookie(e.attr('id')) == false) {
			e.closest('.doclist.toggle').find('.table').addClass('js-hidden');
		}
	});

	// Toggle toggleable tables on/off and save settings

	$('.table_title').click(function(){
		var e = $(this);
		var section_id = e.attr('id')

		var e_table = e.closest('.doclist.toggle').find('.table');
		
		e_table.toggleClass('js-hidden');

		var displayed = (e_table.hasClass('js-hidden')) ? false : true ;

		$.cookie(section_id, displayed, { expires: 7 });
	});


	// Allow user to click on any area in the .table row to access link

	$('tbody tr').click(function (){
		location.href = $(this).find('td a.doclink').attr('href');
	});  


	// Allow user to click on any area on homepage docselect to access link

	$('.docselect').click(function (){
		location.href = $(this).find('h3 a').attr('href');
	});  	        

});