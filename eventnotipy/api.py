from flask import request, jsonify, Blueprint, abort

from eventnotipy.models import db
from eventnotipy.models import EventsNotificationConditions, EventsNotificationData, \
                               EventsNotificationRecipients, EventsNotificationRules, \
                               EventsData, EventsImpactData, EventsStatusData, EventsSystemData, \
                               EventsBeamModeData, EventsGroups, EventsContributors, \
                               EventsSubSystemData, EventsOncallData, EventsOncallNames, \
                               ElogGroupData, ElogBeamModeData, \
                               Templates, SolUsers

api_route = Blueprint('api_route',__name__)

#
# Create/Delete a notification that is triggered on a specific JOE
# <username> - as specified from ldap username string
#
# <event_id> - the JOE id
@api_route.route('/notifications/<username>/<int:event_id>/', methods=['POST, DELETE'])
def api_add_event(event_id, username):
    if request.method == 'POST':
        #response 201
        return jsonify(method='POST',event_id=event_id, user_id=username)

    if request.method == 'DELETE':
        # response 200
        return jsonify(method='DELETE',event_id=event_id, user_id=username)


#
# Show all notifications
@api_route.route('/notifications/', methods=['GET'])
def api_display_current():
    if request.method == 'GET':
        notifications = EventsNotificationData.get_all_current()
        results = []

        for result in notifications:
            mode_string = ''
            if result.notify_mode == 1:
                mode_string = 'email only'
            if result.notify_mode == 2:
                mode_string = 'sms only'
            if result.notify_mode == 3:
                mode_string = 'both email and sms'

            if result.notify_submitted:
                on_submit_string = 'True'
            else:
                on_submit_string = 'False'

            if result.notify_updated:
                on_update_string = 'True'
            else:
                on_update_string = 'False'

            obj = {
                'id': result.notify_id,
                'title': result.notify_title,
                'active': result.notify_active,
                'date_created': result.notify_date_added,
                'date_modified': result.notify_date_modified,
                'mode': mode_string,
                'on_update': on_update_string,
                'on_submit': on_submit_string,
            }
            results.append(obj)

        response = jsonify(results)
        response.status_code = 200
        return response


#
# Show all notifications assigned to a specific user
# <user_id> - as specified from ldap username string
@api_route.route('/notifications/<username>/', methods=['GET'])
def api_display_user(username):
    if request.method == 'GET':
        user_id = db.session.query(SolUsers.id, SolUsers.name).filter_by(username=username).first()

        if not user_id:
            response = jsonify({'error': 'username not found'})
            response.status_code = 200
            return response

        recipients_events = db.session.query(EventsNotificationRecipients.notification_id) \
            .filter_by(recipient_name=user_id.name).all()

        results = []
        for event in recipients_events:

            notifications = EventsNotificationData.query\
                .filter_by(notify_id=event.notification_id)\
                .filter_by(deleted=0).all()

            for result in notifications:
                mode_string = ''
                if result.notify_mode == 1:
                    mode_string = 'email only'
                if result.notify_mode == 2:
                    mode_string = 'sms only'
                if result.notify_mode == 3:
                    mode_string = 'both email and sms'

                if result.notify_submitted:
                    on_submit_string = 'True'
                else:
                    on_submit_string = 'False'

                if result.notify_updated:
                    on_update_string = 'True'
                else:
                    on_update_string = 'False'

                obj = {
                    'id': result.notify_id,
                    'title': result.notify_title,
                    'active': result.notify_active,
                    'date_created': result.notify_date_added,
                    'date_modified': result.notify_date_modified,
                    'mode': mode_string,
                    'on_update': on_update_string,
                    'on_submit': on_submit_string,
                }
                results.append(obj)

        response = jsonify(results)
        response.status_code = 200
        return response


#
# Enable/Disable a notification based on id
# <value> - notification_id
#
# <action> - enable
#            disable
#            delete
#            show
#
@api_route.route('/notifications/<int:value>/<action>', methods=['GET', 'PUT'])
def api_enable_id(action, value):
    if request.method == 'PUT':
        # response 200
        return jsonify(action=action, value=value)

    if request.method == 'GET':
        if action == 'show':
            notifications = EventsNotificationData.query \
                .filter_by(notify_id=value) \
                .filter_by(deleted=0).first()

            if notifications:
                # Only respond if the data is not deleted
                mode_string = ''
                if notifications.notify_mode == 1:
                    mode_string = 'email only'
                if notifications.notify_mode == 2:
                    mode_string = 'sms only'
                if notifications.notify_mode == 3:
                    mode_string = 'both email and sms'

                if notifications.notify_submitted:
                    on_submit_string = 'True'
                else:
                    on_submit_string = 'False'

                if notifications.notify_updated:
                    on_update_string = 'True'
                else:
                    on_update_string = 'False'

                obj = {
                    'id': notifications.notify_id,
                    'title': notifications.notify_title,
                    'active': notifications.notify_active,
                    'date_created': notifications.notify_date_added,
                    'date_modified': notifications.notify_date_modified,
                    'mode': mode_string,
                    'on_update': on_update_string,
                    'on_submit': on_submit_string,
                }
            else:
                obj = {'error': 'Notification has been deleted'}

            response = jsonify(obj)
            response.status_code = 200
            return response

        else:
            abort(404)


#
# Create a notification that is triggered on condition/operator/value
# <user_id> - as specified from ldap username string
#
# <condition> - 1 = Group
#               2 = System
#               3 = Status
#               4 = Impact
#               5 = Beam Mode
#
# <operator> - EQ = equals
#              NE = not equals
#
# <value> - condition specific, see docs for more information
#
@api_route.route('/notifications/<user_id>/<int:condition>/<operator>/<value>/', methods=['POST'])
def api_add_condition(user_id, condition, operator, value):
    if request.method == 'POST':
        # response 200
        return jsonify(user_id=user_id, condition=condition, operator=operator, value=value)
