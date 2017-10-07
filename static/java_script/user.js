    function on_startup() {
        load_json_data("/orders/", $('#user_orders_container'), "handle_order_data");
    }

    var rotation_break = true;

    var request;
    function load_json_data(url, container, handler_function) {
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
                if (handler_function == "handle_order_data"){
                    handle_order_data(data, container);
                } else if (handler_function == "handle_register_data") {
                    handle_register_data(data, container);
                }

            },
            error: function(jqXHR, textStatus, errorThrown) {
                if (textStatus != "abort") {
                    $('#order_message').fadeIn("fast");
                    $('#order_message').removeClass();
                    $('#order_message').addClass( "error" );
                    $('#order_message').text(textStatus);

                    $('#wheel').hide();
                    rotation_break = true;

//                    console.log(errorThrown.name);
//                    console.log(errorThrown.message);
//                    console.log(errorThrown.stack);
                }
            },
            complete: function(jqXHR, textStatus) {
            }
        });
    }

    function change_headers(header_list) {
        $('.order_headers').text("");
        header_html = "";

        for (p = 0; p < header_list.length; p++) {
            header_html += '<span class="' + header_list[p][0] + '">' + header_list[p][1] + '</span>'
        }

        $('.order_headers').append(header_html);
    }

    function handle_register_data(data, container) {
        for (i = 0; i < data.register.length; i++) {
            if (i%2 != 0) {
                order_text = '<div class="order_elements order_element_color">';
            } else {
                order_text = '<div class="order_elements">';
            }

            order_text += '<span class="order_id order_element">' + data.register[i].owner_full_name + '</span>';
            order_text += '<span class="share_amount order_element">' + data.register[i].share_amount + '</span>';
            order_text += '<span class="share_range_content order_element">' + get_share_ranges(data.register[i].share_ranges) + '</span>';

            container.append(order_text);
        }
        $(".create_order_text").hide();
    }

    function get_share_ranges(range_list) {
        if (typeof range_list[0] != "undefined") {
            range_result = "";
            range_list_len = range_list.length - 1;

            for (n = 0; n < range_list_len; n++) {
                range_result += range_list[n][0] + " - " + range_list[n][1] + ", ";
            }

            return range_result + range_list[range_list_len][0] + " - " + range_list[range_list_len][1];
        }
        return " - ";
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

    function show_change_credentials() {
        if ($("#change_credentials").is(":visible")) {
            hide_change_password();
        } else {
            $("#change_credentials").show();
            $("#change_password_button").css('display', 'block');
            $("#save_changes_button").hide();
        }
    }

    function change_email() {
        $("#current_pass_input").show();
        $("#cred_email_input").show();
    }

    function change_password() {
        $("#current_pass_input").show();
        $("#cred_pass_input").show();
        $("#cred_pass_retype").show();
        $("#save_changes_button").show();
        $("#cancel_save_change_button").show();
        $("#change_password_button").css('display', 'none');
    }

    function hide_change_password() {
        $("#current_pass_input").val("");
        $("#current_pass_input").hide();
        $("#cred_pass_input").val("");
        $("#cred_pass_input").hide();
        $("#cred_pass_retype").val("");
        $("#cred_pass_retype").hide();
        $("#change_credentials").hide();
        $("#credentials_error_message").hide();
        $("#cancel_save_change_button").hide();
    }

    function error_message_change_password(error_message) {
        $("#credentials_error_message").text(error_message);
        $("#credentials_error_message").fadeIn("fast");
    }

$(document).ready(function () {
    on_startup();

    $('#create_order_button').click(function () {
        if($('#new_order_wrapper').is(':visible')) {
            $("#new_order_wrapper").fadeOut("fast")
        } else {
            $("#new_order_wrapper").fadeIn("fast")
            document.getElementById("new_order").reset();
            $('#create_order_message').text("");
            $('#create_order_message').fadeOut( "fast" );
        }
    });

    $('#link_pending').click(function () {
        change_headers([["order_id order_header", "user"],
                        ["order_type order_header", "type"],
                        ["share_amount order_header", "amount"],
                        ["share_price order_header", "price"],
                        ["order_result order_header", "result"],
                        ["order_definite_number_of_shares order_header", "final amount"],
                        ["order_definite_price order_header", "final price"],
                        ["order_date order_header", "date"]]);
        $( "#link_register" ).removeClass("selected");
        $( "#link_pending" ).addClass("selected");
        if ($("input:radio[name='view']:checked").val() == "user") {
            load_json_data("/orders/?&user=T", $('#user_orders_container'), "handle_order_data");
        } else if ($("input:radio[name='view']:checked").val() == "all") {
            load_json_data("/orders", $('#user_orders_container'), "handle_order_data");
        }
    });

    $('#link_register').click(function () {
        change_headers([["order_id order_header", "user"],
                        ["share_amount order_header", "share amount"],
                        ["share_range order_header", "share range"]]);
        $( "#link_pending" ).removeClass("selected");
        $( "#link_register" ).addClass("selected");
        if ($("input:radio[name='view']:checked").val() == "user") {
            load_json_data("/catalog/?&user=T", $('#user_orders_container'), "handle_register_data");
        } else if ($("input:radio[name='view']:checked").val() == "all") {
            load_json_data("/catalog", $('#user_orders_container'), "handle_register_data");
        }
    });

    $('input:radio[name=view]').change(function() {
        $('html, body').animate({
            scrollTop: $("#bottom").offset().top - 225
        }, 1000);
//        if (this.value == 'user') {
//            // todo add if statement for register
//            if ($("#link_pending").hasClass( "selected" )) {
//                load_json_data("/orders/?&user=T", $('#user_orders_container'), "handle_order_data");
//            } else if ($("#link_register").hasClass( "selected" )) {
//                load_json_data("/catalog/?&user=T", $('#user_orders_container'), "handle_register_data");
//            }
//        } else if (this.value == 'all') {
            // todo add if statement for register
            if ($("#link_pending").hasClass( "selected" )) {
                load_json_data("/orders", $('#user_orders_container'), "handle_order_data");
            } else if ($("#link_register").hasClass( "selected" )) {
                load_json_data("/catalog", $('#user_orders_container'), "handle_register_data");
            }
//        }
    });

    // deprecated
    $('#show_all').click(function () {
        if($('#order_wrapper_all').is(':visible')) {
            $("#order_wrapper_all").fadeOut("fast")
        } else {
            $("#order_wrapper_all").fadeIn("fast")
            load_json_data("/orders/", $('#all_orders_container'));
        }
    });

    //callback handler for form submit
    $("#new_order").submit(function(e) {
        var postData = $(this).serializeArray();
        var formURL = $(this).attr("action");
        $.ajax({
            url : formURL,
            type: "POST",
            data : postData,
            dataType: 'json',
            success:function(data, textStatus, jqXHR) {
                $('#order_message').fadeOut( "fast" );
                $('#order_message').removeClass();
                if (data.message) {
                    // place message in order_message and remove #create_order
                    $('#new_order_wrapper').fadeOut( "fast" );
                    $('#order_message').fadeIn( "fast" );
                    $('#order_message').addClass( "message" );
                    $('#order_message').text(data.message);
                    load_json_data("/orders/?&user=T&status=DEFINITIVE", $('#user_orders_container'));
                } if (data.warning) {
                    $('#create_order_message').fadeIn("fast");
                    $('#create_order_message').addClass( "warning" );
                    $('#create_order_message').text(data.warning);
                } if (data.error) {
                    $('#create_order_message').fadeIn("fast");
                    $('#create_order_message').addClass( "error" );
                    $('#create_order_message').text(data.error);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                // place error in order_message and remove #create_order
                $('#new_order_wrapper').fadeOut( "fast" );
                $('#order_message').fadeIn("fast");
                $('#order_message').removeClass();
                $('#order_message').addClass( "error" );
                $('#order_message').text("unexpected error");
            }
        });
        e.preventDefault(); //STOP default action
        //e.unbind(); //unbind. to stop multiple form submit.
    });


    $("#change_credentials_form").submit(function(e) {
        var postData = $(this).serializeArray();
        var formURL = $(this).attr("action");
        $.ajax({
            url : formURL,
            type: "POST",
            data : postData,
            dataType: 'json',
            success:function(data, textStatus, jqXHR) {
                console.log("success");
                if (data.error) {
                    error_message_change_password(data.error);
                } else {
                    hide_change_password();
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("error");
                error_message_change_password("Unexpected error occurred.");
            }
        });
        e.preventDefault(); //STOP default action
    });


    //callback handler for form submit
    $("#user_manager_new_person").submit(function(e) {
        var postData = $(this).serializeArray();
        var formURL = $(this).attr("action");
        $.ajax({
            url : formURL,
            type: "POST",
            data : postData,
            dataType: 'json',
            success:function(data, textStatus, jqXHR) {
                $('#order_message').fadeOut( "fast" );
                $('#order_message').removeClass();
                if (data.message) {
                    $('#user_manager_new_person_message').removeClass();
                    $('#user_manager_new_person_message').fadeIn( "fast" );
                    $('#user_manager_new_person_message').addClass( "message" );
                    $('#user_manager_new_person_message').text(data.message);
                    document.getElementById("user_manager_new_person").reset();
                } if (data.warning) {
                    $('#user_manager_new_person_message').removeClass();
                    $('#user_manager_new_person_message').fadeIn("fast");
                    $('#user_manager_new_person_message').addClass( "warning" );
                    $('#user_manager_new_person_message').text(data.warning);
                } if (data.error) {
                    $('#user_manager_new_person_message').removeClass();
                    $('#user_manager_new_person_message').fadeIn("fast");
                    $('#user_manager_new_person_message').addClass( "error" );
                    $('#user_manager_new_person_message').text(data.error);
                }
                var person_select_order = document.getElementById("person_id");
                var option_order = document.createElement("option");
                option_order.text = data.person_name;
                option_order.value = data.person_id;
                person_select_order.add(option_order);

                var person_select_login = document.getElementById("person_login_id");
                var option_login = document.createElement("option");
                option_login.text = data.person_name;
                option_login.value = data.person_id;
                person_select_login.add(option_login);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                // place error in order_message and remove #create_order
                $('#user_manager_new_person_message').fadeIn("fast");
                $('#user_manager_new_person_message').removeClass();
                $('#user_manager_new_person_message').addClass( "error" );
                $('#user_manager_new_person_message').text("unexpected error");
            }
        });
        e.preventDefault(); //STOP default action
        //e.unbind(); //unbind. to stop multiple form submit.
    });

    //callback handler for form submit
    $("#user_manager_new_login").submit(function(e) {
        var postData = $(this).serializeArray();
        var formURL = $(this).attr("action");
        $.ajax({
            url : formURL,
            type: "POST",
            data : postData,
            dataType: 'json',
            success:function(data, textStatus, jqXHR) {
                $('#order_message').fadeOut( "fast" );
                $('#order_message').removeClass();
                if (data.message) {
                    $('#user_manager_new_login_message').removeClass();
                    $('#user_manager_new_login_message').fadeIn( "fast" );
                    $('#user_manager_new_login_message').addClass( "message" );
                    $('#user_manager_new_login_message').text(data.message);
                    document.getElementById("user_manager_new_login").reset();
                } if (data.warning) {
                    $('#user_manager_new_login_message').removeClass();
                    $('#user_manager_new_login_message').fadeIn("fast");
                    $('#user_manager_new_login_message').addClass( "warning" );
                    $('#user_manager_new_login_message').text(data.warning);
                } if (data.error) {
                    $('#user_manager_new_login_message').removeClass();
                    $('#user_manager_new_login_message').fadeIn("fast");
                    $('#user_manager_new_login_message').addClass( "error" );
                    $('#user_manager_new_login_message').text(data.error);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                // place error in order_message and remove #create_order
                $('#user_manager_new_login_message').fadeIn("fast");
                $('#user_manager_new_login_message').removeClass();
                $('#user_manager_new_login_message').addClass( "error" );
                $('#user_manager_new_login_message').text("unexpected error");
            }
        });
        e.preventDefault(); //STOP default action
        //e.unbind(); //unbind. to stop multiple form submit.
    });

    //callback handler for form submit
    $("#user_manager_new_order").submit(function(e) {
        var postData = $(this).serializeArray();
        var formURL = $(this).attr("action");
        $.ajax({
            url : formURL,
            type: "POST",
            data : postData,
            dataType: 'json',
            success:function(data, textStatus, jqXHR) {
                $('#order_message').fadeOut( "fast" );
                $('#order_message').removeClass();
                if (data.message) {
                    $('#user_manager_create_order_message').removeClass();
                    $('#user_manager_create_order_message').fadeIn( "fast" );
                    $('#user_manager_create_order_message').addClass( "message" );
                    $('#user_manager_create_order_message').text(data.message);
                    document.getElementById("user_manager_new_order").reset();
                } if (data.warning) {
                    $('#user_manager_create_order_message').removeClass();
                    $('#user_manager_create_order_message').fadeIn("fast");
                    $('#user_manager_create_order_message').addClass( "warning" );
                    $('#user_manager_create_order_message').text(data.warning);
                } if (data.error) {
                    $('#user_manager_create_order_message').removeClass();
                    $('#user_manager_create_order_message').fadeIn("fast");
                    $('#user_manager_create_order_message').addClass( "error" );
                    $('#user_manager_create_order_message').text(data.error);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                // place error in order_message and remove #create_order
                $('#user_manager_create_order_message').fadeIn("fast");
                $('#user_manager_create_order_message').removeClass();
                $('#user_manager_create_order_message').addClass( "error" );
                $('#user_manager_create_order_message').text("unexpected error");
            }
        });
        e.preventDefault(); //STOP default action
        //e.unbind(); //unbind. to stop multiple form submit.
    });

    $(document).mouseup(function(e) {
        var container = $("#change_credentials");

        // if the target of the click isn't the container nor a descendant of the container
        if (!container.is(e.target) && container.has(e.target).length === 0) {
            hide_change_password()
        }
    });

    $(function() {
        $('a[href*=#]:not([href=#])').click(function() {
            if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
                var target = $(this.hash);
                target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
                if (target.length) {
                    $('html,body').animate({
                        scrollTop: target.offset().top - 225
                    }, 1000);
                return false;
                }
            }
        });
    });
});