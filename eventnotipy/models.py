from eventnotipy.database import db
from sqlalchemy.dialects.mysql import TINYINT

class EventsNotificationRecipients(db.Model):
    __tablename__ = 'events_notification_recipients'

    notification_id = db.Column(TINYINT(11), primary_key=True)
    recipient_name = db.Column(db.String)
    recipient_email = db.Column(db.String)
    recipient_phone = db.Column(db.Integer, primary_key=True)

class EventsNotificationData(db.Model):
    __tablename__ = 'events_notification_data'

    notification_id = db.Column(db.Integer, primary_key=True)
    notify_reporter_id = db.Column(TINYINT(11))
    notify_title = db.Column(db.Text)
    notify_submitted = db.Column(TINYINT(11))
    notification_updated = db.Column(TINYINT(11))
    notification_mode = db.Column(TINYINT(11))
    notification_message = db.Column(db.Text)
    notification_date_added = db.Column(db.DateTime)
    notification_date_modified = db.Column(db.DateTime)
    notification_date_deleted = db.Column(db.DateTime)
    notification_active = db.Column(TINYINT(11))


class EventsNotificationConditions(db.Model):
    __tablename__ = 'events_notification_conditions_data'

    condition_id = db.Column(db.Integer, primary_key=True)
    condition_name = db.Column(db.Text)
    condition_operators = db.Column(db.Text)


class EventsNotificationRules(db.Model):
    __tablename__ = 'events_notification_rules'

    notification_id = db.Column(TINYINT(11), primary_key=True)
    rule_condition = db.Column(db.Text)
    rule_operator = db.Column(db.Text)
    rule_value = db.Column(db.Text)