$(document).ready(function() {
	
	$.cookie.json = true;
	var cookie = $.cookie();

	// for (var id in cookie) {

	$('.table_title').each(function(){
		var e = $(this);
		
		if ($.cookie(e.attr('id')) == false) {
			e.closest('.doclist').find('.table').addClass('js-hidden');
		}
	});

	$('tbody tr').click(function (){
		location.href = $(this).find('td a.doclink').attr('href');
	});          

	$('.table_title').click(function(){
		var e = $(this);
		var section_id = e.attr('id')

		var e_table = e.closest('.doclist').find('.table');
		
		e_table.toggleClass('js-hidden');

		var displayed = (e_table.hasClass('js-hidden')) ? false : true ;

		$.cookie(section_id, displayed, {
			expires: 7
		});
	
	console.log($.cookie());

	});


});