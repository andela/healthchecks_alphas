$(function() {

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

});

