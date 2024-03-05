from tortoise import Model, fields


class Referals(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=128)
    count = fields.IntField(default=0)
    clicked = fields.IntField(default=0)
    price = fields.IntField(default=0)

    class Meta:
        table = 'refs'


class Subs(Model):
    id = fields.IntField(pk=True)
    subbed = fields.IntField(default=0)
    channel_name = fields.TextField(null=True)
    channel_id = fields.BigIntField()
    url = fields.CharField(max_length=256)
    token = fields.TextField(null=True)
    type = fields.TextField(default='channel')

    class Meta:
        table = 'subs'


class Greetings(Model):
    id = fields.IntField(pk=True, index=True)
    text = fields.TextField()
    markup = fields.JSONField(default="[]")

    class Meta:
        table = 'greetings'


class Views(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=128)
    viewed = fields.IntField(default=0)
    max_viewed = fields.IntField(default=0)
    status = fields.IntField(default=1)
    from_user = fields.BigIntField()
    message_id = fields.BigIntField()
    inline_mode = fields.BigIntField(default=0)
    viewed_users = fields.JSONField(default="[]")
    markup = fields.JSONField(default="[]")
    msg = fields.CharField(max_length=4096)

    class Meta:
        table = 'views'


class Users(Model):
    id = fields.BigIntField(pk=True, generated=False, index=True)

    first_name = fields.TextField()
    username = fields.CharField(max_length=64, null=True)
    ref = fields.CharField(max_length=128, null=True)
    subbed = fields.IntField(default=0)
    subbed_count = fields.IntField(default=0)
    valid = fields.SmallIntField(default=1)
    reg_time = fields.BigIntField(null=False)
    last_started = fields.BigIntField(null=False)
    last_active = fields.BigIntField(default=0)
    banned = fields.SmallIntField(default=0)

    my_tests: fields.ReverseRelation["Tests"]

    class Meta:
        table = 'users'


class Groups(Model):
    id = fields.BigIntField(pk=True, generated=False, index=True)
    title = fields.TextField()
    username = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    ref = fields.TextField(null=True)

    class Meta:
        table = 'groups'


class Tests(Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.TextField()
    template = fields.TextField(max_length=200)
    pass_counter = fields.BigIntField(default=0)
    category = fields.CharField(max_length=64, index=True)
    cover_img_url = fields.TextField(null=True)

    owner: fields.ForeignKeyNullableRelation[Users] = fields.ForeignKeyField(
        'models.Users', related_name='my_tests', null=True
    )
    answers: fields.ReverseRelation["Answers"]

    class Meta:
        table = 'tests'


class Answers(Model):
    id = fields.BigIntField(pk=True)
    text = fields.CharField(max_length=200)
    cover_img_url = fields.TextField(null=True)

    test: fields.ForeignKeyRelation[Tests] = fields.ForeignKeyField(
        'models.Tests', related_name='answers'
    )

    class Meta:
        table = 'answers'

class AnonChat(Model):
    id = fields.BigIntField(pk=True)

    user_id = fields.BigIntField()
    gender = fields.TextField()
    interests = fields.TextField()
    age = fields.IntField()
    status = fields.TextField()

    partner_id = fields.BigIntField()
    class Meta:
        table = 'anonchat'

class DefaultTests(Model):
    id = fields.BigIntField(pk=True)

    owner = fields.BigIntField()
    test_type = fields.TextField()
    answers = fields.JSONField(default='[]')

    class Meta:
        table = 'default_tests'

class DefaultAnswers(Model):
    id = fields.BigIntField(pk=True)
    answered = fields.BigIntField()

    owner = fields.BigIntField()
    test_type = fields.TextField()
    answers = fields.JSONField(default='[]')

    class Meta:
        table = 'default_answers'