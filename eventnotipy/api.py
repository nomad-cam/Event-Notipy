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
#
# **** Possible Future Enhancement ****
#
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
            recipients = EventsNotificationRecipients.query.filter_by(notification_id=result.notify_id).all()
            recipient_string = ''
            if recipients:
                for person in recipients:
                    recipient_string += person.recipient_name + ', '
            condition_str = ''
            conditions = EventsNotificationRules.query.filter_by(notification_id=result.notify_id).all()
            if conditions:
                for condition in conditions:
                    condition_str += condition.conditions[0].condition_name
                    if condition.rule_operator == 'EQ':
                        condition_str += ' = '
                    else:
                        condition_str += ' != '
                    condition_str += condition.rule_value + ', '


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
                'recipients': recipient_string[:-2],
                'conditions': condition_str[:-2],
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
                condition_str = ''
                conditions = EventsNotificationRules.query.filter_by(notification_id=result.notify_id).all()
                if conditions:
                    for condition in conditions:
                        condition_str += condition.conditions[0].condition_name
                        if condition.rule_operator == 'EQ':
                            condition_str += ' = '
                        else:
                            condition_str += ' != '
                        condition_str += condition.rule_value + ', '

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
                    'conditions': condition_str[:-2],
                    'on_update': on_update_string,
                    'on_submit': on_submit_string,
                }
                results.append(obj)

        response = jsonify(results)
        response.status_code = 200
        return response


#
# Enable/Disable a notification based on id
# <note_id> - notification_id
#
# <action> - enable
#            disable
#            delete
#            show
#
@api_route.route('/notifications/<int:note_id>/<action>', methods=['GET', 'PUT', 'DELETE'])
def api_enable_id(note_id, action):
    # Process data for all methods
    notification = EventsNotificationData.query \
        .filter_by(notify_id=note_id) \
        .filter_by(deleted=0).first()

    if notification:
        # Only respond if the data is not deleted
        mode_string = ''
        if notification.notify_mode == 1:
            mode_string = 'email only'
        if notification.notify_mode == 2:
            mode_string = 'sms only'
        if notification.notify_mode == 3:
            mode_string = 'both email and sms'

        if notification.notify_submitted:
            on_submit_string = 'True'
        else:
            on_submit_string = 'False'

        if notification.notify_updated:
            on_update_string = 'True'
        else:
            on_update_string = 'False'

        obj = {
            'id': notification.notify_id,
            'title': notification.notify_title,
            'active': notification.notify_active,
            'date_created': notification.notify_date_added,
            'date_modified': notification.notify_date_modified,
            'mode': mode_string,
            'on_update': on_update_string,
            'on_submit': on_submit_string,
        }
    else:
        # return before any access method if notification not available
        return jsonify(error='Notification has been deleted')

    if request.method == 'PUT':
        actions = ['enable', 'disable']
        if action in actions:
            if action == 'enable':
                notification.notify_active = 1
                db.session.commit()
                return jsonify(result='Success')
            if action == 'disable':
                notification.notify_active = 0
                db.session.commit()
                return jsonify(result='Success')
        else:
            abort(404)

    if request.method == 'DELETE':
        if action == 'delete':
            notification.deleted = 1
            notification.notify_active = 0
            db.session.commit()
            return jsonify(result='Success')
        else:
            abort(404)

    if request.method == 'GET':
        if action == 'show':
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
        return jsonify(method='POST',user_id=user_id, condition=condition, operator=operator, value=value)
