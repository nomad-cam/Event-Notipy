from flask import request,jsonify
from eventnotipy import app
from eventnotipy.models import db
from eventnotipy.models import EventsNotificationConditions,EventsNotificationData, \
                               EventsNotificationRecipients,EventsNotificationRules, \
                               EventsData,EventsImpactData,EventsStatusData,EventsSystemData, \
                               EventsBeamModeData, \
                               ElogGroupData
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
        # notify_id = request.values.get('notify_id')

        # if an event id find any actions with required event
        # if event_id:
        #     print('Processing an event_id action')
        #     print(event_id)
        #
        #     return jsonify(event_id)

        if event_id:
            print('Processing a notify_id action')

            print(event_id)
            events_data = db.session.query(EventsData).filter(EventsData.event_id==event_id).first()
            # pp.pprint(events_data.__dict__)

            # if the event can be found continue...
            if events_data:
                print('Event Recieved! Checking for active notifications...')

                # data = EventsNotificationRules.query.all()
                data = db.session.query(EventsNotificationRules,EventsNotificationConditions,EventsNotificationData,EventsNotificationRecipients)\
                                .join(EventsNotificationConditions, EventsNotificationConditions.condition_id == EventsNotificationRules.rule_condition)\
                                .join(EventsNotificationData, EventsNotificationData.notify_id == EventsNotificationRules.notification_id) \
                                .join(EventsNotificationRecipients, EventsNotificationRecipients.notification_id == EventsNotificationData.notify_id) \
                                .filter(EventsNotificationData.deleted == 0) \
                                .all()

                notify_list = []
                for rules,conditions,nData,recipients in data:

                    dict_rules = dict(rules.__dict__);dict_rules.pop('_sa_instance_state',None)
                    dict_cond = dict(conditions.__dict__);dict_cond.pop('_sa_instance_state',None)
                    dict_data = dict(nData.__dict__);dict_data.pop('_sa_instance_state',None)
                    dict_recipients = dict(recipients.__dict__);dict_recipients.pop('_sa_instance_state',None)
                    print(dict_rules)
                    print(dict_cond)
                    print(dict_data)
                    print(dict_recipients)


                    # check for matches against Group
                    if dict_cond['condition_id'] == 1:
                        group = ElogGroupData.query.filter_by(group_id=events_data.group_id).first()
                        print('Trying to determine the operator')
                        # print(group.group_title,dict_rules['rule_value'])
                        if dict_rules['rule_operator'] == 'EQ':
                            # equal condition
                            if dict_rules['rule_value'] == group.group_title:
                                print('Found a Group Match [Equal]: %s') % dict_rules['rule_value']
                                notify_list.append(dict_data['notify_id'])
                        elif dict_rules['rule_operator'] == 'NE':
                            # not equal condition
                            if dict_rules['rule_value'] != group.group_title:
                                print('Found a Group Match [Not Equal]: %s') % dict_rules['rule_value']
                                notify_list.append(dict_data['notify_id'])
                        else:
                            print('Found a Group Match, but could not determine the operator')


                    # check for matches against System
                    elif dict_cond['condition_id'] == 2:
                        print('Found a System Match')
                        system =EventsSystemData.query.filter_by(system_id=events_data.system).first()
                        # pp.pprint(system)
                        print('Trying to determine the operator')
                        if dict_rules['rule_operator'] == 'EQ':
                            # equal condition
                            if dict_rules['rule_value'] == system.system_name:
                                print('Found a System Match [Equal]: %s') % dict_rules['rule_value']
                                notify_list.append(dict_data['notify_id'])
                        elif dict_rules['rule_operator'] == 'NE':
                            # not equal condition
                            if dict_rules['rule_value'] != system.system_name:
                                print('Found a System Match [Not Equal]: %s') % dict_rules['rule_value']
                                notify_list.append(dict_data['notify_id'])
                        else:
                            print('Found a System Match, but could not determine the operator')


                    # check for matches against Status
                    elif dict_cond['condition_id'] == 3:
                        print('Found a Status Match')
                        status = EventsStatusData.query.filter_by(status_id=events_data.status).first()
                        print('Trying to determine the operator')
                        if dict_rules['rule_operator'] == 'EQ':
                            # equal condition
                            if dict_rules['rule_value'] == status.status_name:
                                print('Found a System Match [Equal]: %s') % dict_rules['rule_value']
                                notify_list.append(dict_data['notify_id'])
                        elif dict_rules['rule_operator'] == 'NE':
                            # not equal condition
                            if dict_rules['rule_value'] != status.status_name:
                                print('Found a System Match [Not Equal]: %s') % dict_rules['rule_value']
                                notify_list.append(dict_data['notify_id'])
                        else:
                            print('Found a System Match, but could not determine the operator')


                    # check for matches against Impact
                    elif dict_cond['condition_id'] == 4:
                        print('Found an Impact Match')
                        impact = EventsImpactData.query.filter_by(impact_id=events_data.impact).first()
                        print('Trying to determine the operator')
                        if dict_rules['rule_operator'] == 'EQ':
                            # equal condition
                            if dict_rules['rule_value'] == impact.impact_name:
                                print('Found a System Match [Equal]: %s') % dict_rules['rule_value']
                                notify_list.append(dict_data['notify_id'])
                        elif dict_rules['rule_operator'] == 'NE':
                            # not equal condition
                            if dict_rules['rule_value'] != impact.impact_name:
                                print('Found a System Match [Not Equal]: %s') % dict_rules['rule_value']
                                notify_list.append(dict_data['notify_id'])
                        else:
                            print('Found a System Match, but could not determine the operator')


                    # check for matches against Beam Mode
                    elif dict_cond['condition_id'] == 5:
                        mode = EventsBeamModeData.query.filter_by(beam_mode_id=events_data.beam_mode).first()
                        print('Trying to determine the operator')
                        if dict_rules['rule_operator'] == 'EQ':
                            # equal condition
                            if dict_rules['rule_value'] == mode.beam_mode_name:
                                print('Found a Beam Mode Match [Equal]: %s') % dict_rules['rule_value']
                                notify_list.append(dict_data['notify_id'])
                        elif dict_rules['rule_operator'] == 'NE':
                            # not equal condition
                            if dict_rules['rule_value'] != mode.beam_mode_name:
                                print('Found a Beam Mode Match [Not Equal]: %s') % dict_rules['rule_value']
                                notify_list.append(dict_data['notify_id'])
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

