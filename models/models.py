import app_config

from peewee import Model, PostgresqlDatabase
from peewee import BooleanField, CharField, DateField, DecimalField, IntegerField

db = PostgresqlDatabase(
    app_config.DATABASE['name'],
    user=app_config.DATABASE['user'],
    password=app_config.DATABASE['password'],
    host=app_config.DATABASE['host'],
    port=app_config.DATABASE['port']
)


class BaseModel(Model):
    """
    Base class for Peewee models. Ensures they all live in the same database.
    """
    class Meta:
        database = db


class Results(BaseModel):
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
    lastupdated = DateField(null=True)
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