from flask import request, jsonify, Blueprint

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
# Create a notification that is triggered on a specific JOE
# <user_id> - as specified from ldap username string
#
# <event_id> - the JOE id
@api_route.route('/notifications/<user_id>/<int:event_id>/', methods=['POST'])
def api_add_event(event_id, user_id):
    if request.method == 'POST':
        return jsonify(event_id=event_id, user_id=user_id)


#
# Show all notifications
@api_route.route('/notifications/', methods=['GET'])
def api_display_current():
    if request.method == 'GET':
        notifications = EventsNotificationData.get_all_current()
        results = []

        for result in notifications:
            obj = {
                'id': result.notify_id,
                'title': result.notify_title,
                'active': result.notify_active,
                'date_created': result.notify_date_added,
                'date_modified': result.notify_date_modified
            }
            results.append(obj)

        response = jsonify(results)
        response.status_code = 200
        return response

#
# Show all notifications assigned to a specific user
# <user_id> - as specified from ldap username string
@api_route.route('/notifications/<user_id>/', methods=['GET'])
def api_display_user(user_id):
    if request.method == 'GET':
        return jsonify(user_id=user_id)


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
        return jsonify(user_id=user_id, condition=condition, operator=operator, value=value)
