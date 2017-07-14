from flask import request,jsonify
from eventnotipy import app
from eventnotipy.config import sms_host,sms_localhost,email_host,email_localhost
from eventnotipy.models import db
from eventnotipy.models import EventsNotificationConditions,EventsNotificationData, \
                               EventsNotificationRecipients,EventsNotificationRules, \
                               EventsData,EventsImpactData,EventsStatusData,EventsSystemData, \
                               EventsBeamModeData, \
                               ElogGroupData
import pprint
import requests
import time

pp = pprint.PrettyPrinter(indent=4)

@app.route('/')
def hello_world():
    return 'Access Denied!'

# <change type> = 'on_create', 'on_update'
@app.route('/event/<change_type>/<int:event_id>', methods=['GET','POST'])
def on_change(change_type,event_id):
    if request.method == 'POST':

        if event_id:
            print(time.strftime('%Y-%m-%d %H:%M:%S'))
            print('Processing a %s request for event #%s' % (change_type,event_id))

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
                    # Before checking anything make sure the rule is not deleted and it's active
                    if rule.notify_data[0].deleted == 0 and rule.notify_data[0].notify_active == 1:
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
                                    print('Found a Status Match [Equal]: %s') % rule.rule_value
                                    notify_list.add(rule.notification_id)
                            elif rule.rule_operator == 'NE':
                                # not equal condition
                                if rule.rule_value != status.status_name:
                                    print('Found a Status Match [Not Equal]: %s') % rule.rule_value
                                    notify_list.add(rule.notification_id)
                            else:
                                print('Found a Status Match, but could not determine the operator')


                        # check for matches against Impact
                        elif rule.rule_condition == 4:
                            print('Found an Impact Match')
                            impact = EventsImpactData.query.filter_by(impact_id=events_data.impact).first()
                            # print(impact.impact_name, rule.rule_value)
                            print('Trying to determine the operator')
                            if rule.rule_operator == 'EQ':
                                # equal condition
                                if rule.rule_value == impact.impact_name:
                                    print('Found an Impact Match [Equal]: %s') % rule.rule_value
                                    notify_list.add(rule.notification_id)
                            elif rule.rule_operator == 'NE':
                                # not equal condition
                                if rule.rule_value != impact.impact_name:
                                    print('Found an Impact Match [Not Equal]: %s') % rule.rule_value
                                    notify_list.add(rule.notification_id)
                            else:
                                print('Found a Impact Match, but could not determine the operator')


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

                ########################################################################################################
                # now we have the matched rules, get the details and send out the message

                on_create = False
                on_update = False

                if change_type == 'on_create':
                    on_create = True

                if change_type == 'on_update':
                    on_update = True

                for x in notify_list:
                    # recipient = EventsNotificationRecipients.query.filter_by(notification_id=x).first()
                    # recipients = db.session.query(EventsNotificationRecipients) \
                    #                     .filter_by(notification_id=x) \
                    #                     .join(EventsNotificationData) \
                    #                     .filter_by(deleted=0) \
                    #                     .all()
                    recipients = db.session.query(EventsNotificationRecipients) \
                                          .filter_by(notification_id=x).all()

                    # print(recipients)
                    for recipient in recipients:
                        print(recipient.recipient_email.lower())
                        # check if the recipient requires an email to be sent
                        if (recipient.notify_data[0].notify_mode == 1) or (recipient.notify_data[0].notify_mode == 3):
                            # check which notifications are required on_update or on_create

                            if ((on_create) and (recipient.notify_data[0].notify_submitted == 1)) or ((on_update) and (recipient.notify_data[0].notify_updated == 1)):
                                if recipient.recipient_email:

                                    print('Will now send an %s email to %s' % (change_type,recipient.recipient_email.lower()))

                                    # r = requests.post('http://%s:9119/sendmail/' % email_localhost, data={'subject': recipient.notify_data[0].notify_title,
                                    r = requests.post('http://%s:9119/sendmail/' % email_host, data={'subject': recipient.notify_data[0].notify_title,
                                                                                                   'body': recipient.notify_data[0].notify_message,
                                                                                                   'recipients': recipient.recipient_email.lower()})
                                    # # don't care about responses r.text, r.status_code and r.reason
                                else:
                                    print('No email address provided. Unable to send message.')
                            else:
                                print('Email %s not sent because [notify_submitted] == 0 OR [notify_updated] == 0' % change_type)

                        # check if the recipient requires an SMS to be sent
                        if (recipient.notify_data[0].notify_mode == 2) or (recipient.notify_data[0].notify_mode == 3):
                            # check which notifications are required on_update or on_create

                            if ((on_create) and (recipient.notify_data[0].notify_submitted == 1)) or ((on_update) and (recipient.notify_data[0].notify_updated == 1)):
                                if recipient.recipient_phone:

                                    print('Will now send an %s SMS to %s' % (change_type,recipient.recipient_phone))

                                    # r = requests.post('http://%s:8080' % sms_localhost, data={'message': recipient.notify_data[0].notify_message,
                                    r = requests.post('http://%s:8080' % sms_host, data={'message': recipient.notify_data[0].notify_message,
                                                                                        'numbers': recipient.recipient_phone})
                                    # don't care about responses r.text, r.status_code and r.reason
                                else:
                                    print('No phone number provided. Unable to send SMS.')
                            else:
                                print('SMS %s not sent because [notify_submitted] == 0 OR [notify_updated] == 0' % change_type)


            return jsonify(event_id)

        else:
            return jsonify('None')
        # return {'OK, Got it. Next...'}

    if request.method == 'GET':
        return '/Event Not Available'

