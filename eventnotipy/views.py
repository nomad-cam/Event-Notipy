from flask import request,jsonify
from eventnotipy import app
from eventnotipy.models import EventsNotificationConditions,EventsNotificationData,\
                               EventsNotificationRecipients,EventsNotificationRules


@app.route('/')
def hello_world():
    return 'Access Denied!'

@app.route('/event/<change_type>/', methods=['GET','POST'])
def on_change(change_type):
    if request.method == 'POST':

        # fetch the POST'ed values, default to None if not available
        event_id = request.values.get('event_id')
        notify_id = request.values.get('notify_id')

        # if an event id find any actions with required event
        if event_id:
            print('Processing an event_id action')
            print(event_id)

            return jsonify(event_id)

        elif notify_id:
            print('Processing a notify_id action')
            print(notify_id)

            notify_data = EventsNotificationData.query.filter_by(notify_id=notify_id).first()
            # print(notify_data)
            if notify_data.notify_active:
                print('Notification Active! Checking for recipients...')

                recipient_data = EventsNotificationRecipients.query.filter_by(notification_id=notify_id).all()
                # print(recipient_data.count())

                for person in recipient_data:
                    print(person.recipient_name)



            return jsonify(notify_id)

        else:
            return jsonify('None')
        # return {'OK, Got it. Next...'}

    if request.method == 'GET':
        return '/Event Not Available'

