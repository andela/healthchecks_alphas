$(function() {

    $(".member-remove").click(function() {
        var $this = $(this);

        $("#rtm-email").text($this.data("email"));
        $("#remove-team-member-email").val($this.data("email"));
        $('#remove-team-member-modal').modal("show");

        return false;
    });

});

var foo = document.getElementById("notifications-allowed-list");
Sortable.create(foo, { group: "omega" });

var bar = document.getElementById("notifications-not-allowed-list");
Sortable.create(bar, { group: "omega" });