$(document).ready(function() {
	
	// Insert chevron icon if toggleable

	var chevron = '<span class="glyphicon glyphicon-chevron-down"></span>';
 
	$('.doclist.toggle').each(function() {
		$(this).find('.table_title').append(chevron);	
	});


	// Hide toggleable tables on page load depending on setting in cookies

	$.cookie.json = true;
	var cookie = $.cookie();

	$('.table_title').each(function() {
		var e = $(this);
		
		if ($.cookie(e.attr('id')) == false) {
			e.closest('.doclist.toggle').addClass('js-hidden');
		}
	});


	// Toggle toggleable tables on/off and save settings

	$('.table_title').click(function() {
		var e = $(this);
		var id = e.attr('id')

		var section = e.closest('.doclist.toggle').toggleClass('js-hidden');	

		var displayed = (section.hasClass('js-hidden')) ? false : true ;

		$.cookie(section_id, displayed, { expires: 7 });
	});


	// Allow user to click on any area in the .table row to access link

	$('tbody tr').click(function() {
		location.href = $(this).find('td a.doclink').attr('href');
	});  


	// Allow user to click on any area on homepage docselect to access link

	$('.docselect').click(function() {
		location.href = $(this).find('h3 a').attr('href');
	});  	        

});