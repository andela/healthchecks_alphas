$(function() {
    var MINUTE = {name: "minute", nsecs: 60};
    var HOUR = {name: "hour", nsecs: MINUTE.nsecs * 60};
    var DAY = {name: "day", nsecs: HOUR.nsecs * 24};
    var WEEK = {name: "week", nsecs: DAY.nsecs * 7};
    var UNITS = [WEEK, DAY, HOUR, MINUTE];

    var secsToText = function(total) {
        var remainingSeconds = Math.floor(total);
        var result = "";
        for (var i=0, unit; unit=UNITS[i]; i++) {
            if (unit === WEEK && remainingSeconds % unit.nsecs != 0) {
                // Say "8 days" instead of "1 week 1 day"
                continue
            }

            var count = Math.floor(remainingSeconds / unit.nsecs);
            remainingSeconds = remainingSeconds % unit.nsecs;

            if (count == 1) {
                result += "1 " + unit.name + " ";
            }

            if (count > 1) {
                result += count + " " + unit.name + "s ";
            }
        }

        return result;
    }

    var priorityDelaySlider = document.getElementById("priority-delay-slider");
    noUiSlider.create(priorityDelaySlider, {
        start: [20],
        connect: "lower",
        range: {
            'min': [60, 60],
            '33%': [3600, 3600],
            '66%': [86400, 86400],
            '83%': [604800, 604800],
            'max': 2592000,
        },
        pips: {
            mode: 'values',
            values: [60, 1800, 3600, 43200, 86400, 604800, 2592000],
            density: 4,
            format: {
                to: secsToText,
                from: function() {}
            }
        }
    });

    priorityDelaySlider.noUiSlider.on("update", function(a, b, value) {
        var rounded = Math.round(value);
        $("#priority-delay-slider-value").text(secsToText(rounded));
        $("#update-priority-delay-delay").val(rounded);
    });


    var allowed = document.getElementById("notifications-allowed-list");
    var srt_allowed = Sortable.create(allowed, {
        group: "omega",
        onSort: function (evt) {
            console.log("on sort!");
            var childs = $("#notifications-allowed-list").children();
//            console.log("Childs: " + JSON.stringify(childs));
            childs.each(function(index) {
                console.log("Child each: " + JSON.stringify(this));
//                console.log("Child each: " + this);
                $(this).children("input[name*='priority']").val(index+1);
            });
        }
     });

    var blocked = document.getElementById("notifications-not-allowed-list");
    srt_blocked = Sortable.create(blocked,{
        group: "omega",
        onAdd: function(evt){
                console.log("on Add Not Allowed changed!");
                console.log(evt.newIndex);
                console.log(evt.item)
                $(evt.item).children("input[name*='priority']").val(0);
            }
        });

    $(".member-remove").click(function() {
        var $this = $(this);

        $("#rtm-email").text($this.data("email"));
        $("#remove-team-member-email").val($this.data("email"));
        $('#remove-team-member-modal').modal("show");

        return false;
    });

    $(".edit-checks").click(function() {
        var $this = $(this);
        $("#set-allowed-checks-modal").modal("show");
        var url = $(this).attr("href");
        console.log("Url: " + url)
        $.ajax(url).done(function(data) {
            $("#set-allowed-checks-modal .modal-content").html(data);
            $("#set-checks-email").text($this.data("email"));
            $("#set-checks-team-member-email").val($this.data("email"));
        })

        return false;
    });

    var $allowed_checks_modal = $("#set-allowed-checks-modal");
    $allowed_checks_modal.on("click", "#toggle-all", function() {
        var value = $(this).prop("checked");
        $allowed_checks_modal.find(".toggle").prop("checked", value);

    });

});

