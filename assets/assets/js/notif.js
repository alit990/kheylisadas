function notif(text, btn_text = '', href = ''){
	// wrapper element for a notification
	NotifWrapper = document.createElement('div');
	$(NotifWrapper).attr('class', 'notif-wrapper');
	
	// the text message in the notification
	NotifMsg = document.createElement('p');
	$(NotifMsg).attr('class', 'notif-alert');
	$(NotifMsg).html(text);
	$(NotifWrapper).append(NotifMsg);

	// button link to be added in the notification
	if(btn_text != ''){
		NotifAction = document.createElement('a');
		if(href != ''){
			$(NotifAction).attr('href', href);
		}
		$(NotifAction).attr('class', 'notif-action');
		$(NotifAction).html(btn_text);
		$(NotifWrapper).append(NotifAction);
	}

	// notification close button
	NotifClose = document.createElement('div');
	$(NotifClose).attr('class', 'notif-close');
	$(NotifClose).html('&times;');
	$(NotifWrapper).append(NotifClose);
	
	// append the notification wrapper element to the body
	$('body').append(NotifWrapper);
	
	// delay display of notification by 10ms
	setTimeout(function(){
		$('.notif-wrapper').css({
			'top': 0
		});
	},10);

	// notification close button on-click handler
	$('.notif-wrapper .notif-close').click(function(){
		$(this).parent().remove();
	});
}
