from flask import request,jsonify
from eventnotipy import app
from eventnotipy.models import db
from eventnotipy.models import EventsNotificationConditions,EventsNotificationData, \
                               EventsNotificationRecipients,EventsNotificationRules, \
                               EventsData,EventsImpactData,EventsStatusData,EventsSystemData, \
                               EventsBeamModeData, \
                               ElogGroupData
import pprint
import requests

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

                data_rules = db.session.query(EventsNotificationRules) \
                            .join(EventsNotificationData, EventsNotificationRules.notification_id == EventsNotificationData.notify_id) \
                            .all()

                # use a set as we don't care about duplicates
                notify_list = set()
                for rule in data_rules:
                    # Before checking anything make sure the rule is not deleted
                    if rule.notify_data[0].deleted == 0:
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
                                    # if data_rules.deleted == 0:
                                        # the event has not been deleted
                                    notify_list.add(rule.notification_id)
                            elif rule.rule_operator == 'NE':
                                # not equal condition
                                if rule.rule_value != group.group_title:
                                    print('Found a Group Match [Not Equal]: %s') % rule.rule_value
                                    notify_list.add(rule.notification_id)
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
                                    notify_list.add(rule.notification_id)
                            elif rule.rule_operator == 'NE':
                                # not equal condition
                                if rule.rule_value != system.system_name:
                                    print('Found a System Match [Not Equal]: %s') % rule.rule_value
                                    notify_list.add(rule.notification_id)
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
                                    notify_list.add(rule.notification_id)
                            elif rule.rule_operator == 'NE':
                                # not equal condition
                                if rule.rule_value != status.status_name:
                                    print('Found a System Match [Not Equal]: %s') % rule.rule_value
                                    notify_list.add(rule.notification_id)
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
                                    notify_list.add(rule.notification_id)
                            elif rule.rule_operator == 'NE':
                                # not equal condition
                                if rule.rule_value != impact.impact_name:
                                    print('Found a System Match [Not Equal]: %s') % rule.rule_value
                                    notify_list.add(rule.notification_id)
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
                                    notify_list.add(rule.notification_id)
                            elif rule.rule_operator == 'NE':
                                # not equal condition
                                if rule.rule_value != mode.beam_mode_name:
                                    print('Found a Beam Mode Match [Not Equal]: %s') % rule.rule_value
                                    notify_list.add(rule.notification_id)
                            else:
                                print('Found a Beam Mode Match, but could not determine the Operator')
                        else:
                            print('No Matches Found')

                    else:
                        print('Sorry rule #%s has been deleted' % rule.notification_id)

                print('The following notifications were matched:')
                # notify list contains the notify_ids of the matched rules...
                print(notify_list)

                # now we have the matched rules, get the details and send out the message
                for x in notify_list:
                    # recipient = EventsNotificationRecipients.query.filter_by(notification_id=x).first()
                    recipient = db.session.query(EventsNotificationRecipients) \
                                        .filter_by(notification_id=x) \
                                        .join(EventsNotificationData) \
                                        .filter_by(deleted=0) \
                                        .first()

                    # check if the recipient requires an email to be sent
                    if (recipient.notify_data[0].notify_mode == 1) or (recipient.notify_data[0].notify_mode == 3):
                        print('Will now send an email to %s' % recipient.recipient_email.lower())
                        # print(recipient.notify_data)

                        # r = requests.post('http://10.17.100.199:9119/sendmail/', data={'subject': recipient.notify_data[0].notify_title,
                        r = requests.post('http://10.6.100.199:9119/sendmail/', data={'subject': recipient.notify_data[0].notify_title,
                                                                                       'body': recipient.notify_data[0].notify_message,
                                                                                       'recipients': recipient.recipient_email.lower()})
                        # don't care about responses r.text, r.status_code and r.reason

                    # check if the recipient requires an SMS to be sent
                    if (recipient.notify_data[0].notify_mode == 2) or (recipient.notify_data[0].notify_mode == 3):
                        print('Will now send an SMS to %s' % recipient.recipient_phone)

                        # r = requests.post('http://10.17.100.199:8080', data={'message': recipient.notify_data[0].notify_message,
                        r = requests.post('http://10.6.100.199:8080', data={'message': recipient.notify_data[0].notify_message,
                                                                            'numbers': recipient.recipient_phone})
                        # don't care about responses r.text, r.status_code and r.reason



            return jsonify(event_id)

        else:
            return jsonify('None')
        # return {'OK, Got it. Next...'}

    if request.method == 'GET':
        return '/Event Not Available'

