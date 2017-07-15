from eventnotipy.database import db
from sqlalchemy.dialects.mysql import TINYINT


class EventsGroups(db.Model):
    __tablename__ = 'events_groups'

    event_id = db.Column(db.Integer, primary_key=True)
    event_group_id = db.Column(db.Integer, primary_key=True)


class EventsNotificationRecipients(db.Model):
    __tablename__ = 'events_notification_recipients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    notification_id = db.Column(TINYINT(11), primary_key=True)
    # type_id = db.Column(db.Integer, primary_key=True)
    recipient_name = db.Column(db.String)
    recipient_email = db.Column(db.String)
    recipient_phone = db.Column(db.Integer)

    notify_data = db.relationship('EventsNotificationData')

    def __repr__(self):
        return '[notification_id] %r, [recipient_name] %r, [recipient_email] %r, [recipient_phone] %r' % \
               (self.notification_id,self.recipient_name,self.recipient_email,self.recipient_phone)


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

    def __repr__(self):
        return '[notify_id] %r, [notify_title] %r, [deleted] %r' % (self.notify_id,self.notify_title,self.deleted)


class EventsNotificationRules(db.Model):
    __tablename__ = 'events_notification_rules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    notification_id = db.Column(TINYINT(11), primary_key=True)
    rule_condition = db.Column(db.Integer, db.ForeignKey('events_notification_conditions_data.condition_id'), primary_key=True)
    rule_operator = db.Column(db.Text)
    rule_value = db.Column(db.Text)

    notify_data = db.relationship('EventsNotificationData')
    # conditions = db.relationship('EventsNotificationConditions')

    def __repr__(self):
        return '[notification_id] %r, [rule_condition] %r, [rule_operator] %r, [rule_value] %r, [notify_data] %r' \
               % (self.notification_id,self.rule_condition,self.rule_operator,self.rule_value,self.notify_data)


class EventsNotificationConditions(db.Model):
    __tablename__ = 'events_notification_conditions_data'

    condition_id = db.Column(db.Integer, primary_key=True)
    condition_name = db.Column(db.Text)
    condition_operators = db.Column(db.Text)

    rules = db.relationship(EventsNotificationRules)


class EventsContributors(db.Model):
    __table_name__ = 'events_contributors'

    event_id = db.Column(db.Integer, db.ForeignKey('events_data.event_id'), primary_key=True)
    event_contributor_id = db.Column(db.Integer, db.ForeignKey('sol_users.id'), primary_key=True)


class EventsData(db.Model):
    __tablename__ = 'events_data'

    event_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    reported_by = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    optime = db.Column(db.Integer)
    group_id = db.Column(TINYINT(3), db.ForeignKey('elog_group_data.group_id'))  # to be deleted
    impact = db.Column(TINYINT(3), db.ForeignKey('events_impact_data.impact_id'))
    system = db.Column(db.Integer, db.ForeignKey('events_system_data.system_id'))
    sub_system = db.Column(db.Text)
    sub_system_name = db.Column(db.Text)
    device = db.Column(db.Text)
    title = db.Column(db.Text)
    contributors = db.Column(db.Text) # to be deleted...
    description = db.Column(db.Text)
    resolution = db.Column(db.Text)
    actions = db.Column(db.Text)
    status = db.Column(TINYINT(3), db.ForeignKey('events_status_data.status_id'))
    linked_content = db.Column(TINYINT(3))
    on_call = db.Column(db.Text)
    beam_mode = db.Column(TINYINT(3))
    notify = db.Column(db.Integer)
    elog = db.Column(db.Integer)
    elog_id = db.Column(db.Integer)
    deleted = db.Column(db.Integer)

    contributor_name = db.relationship(EventsContributors)


class EventsImpactData(db.Model):
    __tablename__ = 'events_impact_data'

    impact_id = db.Column(TINYINT(3),primary_key=True,autoincrement=True)
    impact_name = db.Column(db.Text)
    impact_category = db.Column(db.Integer)


class EventsStatusData(db.Model):
    __tablename__ = 'events_status_data'

    status_id = db.Column(TINYINT(3), primary_key=True, autoincrement=True)
    status_name = db.Column(db.Text)


class EventsSystemData(db.Model):
    __tablename__ = 'events_system_data'

    system_id = db.Column(TINYINT(3), primary_key=True, autoincrement=True)
    system_name = db.Column(db.Text)
    system_category = db.Column(db.Integer)


class EventsBeamModeData(db.Model):
    __tablename__ = 'events_beam_mode_data'

    beam_mode_id = db.Column(TINYINT(3),primary_key=True)
    beam_mode_name = db.Column(db.Text)


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


class Templates(db.Model):
    __tablename__ = 'templates'

    template_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255))
    body = db.Column(db.Text)
    group_id = db.Column(db.Integer)
    created = db.Column(db.TIMESTAMP)
    edited = db.Column(db.TIMESTAMP)
    user_id = db.Column(db.Integer)
    sort = db.Column(db.Integer)
    deleted = db.Column(TINYINT(3))


class SolUsers(db.Model):
    __tablename__ = 'sol_users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    username = db.Column(db.String(150))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(10))
    password = db.Column(db.String(100))
    gid = db.Column(db.Integer)
    registerDate = db.Column(db.DateTime)
    lastvisitDate = db.Column(db.DateTime)
    elog_hide_important = db.Column(TINYINT(4))
    elog_collapse_all = db.Column(TINYINT(4))
    elog_entries_per_page = db.Column(db.Integer)
    site_nickname = db.Column(db.String)
    elog_simple_editor = db.Column(TINYINT(4))
    elog_shadow_boxer = db.Column(TINYINT(11))
    elog_show_keywords = db.Column(TINYINT(1))
    elog_date_format = db.Column(db.String)
    guest = db.Column(TINYINT(4))
    operator = db.Column(TINYINT(4))
    active = db.Column(db.Integer)


class ElogBeamModeData(db.Model):
    __tablename__ = 'elog_beam_mode_data'

    beam_mode_id = db.Column(TINYINT(3),autoincrement=True,primary_key=True)
    beam_mode_title = db.Column(db.Text)