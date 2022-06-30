var notification_heart_beat = false;
$(document).on('click', '#notiDropDown', function (e) {
    e.stopPropagation();
});

function getNumberOfUnseenNotification() {
    $.ajax({
        url: '/notification/unseen_notifications',
        success: function(result) {
            if (result['data'] > 0){
                if (!notification_heart_beat){
                    $('#notiIconLink').append('<span class="heartbeat" id="heartbeat"></span>');
                    notification_heart_beat = true;
                }
                $('#no_of_notifications').html('New '+result['data']);
                fetchNotifications();
            } else {
                $('#heartbeat').remove();
                notification_heart_beat = false;
                $('#no_of_notifications').html('New 0');
                $('#notisList').html('\
                    <li>\
                        <a href="javascript:;">\
                            <span class="details">\
                            <span class="notification-icon circle blue-bgcolor"><i class="fa fa-info"></i></span>\
                            <b> No new notifications. </b></span>\
                        </a>\
                    </li>\
                ');
            }
        },
        error: function() {
            $('#no_of_notifications').html('New 0');
            console.log('Error while getting no of unread notifications.')
        }
    })
}

function fetchNotifications() {
    $.ajax({
        url: '/notification/html_notis',
        success: function(result) {
            $('#notisList').html(result['data']);
        },
        error: function() {
            $('#notisList').html('<li> <b>Error while fetching notifications.</b></li>');
        }
    })
}

function markAsRead(id){
    $.ajax({
        url: '/notification/mark_as_read/' + id,
        success: function(result) {
            getNumberOfUnseenNotification();
        },
        error: function() {
            getNumberOfUnseenNotification();
        }
    })
}
getNumberOfUnseenNotification();
setInterval(getNumberOfUnseenNotification, 180000);