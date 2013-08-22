
// Date picker 
$(function() {
  $("#contact_date").datepicker();
  $("#disbursement_date").datepicker();
  $("#payment_date").datepicker();
  $("#contribution_date").datepicker();
  $("#gift_date").datepicker();
  $("#stamp_date").datepicker();
  $("#end_date").datepicker();

  //this is the search function, select2
  function createSelect(tag, resourse){
    
    $(tag).select2({
      minimumInputLength: 2,
      allowClear: true,
      
      query: function(query) {

        $.getJSON(resourse, {q: query.term}, function(results){
          // console.log(results);
            
            data = {
              results: results
            };
            // results is now set to [{id: "whatever", text: "whatever"}]

          query.callback(data);
        });
      }
    });
  }
  function createMSelect(tag, resourse){
    
    $(tag).select2({
      minimumInputLength: 2,
      allowClear: true,
      multiple: true,
      query: function(query) {

        $.getJSON(resourse, {q: query.term}, function(results){
          // console.log(results);
            
            data = {
              results: results
            };
            // results is now set to [{id: "whatever", text: "whatever"}]

          query.callback(data);
        });
      }
    });
  }

createMSelect("#contact_recip", "/formchoices/recip");
createMSelect("#client_client", "/formchoices/client");
createMSelect("#lobbyist_lobbyist", "/formchoices/lobbyist");
createSelect("#cont_recip", "/formchoices/recip");
createSelect("#client_location", "/formchoices/location");
createSelect("#disbursement_subcontractor", "/formchoices/reg");
createSelect("#payment_subcontractor", "/formchoices/reg");
createSelect("#gift_recip", "/formchoices/recip");

});


// This posts new client data without refreshing the page and updates the client choices

jQuery(document).ready(function() {
  var options = {
    success: function(responses, statusText, xhr, h){
      console.log(response)
      // var response.error = error
      // if ((error== 'name in system') ||(error== 'failed')){
      //   var message = "Error: " + error
      //   alert(message)
      // }  
      // else{
        //response is an array of JSON objects returned from the server
        for (var i=0; i<responses.length; i += 1) {
          var response = responses[i];

          var name = response.name;
          var id = response.id;

          // 1) update forms (I still need this even with select 2)
          var option = "<option value='" + id + "'>" + name + "</option>";
          $("#contact_client").append(option);
          $("#pay_client").append(option);
          $("#dis_client").append(option);
          $("#gift_client").append(option);
          $("#terminated_client").append(option);
          $("#ab_client").append(option);
      
          // 2) update list
          var item = "<li>" + name + "</li>"
          $("#client_list ul").append(item);

          // 3) clear form
          $('#clientform').each(function(){
              this.reset();   
          });
          $('#add_clientform').each(function(){
              this.reset(); 
          });

          // clears select2 boxes
          var $client_location = $('#client_location');
          $client_location.select2('data', null);
          var $location = $('#location');
          $location.select2('data', null);
          var $client_client = $('#client_client');
          $client_client.select2('data', null);

        }     
      //}
    }, 
    
    error: function(jqxhr, errorText, error){
        var message = "Error: " + error
        alert(message)
    },
  } 
  jQuery("#clientform").ajaxForm(options);
  jQuery("#add_clientform").ajaxForm(options);
   
  var contact_options = {
    success: function(responseText, statusText, xhr, h){

        update_option('<option value="{{ client.id }}">{{ client.client_name }}</option>', '#contactform', '#contact_client');
    } 
  }      
});


// <!-- This posts new lobbyist data without refreshing the page and updates the lobbyist choices -->

jQuery(document).ready(function(){
  function clearlselect(){
    var $lobbyist_lobbyist = $('#lobbyist_lobbyist');
    $lobbyist_lobbyist.select2('data', null);
    console.log("running")
  }
  var lobby_options = {
    success: function(responses, statusText, xhr, h){
      for (var i=0; i<responses.length; i += 1) {
        var response = responses[i];

        if (typeof response.error== 'undefined'){
          var name = response.name;
          var id = response.id;
          console.log(name)
          // 1) update forms (I still need this even with select 2)
          var option = "<option value='" + id + "'>" + name + "</option>";
          $("#contact_lobbyist").append(option);
          $("#cont_lobbyist").append(option);
      
          // 2) update list
          var item = "<li>" + name + "</li>";
          $("#lobby_list ul").append(item);

          // 3) clear form
          $('#lobbyform').each(function(){
              this.reset();   
          });
          $('#add_lobbyform').each(function(){
              this.reset(clearlselect());   
          });
        }

        else{
          var errors = response.error
          var message = "Error: " + errors
          alert(message)
        } 
      } 
    },
    error: function(jqxhr, errorText, error){
      var message = "Error: failed"
      alert(message)
    },
  }


jQuery("#lobbyform").ajaxForm(lobby_options);
jQuery("#add_lobbyform").ajaxForm(lobby_options);
 
var contact_options = {
    success: function(responseText, statusText, xhr, h){
      update_option('<option value="{{ client.id }}">{{ client.client_name }}</option>', '#contactform', '#contact_client');
    } 
  }     
});

// <!-- adding ajax  and updating-->

jQuery(document).ready(function(){

  function update(tag){

    var opt = {
      success: function(response, statusText, xhr, h){
        var error = response.error
        if (typeof error== 'undefined'){
          
          var no_clear = response.do_not_clear;
          if (no_clear == "on"){
                console.log("clear on")
          }
          else{
            $(tag).each(function(){
              this.reset();
            }); 
          }
          //3) update display
          console.log(response);

          if (tag == "#stampform"){
            var date = response.date;
            var id = response.id;
            var item = "<p>" + date + "</p>";
            console.log(item);
            $("#stamp_list").replaceWith(item);
          }

          if (tag == "#terminatedclientform"){
            for (var i=0; i<response.length; i += 1) {
              var responses = response[i];
              var name = responses.name;
              var id = responses.id;
              var item = "<li>" + name + "</li>";
            $("#terminated_client_list ul").append(item)
            }
          }

          if (tag == "#contactform"){
            var date = response.date;
            var name = response.name;
            var item = "<li>"+ name + " " + date + "</li>";
            $("#contact_list ul").append(item);
            var $contact_recip = $('#contact_recip');
            $contact_recip.select2('data', null)
          }

          if (tag == "#payform"){
            var amount = response.amount;
            var date = response.date;
            var client = response.client;
            var fee = response.fee;
            
            if (fee = "True"){
              fee = "fee"
            }
            else{
              fee = ""
            }
            
            var item = '<tr><td>$'+ amount + '</td><td>'+ client +'</td><td>'+ date +'</td><td>'+ fee +'</td></tr>';
            $('#pay_table').append(item);
            var $payment_subcontractor = $('#payment_subcontractor');
            $payment_subcontractor.select2('data', null);

          }

          if (tag == "#disform"){
            var amount = response.amount;
            var date = response.date;
            var client = response.client;

            item = '<tr><td>$'+ amount +'</td><td>'+ date + '</td><td>'+ client +'</td></tr>'
            $('#dis_table').append(item);
            var $disbursement_subcontractor = $('#disbursement_subcontractor');
            $disbursement_subcontractor.select2('data', null)
          }

          if (tag == '#contform'){
            var amount = response.amount;
            var lobbyist = response.lobbyist;
            var recipient = response.recipient;
            var date =  response.date;
            var cont_id = response.cont_id;

            var item = '<tr><td>$' + amount + '</td><td>' + lobbyist + '</td><td>'+ recipient +'</td><td>'+ date + '</td></tr>';
            $('#cont_table').append(item);
            var $cont_recip = $('#cont_recip');
            $cont_recip.select2('data', null)
          }
           
          if (tag == '#giftform'){
            var date = response.date;
            var client = response.client;
            var description = response.description;

            var item = '<li>' + description + " from " + client + " on " + date + '</li>'
            $('#gift_basket ul').append(item);
            var $gift_recip = $('#gift_recip');
            $gift_recip.select2('data', null) 
          }

          if (tag == '#descriptionform'){
            var description = response.description;
            var item =  '<p>Description: ' + description + '</p>';
            $('#discription_list').replaceWith(item);
          }

          if (tag == '#locationform'){
            var location = response.location;
            var item = '<p>' + location + ' added to locations </p>';
            $('#location_list').append(item);
          }
          if (tag == '#recipform'){
            var name = response.name;
            var item = '<p>Added: ' + name + '</p>';
            $('#reg_list').append(item);
          }
          if (tag == '#regform'){
            var name = response.name;
            var item = '<p>Added: ' + name + '</p>';
            $('#reg_list').append(item);
          }
          if (tag == '#client_infoform'){
            var client_type = response.client_type;
            var description = response.description;
            var item = '<p>Client type: '+ client_type + "</p><p>Description: " + description + '</p>';
            $('#ab_client_info').replaceWith(item);
          }

          if (tag == '.deleteable'){
            h.parent('div').remove();
          }
        }
        
        // creates error messages generated in views
        else{
          console.log("error")
          var message = "Error: " + response.error;
          alert(message);
        }  
      },

      // creates error messages 
      error: function( jqxhr, errorText, error){
        var message = "Error: " + error;
        alert(message);
      },
    }
    
    // 1) submit form
    $(tag).ajaxForm(opt);

  };

  update('#stampform');
  update('#terminatedclientform');
  update('#contactform');
  update('#recipform');
  update('#regform');
  update('#payform');
  update('#disform');
  update('#contform');
  update('#giftform');
  update('#descriptionform');
  update('#locationform');
  update('#client_infoform');
  update('#contact_remove_recip');
  update('#contact_remove_lobby');
  update('.deleteable');
  
});


// <!-- redirect after processing  -->

jQuery(document).ready(function() {

  var direct = {
      success: function(response, statusText, xhr, h){
           console.log(response);
           window.location.href="{% url 'entry-list' %}";
  }
}

$("#metaform").ajaxForm(direct);

});  

console.log("working")