from flask import request, jsonify
from eventnotipy import app
from eventnotipy.api import api_route
from eventnotipy.config import sms_host, sms_localhost, email_host, email_localhost
from eventnotipy.models import db
from eventnotipy.models import EventsNotificationConditions, EventsNotificationData, \
                               EventsNotificationRecipients, EventsNotificationRules, \
                               EventsData, EventsImpactData, EventsStatusData, EventsSystemData, \
                               EventsBeamModeData, EventsGroups, EventsContributors, \
                               EventsSubSystemData, EventsOncallData, EventsOncallNames, \
                               ElogGroupData, ElogBeamModeData, \
                               Templates, SolUsers
from string import Template
import pprint
import requests
import time

app.register_blueprint(api_route, url_prefix='/api/v1')

pp = pprint.PrettyPrinter(indent=4)


@app.route('/')
def hello_world():
    return 'Access Denied!'


# <change type> = 'on_create', 'on_update'
@app.route('/event/<change_type>/<int:event_id>', methods=['GET', 'POST'])
def on_change(change_type, event_id):
    if request.method == 'POST':

        if event_id:
            print(time.strftime('%Y-%m-%d %H:%M:%S'))
            print('Processing a %s request for event #%s' % (change_type, event_id))

            print(event_id)
            events_data = db.session.query(EventsData).filter(EventsData.event_id == event_id).first()
            # pp.pprint(events_data.__dict__)

            # if the event can be found continue...
            if events_data:
                print('Event Recieved! Checking for active notifications...')

                data_rules = db.session.query(EventsNotificationRules) \
                            .join(EventsNotificationData, EventsNotificationRules.notification_id == EventsNotificationData.notify_id) \
                            .all()

                # use a set as we don't care about duplicates
                notify_list = set()
                add_list = set()
                rem_list = set()
                for rule in data_rules:
                    # Before checking anything make sure the rule is not deleted and it's active
                    if rule.notify_data[0].deleted == 0 and rule.notify_data[0].notify_active == 1:
                        # check for matches against Group
                        if rule.rule_condition == 1:
                            print('Found a Group Match gid: %s, notify_id: %s' % (events_data.group_id, rule.notification_id))

                            data = EventsGroups.query.filter_by(event_id=events_data.event_id).all()
                            for d in data:
                                # print(d.event_group_id)
                                group = ElogGroupData.query.filter_by(group_id=d.event_group_id).first()
                                print('Group Name: %s' % group.group_title)
                                print('Trying to determine the operator')
                                # print(group.group_title,rule.rule_value)
                                if rule.rule_operator == 'EQ':
                                    # equal condition
                                    if rule.rule_value == group.group_title:
                                        print('Found a Group Match [Equal]: %s' % rule.rule_value)
                                        add_list.add(rule.notification_id)
                                elif rule.rule_operator == 'NE':
                                    # not equal condition
                                    if rule.rule_value == group.group_title:
                                        print('Found a Group Match [Not Equal]: %s' % rule.rule_value)
                                        rem_list.add(rule.notification_id)
                                    else:
                                        add_list.add(rule.notification_id)
                                else:
                                    print('Found a Group Match, but could not determine the operator')

                        # check for matches against System
                        elif rule.rule_condition == 2:
                            print('Found a System Match')
                            system = EventsSystemData.query.filter_by(system_id=events_data.system).first()
                            # print(system.system_name, rule.rule_value)
                            print('Trying to determine the operator')
                            if rule.rule_operator == 'EQ':
                                # equal condition
                                if rule.rule_value == system.system_name:
                                    print('Found a System Match [Equal]: %s' % rule.rule_value)
                                    add_list.add(rule.notification_id)
                            elif rule.rule_operator == 'NE':
                                # not equal condition
                                if rule.rule_value == system.system_name:
                                    print('Found a System Match [Not Equal]: %s' % rule.rule_value)
                                    rem_list.add(rule.notification_id)
                                else:
                                    add_list.add(rule.notification_id)
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
                                print('EQ %s %s' % (rule.rule_value, status.status_name))
                                if rule.rule_value == status.status_name:
                                    print('Found a Status Match [Equal]: %s') % rule.rule_value
                                    add_list.add(rule.notification_id)
                            elif rule.rule_operator == 'NE':
                                # not equal condition
                                print('NE %s %s' % (rule.rule_value, status.status_name))
                                if rule.rule_value == status.status_name:
                                    print('Found a Status Match [Not Equal]: %s') % rule.rule_value
                                    # if rule.notification_id in notify_list:
                                    #     print('Removing %s from the notifications list' % rule.notification_id)
                                    rem_list.add(rule.notification_id)
                                else:
                                    add_list.add(rule.notification_id)
                            else:
                                print('Found a Status Match, but could not determine the operator')

                        # check for matches against Impact
                        elif rule.rule_condition == 4:
                            print('Found an Impact Match')
                            # fetch the impact description from the impact_id
                            impact = EventsImpactData.query.filter_by(impact_id=events_data.impact).first()
                            # print(impact.impact_name, rule.rule_value)
                            print('Trying to determine the operator')
                            if rule.rule_operator == 'EQ':
                                print('EQ %s' % impact.impact_name)
                                # equal condition
                                if rule.rule_value == impact.impact_name:
                                    print('Found an Impact Match [Equal]: %s') % rule.rule_value
                                    add_list.add(rule.notification_id)
                            elif rule.rule_operator == 'NE':
                                print('NE %s %s' % (rule.rule_value, impact.impact_name))
                                # not equal condition
                                if rule.rule_value == impact.impact_name:
                                    print('Found an Impact Match [Not Equal]: %s') % rule.rule_value
                                    # if rule.notification_id in notify_list:
                                    #     print('Removing %s from the notifications list' % rule.notification_id)
                                    rem_list.add(rule.notification_id)
                                else:
                                    add_list.add(rule.notification_id)
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
                                    add_list.add(rule.notification_id)
                            elif rule.rule_operator == 'NE':
                                # not equal condition
                                if rule.rule_value == mode.beam_mode_name:
                                    print('Found a Beam Mode Match [Not Equal]: %s') % rule.rule_value
                                    # if rule.notification_id in notify_list:
                                    #     print('Removing %s from the notifications list' % rule.notification_id)
                                    rem_list.add(rule.notification_id)
                                else:
                                    add_list.add(rule.notification_id)
                            else:
                                print('Found a Beam Mode Match, but could not determine the Operator')
                        else:
                            print('No Matches Found')

                    else:
                        print('Sorry notification #%s has been deleted or disabled' % rule.notification_id)

                print('The following notifications were matched:')
                # notify list contains the notify_ids of the matched rules...
                for item in add_list:
                    if item not in rem_list:
                        notify_list.add(item)

                print('add: %s, remove: %s, final: %s' % (add_list, rem_list, notify_list))

                ########################################################################################################
                # now we have the matched rules, get the details and send out the message

                on_create = False
                on_update = False

                if change_type == 'on_create':
                    on_create = True

                if change_type == 'on_update':
                    on_update = True

                sent_email_list = []
                sent_sms_list = []

                for x in notify_list:
                    # recipient = EventsNotificationRecipients.query.filter_by(notification_id=x).first()
                    # recipients = db.session.query(EventsNotificationRecipients) \
                    #                     .filter_by(notification_id=x) \
                    #                     .join(EventsNotificationData) \
                    #                     .filter_by(deleted=0) \
                    #                     .all()
                    recipients = db.session.query(EventsNotificationRecipients) \
                                          .filter_by(notification_id=x).all()

                    for recipient in recipients:
                        print(recipient.recipient_email.lower())

                        # Gather generic data from the db for both cases...
                        # Fetch the Impact data
                        impact = EventsImpactData.query.filter_by(impact_id=events_data.impact).first()
                        #  Fetch status
                        stat = EventsStatusData.query.filter_by(status_id=events_data.status).first()

                        # check if the recipient requires an email to be sent
                        if (recipient.notify_data[0].notify_mode == 1) or (recipient.notify_data[0].notify_mode == 3):
                            # check which notifications are required on_update or on_create

                            if ((on_create) and (recipient.notify_data[0].notify_submitted == 1)) or ((on_update) and (recipient.notify_data[0].notify_updated == 1)):
                                if recipient.recipient_email:
                                    if recipient.recipient_name not in sent_email_list:
                                        print('Sent emails: %s' % sent_email_list)

                                        template = Templates.query.filter_by(deleted=0).filter_by(title=impact.impact_name).first()

                                        # Fetch the contributors
                                        contributors = EventsContributors.query.filter_by(event_id=events_data.event_id).all()
                                        contrib_string = ''
                                        for i in contributors:
                                            tmp = SolUsers.query.filter_by(id=i.event_contributor_id).first()
                                            contrib_string += tmp.name + ', '

                                        # Fetch the oncall data
                                        oncall_string = ''
                                        if events_data.on_call:
                                            oncall_ids = str(events_data.on_call).split(',')

                                            for oid in oncall_ids:
                                                tmp = EventsOncallData.query.filter_by(oncall_id=oid).first()
                                                tmp2 = EventsOncallNames.query.filter_by(oncall_id=tmp.person).first()
                                                oncall_string += tmp2.oncall_name + ', '

                                        #  Fetch system
                                        sys = EventsSystemData.query.filter_by(system_id=events_data.system).first()

                                        #  Fetch Sub System data
                                        sub = EventsSubSystemData.query.filter_by(sub_system_id=events_data.sub_system).first()

                                        #  Fetch the beam mode
                                        mode = EventsBeamModeData.query.filter_by(beam_mode_id=events_data.beam_mode).first()

                                        # Generate the optime in HH:MM
                                        m, s = divmod(events_data.optime, 60)
                                        hh, mm = divmod(m, 60)
                                        opt = '%02d:%02d' % (hh, mm)

                                        # generate the template conversion
                                        body_text = Template(template.body)
                                        body_format = body_text.safe_substitute(event_id=events_data.event_id,
                                                             event_impact=impact.impact_name,
                                                             event_diff=events_data.end_date - events_data.start_date,
                                                             event_system=sys.system_name,
                                                             event_status=stat.status_name,
                                                             event_sub_system=sub.sub_system_name,
                                                             event_beam_mode=mode.beam_mode_name,
                                                             event_contributors=contrib_string[:-2],
                                                             event_optime=opt,
                                                             event_oncall_str=oncall_string[:-2],
                                                             event_description=events_data.description,
                                                             event_resolution=events_data.resolution,
                                                             event_actions=events_data.actions)

                                        # print(body_format)

                                        print('Will now send an %s email to %s' % (change_type, recipient.recipient_email.lower()))

                                        # r = requests.post('http://%s:9119/sendmail/' % email_localhost, data={'subject': recipient.notify_data[0].notify_title,
                                        r = requests.post('http://%s:9119/sendmail/' % email_host, data={'subject': events_data.title,
                                                                                                         'from': 'JOE',
                                                                                                         'body': body_format,
                                                                                                         'recipients': recipient.recipient_email.lower()})
                                        # # don't care about responses r.text, r.status_code and r.reason
                                        # add recipient to the already sent list
                                        sent_email_list.append(recipient.recipient_name)

                                    else:
                                        print('Already sent email to %s for JOE_ID=%s. I refuse to send this message again' % (recipient.recipient_name, events_data.event_id))
                                else:
                                    print('No email address provided. Unable to send message.')
                            else:
                                print('Email %s not sent because [notify_submitted] == 0 OR [notify_updated] == 0' % change_type)

                        # check if the recipient requires an SMS to be sent
                        if (recipient.notify_data[0].notify_mode == 2) or (recipient.notify_data[0].notify_mode == 3):
                            # check which notifications are required on_update or on_create

                            if ((on_create) and (recipient.notify_data[0].notify_submitted == 1)) or ((on_update) and (recipient.notify_data[0].notify_updated == 1)):
                                if recipient.recipient_phone:
                                    if recipient.recipient_name not in sent_sms_list:
                                        print('Sent SMS %s' % sent_sms_list)

                                        body_text = Template("Hello JOE\n$event_title\nJOE id: $event_id\nStatus: $event_status")
                                        body_format = body_text.safe_substitute(event_id=events_data.event_id,
                                                                                event_status=stat.status_name,
                                                                                event_title=events_data.title
                                                                                )

                                        print('Will now send an %s SMS to %s' % (change_type, recipient.recipient_phone))

                                        # r = requests.post('http://%s:8080' % sms_localhost, data={'message': recipient.notify_data[0].notify_message,
                                        r = requests.post('http://%s:8080' % sms_host, data={'message': body_format,
                                                                                            'numbers': recipient.recipient_phone})
                                        # don't care about responses r.text, r.status_code and r.reason
                                        sent_sms_list.append(recipient.recipient_name)
                                    else:
                                        print('Already sent SMS to %s for JOE_ID=%s. I refuse to waste money sending it again' % (recipient.recipient_name, events_data.event_id))
                                else:
                                    print('No phone number provided. Unable to send SMS.')
                            else:
                                print('SMS %s not sent because [notify_submitted] == 0 OR [notify_updated] == 0' % change_type)

            date = time.strftime('%Y-%m-%d %H:%M:%S')
            print('Notifications Completed: %s' % date)
            return jsonify(event_id)

        else:
            return jsonify('None')
        # return {'OK, Got it. Next...'}

    if request.method == 'GET':
        return '/Event Not Available'

