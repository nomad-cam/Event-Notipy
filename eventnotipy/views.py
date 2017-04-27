from flask import request,jsonify
from eventnotipy import app
from eventnotipy.models import db
from eventnotipy.models import EventsNotificationConditions,EventsNotificationData,\
                               EventsNotificationRecipients,EventsNotificationRules,\
                               EventsData
import pprint

pp = pprint.PrettyPrinter(indent=4)

@app.route('/')
def hello_world():
    return 'Access Denied!'

@app.route('/event/<change_type>/<int:event_id>', methods=['GET','POST'])
def on_change(change_type,event_id):
    if request.method == 'POST':
        print(request.form)

        # fetch the POST'ed values, default to None if not available
        # event_id = request.values.get('event_id')
        notify_id = request.values.get('notify_id')

        # if an event id find any actions with required event
        # if event_id:
        #     print('Processing an event_id action')
        #     print(event_id)
        #
        #     return jsonify(event_id)

        if event_id:
            print('Processing a notify_id action')

            events_data = EventsData.query.filter_by(event_id=event_id).first()

            # if the event can be found continue...
            if events_data:
                print('Event Recieved! Checking for active notifications...')

                # data = EventsNotificationRules.query.all()
                data = db.session.query(EventsNotificationRules,EventsNotificationConditions,EventsNotificationData)\
                                           .join(EventsNotificationConditions, EventsNotificationConditions.condition_id == EventsNotificationRules.rule_condition)\
                                           .join(EventsNotificationData, EventsNotificationData.notify_id == EventsNotificationRules.notification_id) \
                                           .all()

                for rules,conditions,nData in data:

                    print(rules.__dict__)
                    print(conditions.__dict__)
                    print(nData.__dict__)


            return jsonify(event_id)

        else:
            return jsonify('None')
        # return {'OK, Got it. Next...'}

    if request.method == 'GET':
        return '/Event Not Available'

