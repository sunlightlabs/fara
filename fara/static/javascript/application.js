$(document).ready(function() {
	

	// Insert chevron icon if toggleable

	var chevron = '<span class="glyphicon glyphicon-chevron-down"></span>';
 
	$('.doclist.toggle').each(function() {
		$(this).find('.table_title').append(chevron);	
	});


	// Hide toggleable tables on page load depending on setting in cookie

	$.cookie.json = true;
	var cookie = $.cookie();

	$('.table_title').each(function() {
		var e = $(this);
		
		if ($.cookie(e.attr('id')) == false) {
			e.closest('.doclist.toggle').addClass('js-hidden');
		}
	});


	// Toggle toggleable tables on/off and save settings to cookie

	$('.table_title').on('click', function() {
		var e = $(this);
		var id = e.attr('id')

		var section = e.closest('.doclist.toggle').toggleClass('js-hidden');	

		var displayed = (section.hasClass('js-hidden')) ? false : true ;

		$.cookie(id, displayed, { expires: 7 });
	});



	// Custom popup function for links

	var popup = function(linkClass) {
		$(document).on('click', linkClass, function(e){
			e.preventDefault();

			var url = $(this).attr('href');
			newPopup = window.open(url, 'name', 'width=550, height=750');
			
			if (window.focus) {
				newPopup.focus();
			}
			return false;			
		});
	}

	var popupClass = 'js-popup'; // Define the popup class
	var popupSelector = '.' + popupClass; // Define the popup selector

	popup(popupSelector); // Trigger popup on this selector



	// Allow user to click on any area in the .table row to access a link 

	$(document).on('click', '.table tbody tr', function() {

		if ($('td a', this).hasClass(popupClass)) { // If the link is a popup, create a popup window for it

			var url = $(popupSelector, this).attr('href');
			newPopup = window.open(url, 'name', 'width=550, height=750');
			
			if (window.focus) {
				newPopup.focus();
			}
			return false;	

		} else { // Otherwise redirect normally
			location.href = $('td .doclink', this).attr('href');
		}

	});  


	// Allow user to click inside .docselect on the homepage to access link

	$('.docselect').on('click', function() {
		location.href = $(this).find('h3 a').attr('href');
	});  	        

});





