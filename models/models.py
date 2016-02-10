import app_config

from peewee import Model, PostgresqlDatabase
from peewee import BooleanField, CharField, DateField, DateTimeField, DecimalField, ForeignKeyField, IntegerField
from slugify import slugify

db = PostgresqlDatabase(
    app_config.database['PGDATABASE'],
    user=app_config.database['PGUSER'],
    password=app_config.database['PGPASSWORD'],
    host=app_config.database['PGHOST'],
    port=app_config.database['PGPORT']
)


class BaseModel(Model):
    """
    Base class for Peewee models. Ensures they all live in the same database.
    """
    class Meta:
        database = db


class Result(BaseModel):
    id = CharField(primary_key=True)
    unique_id = CharField(null=True)
    raceid = CharField(null=True)
    racetype = CharField(null=True)
    racetypeid = CharField(null=True)
    ballotorder = IntegerField(null=True)
    candidateid = CharField(null=True)
    description = CharField(null=True)
    electiondate = DateField(null=True)
    fipscode = CharField(max_length=5, null=True)
    first = CharField(null=True)
    incumbent = BooleanField(null=True)
    initialization_data = BooleanField(null=True)
    is_ballot_measure = BooleanField(null=True)
    last = CharField(null=True)
    lastupdated = DateTimeField(null=True)
    level = CharField(null=True)
    national = BooleanField(null=True)
    officeid = CharField(null=True)
    officename = CharField(null=True)
    party = CharField(null=True)
    polid = CharField(null=True)
    polnum = CharField(null=True)
    precinctsreporting = IntegerField(null=True)
    precinctsreportingpct = DecimalField(null=True)
    precinctstotal = IntegerField(null=True)
    reportingunitid = CharField(null=True)
    reportingunitname = CharField(null=True)
    runoff = BooleanField(null=True)
    seatname = CharField(null=True)
    seatnum = CharField(null=True)
    statename = CharField(null=True)
    statepostal = CharField(max_length=2)
    test = BooleanField(null=True)
    uncontested = BooleanField(null=True)
    votecount = IntegerField(null=True)
    votepct = DecimalField(null=True)
    winner = BooleanField(null=True)


class Call(BaseModel):
    call_id = ForeignKeyField(Result, related_name='call')
    accept_ap = BooleanField(default=False)
    override_winner = BooleanField(default=False)


class Race(BaseModel):
    id = CharField(null=True)
    raceid = CharField(null=True)
    racetype = CharField(null=True)
    racetypeid = CharField(null=True)
    description = CharField(null=True)
    electiondate = DateField(null=True)
    initialization_data = BooleanField(null=True)
    lastupdated = DateField(null=True)
    national = BooleanField(null=True)
    officeid = CharField(null=True)
    officename = CharField(null=True)
    party = CharField(null=True)
    seatname = CharField(null=True)
    seatnum = CharField(null=True)
    statename = CharField(null=True)
    statepostal = CharField(null=True, max_length=2)
    test = BooleanField(null=True)
    uncontested = BooleanField(null=True)


class ReportingUnit(BaseModel):
    id = CharField(null=True)
    reportingunitid = CharField(null=True)
    reportingunitname = CharField(null=True)
    description = CharField(null=True)
    electiondate = DateField()
    fipscode = CharField(null=True, max_length=5)
    initialization_data = BooleanField(null=True)
    lastupdated = DateField(null=True)
    level = CharField(null=True)
    national = CharField(null=True)
    officeid = CharField(null=True)
    officename = CharField(null=True)
    precinctsreporting = IntegerField(null=True)
    precinctsreportingpct = DecimalField(null=True)
    precinctstotal = IntegerField(null=True)
    raceid = CharField(null=True)
    racetype = CharField(null=True)
    racetypeid = CharField(null=True)
    seatname = CharField(null=True)
    seatnum = CharField(null=True)
    statename = CharField(null=True)
    statepostal = CharField(null=True, max_length=2)
    test = BooleanField(null=True)
    uncontested = BooleanField(null=True)
    votecount = IntegerField(null=True)


class Candidate(BaseModel):
    id = CharField(null=True)
    unique_id = CharField(null=True)
    candidateid = CharField(null=True)
    ballotorder = IntegerField(null=True)
    first = CharField(null=True)
    last = CharField(null=True)
    party = CharField(null=True)
    polid = CharField(null=True)
    polnum = CharField(null=True)


class BallotPosition(BaseModel):
    id = CharField(null=True)
    unique_id = CharField(null=True)
    candidateid = CharField(null=True)
    ballotorder = IntegerField(null=True)
    description = CharField(null=True)
    last = CharField(null=True)
    polid = CharField(null=True)
    polnum = CharField(null=True)
    seatname = CharField(null=True)


class CandidateDelegates(BaseModel):
    level = CharField()
    party_total = IntegerField()
    superdelegates_count = IntegerField()
    last = CharField()
    state = CharField()
    candidateid = CharField()
    party_need = IntegerField()
    party = CharField()
    delegates_count = IntegerField()
    id = CharField()
    d1 = IntegerField()
    d7 = IntegerField()
    d30 = IntegerField()

    def slug(self):
        return slugify(self.last)

    def status(self):
        return self.candidateid not in app_config.DROPPED_OUT

    def pledged_delegates_pct(self):
        estimated_total = app_config.DELEGATE_ESTIMATES[self.party]
        return 100 * ((self.delegates_count - self.superdelegates_count) / float(estimated_total))

    def superdelegates_pct(self):
        estimated_total = app_config.DELEGATE_ESTIMATES[self.party]
        return 100 * (self.superdelegates_count / float(estimated_total))

    def delegates_pct(self):
        estimated_total = app_config.DELEGATE_ESTIMATES[self.party]
        return 100 * (self.delegates_count / float(estimated_total))
