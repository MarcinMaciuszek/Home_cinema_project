//$(".seat_info").hide();

//$(".seat").on('mouseenter', ()=>{
//  var content = "Wolne";
//  content = $(this).attr('content');
//  console.log(content);
//  $(".seat_info").html(content);
//  $(".seat_info").show();
//
//})
//
//$(".seat").on('mouseleave', ()=>{
//  $(".seat_info").hide();
//})

$(document).ready(function() {
    if($(".taken_place_banner").length){
        $('.seats_wrapper').find('a').removeAttr('href');
        $('.seat_label_empty').css({'cursor': 'default'});
    }
});

$(".seat").on({
    mouseenter: function () {
        console.log($(this).attr('content'))
        console.log($('.user_name').attr('content'))
        if ($(this).attr('content') == $('.user_name').attr('content'))
        {
            console.log(2)
            var message = "Twoje miejsce !";
            var div_name = ".seat_label_user_taken";
            var background_color = $(div_name).css('background-color');
            var color = $(div_name).css('color');
        }
        else if ($(this).attr('content') != 'None')
        {
            console.log(1)
            var message = $(this).attr('content');
            var div_name = ".seat_label_taken";
            var background_color = $(div_name).css('background-color');
            var color = $(div_name).css('color');
        }
        else
        {
            console.log(3)
            var message = "Wolne !";
            var div_name = ".seat_label_empty";
            var background_color = $(div_name).css('background-color');
            var color = $(div_name).css('color');
        }
        var place = $(this).text();
        var result_message = "Miejsce " + place + ":<br/>" + message;
        $('.seat_info').html(result_message);
        $('.seat_info').css({'opacity': '1', 'background-color': background_color, 'color': color});
    },
    mouseleave: function () {
        $('.seat_info').css({'opacity': '0'});
    }
});




