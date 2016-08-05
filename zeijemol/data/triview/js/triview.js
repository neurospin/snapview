
var images_stack;

function initTriViewGui() {
    $("#loading-msg").show();
    $.ajax({
        url: triview_data.ajaxcallback,
        method: "POST",
        data: {"file_data": JSON.stringify(triview_data.file_data)}
    }).done(function(data) {
        $("#loading-msg").hide();
        images_stack = data;
        load_images();
        enableTriViewBtn();
    });
}
function disableTriViewBtn() {
    $(".triview-btn").each(function () {
        $(this).prop("disabled", true);
    });
}
function enableTriViewBtn() {
    $(".triview-btn").each(function () {
        $(this).prop("disabled", false);
    });
}
function load_images() {
    $.each(triview_data.orientations, function( index, orient ) {
        var canvas = $("#" + orient).children("canvas");
        var canvas_el = canvas.get(0);
        canvas.mousedown(function (e) {
            cursor_changed(e, canvas_el, orient);
            $(this).mousemove(function (e) {
                cursor_changed(e, canvas_el, orient);
            });
        }).mouseup(function () {
            $(this).unbind("mousemove");
        }).mouseout(function () {
            $(this).unbind("mousemove");
        });

        var ctx = canvas_el.getContext("2d");
        $("#" + orient).children(".slice-bar").each(function () {
            var nb_slices = images_stack[orient].length;
            $("<span>").addClass("output").insertAfter($(this));
            draw_img(ctx, images_stack[orient][nb_slices / 2.]);
            set_brightness(canvas, triview_data.brightness);

        }).bind("slider:ready slider:changed", function (event, data) {
            var slice_index = data.value;
            $("#"+orient).children(".slice-bar-text").html(
                slice_index + " / " + triview_data.nb_slices[orient]);
            draw_img(ctx, images_stack[orient][slice_index]);
            set_brightness(canvas, triview_data.brightness);
        });

        $("#brightness-bar").each(function () {
        }).bind("slider:ready slider:changed", function (event, data) {
            brightness = data.value;
            $("#brightness-bar-text").html(brightness + " %");
            $(".slice-img").each(function () {
                set_brightness($(this), brightness);
            });
        });

        $(".container").show();
    });
}
function draw_img(canvas_context, encoded_img) {
    var image = new Image();
    image.onload = function() {
        canvas_context.drawImage(image, 0, 0);
    };
    image.src = "data:image/"+ triview_data.extension  + ";base64," + encoded_img;
}
function set_brightness(canvas_el, brightness) {
    var filter = "brightness(" + brightness + "%)";
    var filter_targets = ["filter", "-webkit-filter", "-moz-filter",
                          "-o-filter", "-ms-filter"];
    $.each(filter_targets, function( _, target ){
        canvas_el.css(target, filter);
    });
}
function get_mouse_pos(canvas_el, evt) {
    var rect = canvas_el.getBoundingClientRect();
    return {
        x: evt.clientX - rect.left,
        y: evt.clientY - rect.top
    };
}
function cursor_changed(evt, canvas_el, orient){
    var pos = get_mouse_pos(canvas_el, evt);
    x = pos.x;
    y = pos.y;
    if (orient=="axial") {
        var other_coords = {
            sagittal: Math.round(
                x / triview_data["shapes"][orient][0] *
                triview_data["nb_slices"]["sagittal"]),
            coronal: Math.round(
                triview_data["nb_slices"]["coronal"] -
                y / triview_data["shapes"][orient][1] *
                triview_data["nb_slices"]["coronal"])
        };
    }
    else if (orient=="coronal") {
        var other_coords = {
            sagittal: Math.round(
                x / triview_data["shapes"][orient][0] *
                triview_data["nb_slices"]["sagittal"]),
            axial: Math.round(
                y / triview_data["shapes"][orient][1] *
                triview_data["nb_slices"]["axial"])
        };
    }
    else if (orient=="sagittal") {
        var other_coords = {
            coronal: Math.round(
                x / triview_data["shapes"][orient][0] *
                triview_data["nb_slices"]["coronal"]),
            axial: Math.round(
                y / triview_data["shapes"][orient][1] *
                triview_data["nb_slices"]["axial"])
        };
    }
    $.each(other_coords, function( orient, cut_coord ) {
        $("#" + orient).find(".slice-bar").each(function () {
            $(this).simpleSlider("setValue", cut_coord);
        });
    });
}

