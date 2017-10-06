
    function on_startup() {
        load_json_data("/orders", $('#user_orders_container'));
    }

    var rotation_break = true;

    var request;
    function load_json_data(url, container) {
        start_rotate();
        container.text("");

        // quite prev. request
        if (request) {
            request.abort();
        }

        request = $.ajax({
            url : url,
            type: "GET",
            dataType: 'json',
            success:function(data, textStatus, jqXHR) {
                $('#wheel').hide();
                rotation_break = true;
                handle_order_data(data, container);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if (textStatus != "abort") {
                    $('#order_message').fadeIn("fast");
                    $('#order_message').removeClass();
                    $('#order_message').addClass( "error" );
                    $('#order_message').text(textStatus);

                    $('#wheel').hide();
                    rotation_break = true;
                }
            },
            complete: function(jqXHR, textStatus) {
            }
        });
    }

    function handle_order_data(data, container) {
        for (i = 0; i < data.orders.length; i++) {
            if (i%2 != 0 && data.orders[i].type == "SELL") {
                order_text = '<div class="order_elements order_element_color sell_order_color">';
            } else if (i%2 != 0) {
                order_text = '<div class="order_elements order_element_color">';
            } else if (data.orders[i].type == "SELL") {
                order_text = '<div class="order_elements sell_order">';
            } else {
                order_text = '<div class="order_elements">';
            }

            order_text += '<span class="order_id order_element">' + data.orders[i].owner_username + '</span>';
            order_text += '<span class="order_type order_element">' + data.orders[i].type + '</span>';
            order_text += '<span class="share_amount order_element">' + data.orders[i].amount + '</span>';
            order_text += '<span class="share_price order_element">' + parseFloat(data.orders[i].price).toFixed(2) + '</span>';
            order_text += '<span class="order_result order_element">' + data.orders[i].result + '</span>';
            order_text += '<span class="order_definite_number_of_shares order_element">' + data.orders[i].final_amount + '</span>';

            if (data.orders[i].final_price) {
                order_text += '<span class="order_definite_price order_element">' + parseFloat(data.orders[i].final_price).toFixed(2) + '</span>';
            } else {
                order_text += '<span class="order_definite_price order_element"></span>';
            }

            order_text += '<span class="order_date order_element">' + data.orders[i].date + '</span>';

            order_text += '</div>';

            container.append(order_text);
        }
        $(".create_order_text").show();
    }


    //simple script to rotate all spinners 45 degrees on each tick
    //this works differently from the css transforms, which is smooth

    function start_rotate() {
        if (rotation_break) {
            rotation_break = false;
            $('#wheel').fadeIn( "fast" );
            rotate();
        }
    }

    var count = 0;
    function rotate() {
        if (!rotation_break) {
            var elem2 = document.getElementById('wheel');
            elem2.style.MozTransform = 'scale(0.5) rotate('+count+'deg)';
            elem2.style.WebkitTransform = 'scale(0.5) rotate('+count+'deg)';
            if (count==360) { count = 0 }
            count+=45;
            window.setTimeout(rotate, 100);
        }
    }


$(document).ready(function () {
    on_startup();

    $('#login_link').click(function () {
        $( "#login_form_container" ).fadeIn( "fast" );
        $( "#login_link" ).fadeOut( "slow" );
    });

    $('#register_link').click(function () {
        $( "#login_form_container" ).fadeOut( "fast", function() {
            $( "#register_form_container" ).fadeIn( "fast" );
        });
    });

    $('#close_register').click(function () {
        $( "#register_form_container" ).fadeOut( "fast", function() {
            $( "#login_link" ).fadeIn( "fast" );
        });
    });

    $(document).mouseup(function(e) {
        var container = $("#login_form_container");

        // if the target of the click isn't the container nor a descendant of the container
        if (!container.is(e.target) && container.has(e.target).length === 0) {
            container.hide();
            $("#login_link").show();
        }
    });
});
