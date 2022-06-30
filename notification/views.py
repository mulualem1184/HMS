from datetime import datetime
from typing import Sequence
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from .serializers import NotificationSerializer
from .models import Notification, get_read, get_unread, notify, UserNotification


@login_required
def ListNotifications(request):
	try:
		return render(request, 'notification/notification_list.html',{'notis': request.user.notification_set.all()})
	except Exception as e:
		print("### Exception ", e)
		messages.error(request, "Couldn't load notifications. Please try again later!")
		return redirect('Nowheretoredirect')


html_base_string = """
<li>
	<a href="{link}">
		<span class="time">{time}</span>
		<span class="details">
		<span class="notification-icon circle blue-bgcolor"><i class="fa fa-bell"></i></span>
		<b> {message} </b></span>
	</a>
</li>
"""


def get_html_notifications(request):
	nots:Sequence[Notification] = get_unread(request.user)
	html_string = ""
	# n.link if n.link else 'javascript:;'
	for n in nots:
		html_string += html_base_string.format(link=f'/notification/redirect/{n.id}' if n.link else f'javascript:markAsRead({n.id});', time=n.timesince(), message=n.noti)
	return JsonResponse({
		'data': html_string
	})


def redirect_notification(request, noti_id):
	notification:Notification = get_object_or_404(Notification, id=noti_id)
	un = UserNotification.objects.get(noti=notification)
	un.read = True
	un.save()
	return redirect(notification.link)


@login_required   
def GetUnread(request):
	try:
		unread  = get_unread(request.user)
		data = {'fetch_time':datetime.now(),'notis':NotificationSerializer(unread, many=True).data, 'num':unread.count(),'error':False}
		return JsonResponse( data, safe = False)
	except Exception as e:
		print("@@@@@@ Exception ", e)
		return JsonResponse( {'error':True, 'msg':str(e)})


def NumberofUnreadNotification(request):
	user = request.user
	unread_notis = get_unread(user)
	return JsonResponse({
		'data': len(unread_notis)
	})


@login_required
def GetLastNotiId(request):
	try:
		last_noti_id  = request.user.notification_set.filter(usernotification__read = False, usernotification__delete = False)[:1]
		return JsonResponse({'error':False, 'id':last_noti_id.id}) 
	except Exception as e:
		print("@@@@ Exception ", e)
		return JsonResponse({'error':True, 'msg':str(e)})


@login_required
def MarkAsRead(request, pk):
	try:
		noti:Notification = get_object_or_404(Notification, id=pk)
		un:UserNotification = UserNotification.objects.get(noti=noti)
		un.read = True
		un.save()
		return JsonResponse(data = {'error':False, })
	except Exception as e:
		print("@@@ Exception ",e)
		return JsonResponse(data = {'error':True, 'msg':str(e)})