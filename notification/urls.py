from django.urls import path

from .views import (GetUnread, ListNotifications, NumberofUnreadNotification,
                    get_html_notifications, redirect_notification, GetLastNotiId, MarkAsRead)

urlpatterns =[
    # page
    path('notifications/', ListNotifications, name = 'notifications'),
    path('list_unread/', GetUnread, name = 'list_unread'),

    # api
    path('unseen_notifications', NumberofUnreadNotification),
    path('html_notis', get_html_notifications),
    path('redirect/<int:noti_id>', redirect_notification),
    path('api_get_unread/', GetUnread, name = 'get_unread'),
    path('get_last_noti_id', GetLastNotiId, name = 'get_last_noti_id'),
    path('mark_all_as_read/', GetUnread, name = 'mark_all_as_read'),
    path('mark_as_read/<int:pk>/', MarkAsRead, name = 'mark_as_read'),
    path('delete/<int:pk>/', GetUnread, name = 'delete'),
]