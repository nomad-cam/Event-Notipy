from eventnotipy.database import db
from sqlalchemy.dialects.mysql import TINYINT

class EventsNotificationRecipients(db.Model):
    __tablename__ = 'events_notification_recipients'

    notification_id = db.Column(TINYINT(11), primary_key=True)
    type_id = db.Column(db.Integer, primary_key=True)
    recipient_name = db.Column(db.String)
    recipient_email = db.Column(db.String)
    recipient_phone = db.Column(db.Integer)

class EventsNotificationData(db.Model):
    __tablename__ = 'events_notification_data'

    notify_id = db.Column(db.Integer, db.ForeignKey('events_notification_rules.notification_id'),
                          db.ForeignKey('events_notification_recipients.notification_id'), primary_key=True)
    notify_type = db.Column(db.Integer)
    notify_reporter_id = db.Column(TINYINT(11))
    notify_title = db.Column(db.Text)
    notify_submitted = db.Column(TINYINT(11))
    notify_updated = db.Column(TINYINT(11))
    notify_mode = db.Column(TINYINT(11))
    notify_message = db.Column(db.Text)
    notify_date_added = db.Column(db.DateTime)
    notify_date_modified = db.Column(db.DateTime)
    notify_date_deleted = db.Column(db.DateTime)
    notify_active = db.Column(TINYINT(11))
    deleted = db.Column(db.Integer)

    rules = db.relationship('EventsNotificationRules')


class EventsNotificationRules(db.Model):
    __tablename__ = 'events_notification_rules'

    notification_id = db.Column(TINYINT(11), primary_key=True)
    rule_condition = db.Column(db.Integer, db.ForeignKey('events_notification_conditions_data.condition_id'))
    rule_operator = db.Column(db.Text)
    rule_value = db.Column(db.Text)

    conditions = db.relationship('EventsNotificationConditions')


class EventsNotificationConditions(db.Model):
    __tablename__ = 'events_notification_conditions_data'

    condition_id = db.Column(db.Integer, primary_key=True)
    condition_name = db.Column(db.Text)
    condition_operators = db.Column(db.Text)

    rules = db.relationship(EventsNotificationRules)



class EventsData(db.Model):
    __tablename__ = 'events_data'

    event_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    reported_by = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    group_id = db.Column(TINYINT(3), db.ForeignKey('elog_group_data.group_id'))
    impact = db.Column(TINYINT(3))
    system = db.Column(db.Integer)
    sub_system = db.Column(db.Text)
    title = db.Column(db.Text)
    contributors = db.Column(db.Text)
    description = db.Column(db.Text)
    resolution = db.Column(db.Text)
    actions = db.Column(db.Text)
    status = db.Column(TINYINT(3))
    linked_content = db.Column(TINYINT(3))
    on_call = db.Column(db.Text)
    beam_mode = db.Column(TINYINT(3))
    notify = db.Column(db.Integer)
    elog = db.Column(db.Integer)
    elog_id = db.Column(db.Integer)
    deleted = db.Column(db.Integer)


class ElogGroupData(db.Model):
    __tablename__ = 'elog_group_data'

    group_id = db.Column(TINYINT(3),primary_key=True)
    group_title = db.Column(db.Text)
    group_type = db.Column(TINYINT(1), primary_key=True)
    sort = db.Column(db.SmallInteger, primary_key=True)
    private = db.Column(TINYINT(1), primary_key=True)
    urlName = db.Column(db.Text)
    oncall = db.Column(db.Integer, primary_key=True)
    ldap_group_name = db.Column(db.Text)

class ElogBeamModeData(db.Model):
    __tablename__ = 'elog_beam_mode_data'

    beam_mode_id = db.Column(TINYINT(3),primary_key=True)
    beam_mode_title = db.Column(db.Text)