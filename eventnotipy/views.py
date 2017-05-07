from flask import request,jsonify
from eventnotipy import app
from eventnotipy.models import db
from eventnotipy.models import EventsNotificationConditions,EventsNotificationData, \
                               EventsNotificationRecipients,EventsNotificationRules, \
                               EventsData,EventsImpactData,EventsStatusData,EventsSystemData, \
                               EventsBeamModeData, \
                               ElogGroupData
import pprint
from sqlalchemy.inspection import inspect

pp = pprint.PrettyPrinter(indent=4)

@app.route('/')
def hello_world():
    return 'Access Denied!'

@app.route('/event/<change_type>/<int:event_id>', methods=['GET','POST'])
def on_change(change_type,event_id):
    if request.method == 'POST':

        if event_id:
            print('Processing a notify_id action')

            print(event_id)
            events_data = db.session.query(EventsData).filter(EventsData.event_id==event_id).first()
            # pp.pprint(events_data.__dict__)

            # if the event can be found continue...
            if events_data:
                print('Event Recieved! Checking for active notifications...')

                data_rules = db.session.query(EventsNotificationRules).all()


                notify_list = []
                for rule in data_rules:
                    # check for matches against Group
                    if rule.rule_condition == 1:
                        print('Found a Group Match')
                        group = ElogGroupData.query.filter_by(group_id=events_data.group_id).first()
                        print('Trying to determine the operator')
                        # print(group.group_title,rule.rule_value)
                        if rule.rule_operator == 'EQ':
                            # equal condition
                            if rule.rule_value == group.group_title:
                                print('Found a Group Match [Equal]: %s') % rule.rule_value
                                notify_list.append(rule.notification_id)
                        elif rule.rule_operator == 'NE':
                            # not equal condition
                            if rule.rule_value != group.group_title:
                                print('Found a Group Match [Not Equal]: %s') % rule.rule_value
                                notify_list.append(rule.notification_id)
                        else:
                            print('Found a Group Match, but could not determine the operator')


                    # check for matches against System
                    elif rule.rule_condition == 2:
                        print('Found a System Match')
                        system =EventsSystemData.query.filter_by(system_id=events_data.system).first()
                        # print(system.system_name, rule.rule_value)
                        print('Trying to determine the operator')
                        if rule.rule_operator == 'EQ':
                            # equal condition
                            if rule.rule_value == system.system_name:
                                print('Found a System Match [Equal]: %s') % rule.rule_value
                                notify_list.append(rule.notification_id)
                        elif rule.rule_operator == 'NE':
                            # not equal condition
                            if rule.rule_value != system.system_name:
                                print('Found a System Match [Not Equal]: %s') % rule.rule_value
                                notify_list.append(rule.notification_id)
                        else:
                            print('Found a System Match, but could not determine the operator')


                    # check for matches against Status
                    elif rule.rule_condition == 3:
                        print('Found a Status Match')
                        status = EventsStatusData.query.filter_by(status_id=events_data.status).first()
                        # print(status.status_name, rule.rule_value)
                        print('Trying to determine the operator')
                        if rule.rule_operator == 'EQ':
                            # equal condition
                            if rule.rule_value == status.status_name:
                                print('Found a System Match [Equal]: %s') % rule.rule_value
                                notify_list.append(rule.notification_id)
                        elif rule.rule_operator == 'NE':
                            # not equal condition
                            if rule.rule_value != status.status_name:
                                print('Found a System Match [Not Equal]: %s') % rule.rule_value
                                notify_list.append(rule.notification_id)
                        else:
                            print('Found a System Match, but could not determine the operator')


                    # check for matches against Impact
                    elif rule.rule_condition == 4:
                        print('Found an Impact Match')
                        impact = EventsImpactData.query.filter_by(impact_id=events_data.impact).first()
                        # print(impact.impact_name, rule.rule_value)
                        print('Trying to determine the operator')
                        if rule.rule_operator == 'EQ':
                            # equal condition
                            if rule.rule_value == impact.impact_name:
                                print('Found a System Match [Equal]: %s') % rule.rule_value
                                notify_list.append(rule.notification_id)
                        elif rule.rule_operator == 'NE':
                            # not equal condition
                            if rule.rule_value != impact.impact_name:
                                print('Found a System Match [Not Equal]: %s') % rule.rule_value
                                notify_list.append(rule.notification_id)
                        else:
                            print('Found a System Match, but could not determine the operator')


                    # check for matches against Beam Mode
                    elif rule.rule_condition == 5:
                        mode = EventsBeamModeData.query.filter_by(beam_mode_id=events_data.beam_mode).first()
                        # print(mode.beam_mode_name, rule.rule_value)
                        print('Trying to determine the operator')
                        if rule.rule_operator == 'EQ':
                            # equal condition
                            if rule.rule_value == mode.beam_mode_name:
                                print('Found a Beam Mode Match [Equal]: %s') % rule.rule_value
                                notify_list.append(rule.notification_id)
                        elif rule.rule_operator == 'NE':
                            # not equal condition
                            if rule.rule_value != mode.beam_mode_name:
                                print('Found a Beam Mode Match [Not Equal]: %s') % rule.rule_value
                                notify_list.append(rule.notification_id)
                        else:
                            print('Found a Beam Mode Match, but could not determine the Operator')
                    else:
                        print('No Matches Found')


                print('The following notifications were matched:')
                # notify list contains the notify_ids of the matched rules...
                print(notify_list)

            return jsonify(event_id)

        else:
            return jsonify('None')
        # return {'OK, Got it. Next...'}

    if request.method == 'GET':
        return '/Event Not Available'

