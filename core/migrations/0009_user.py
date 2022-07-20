# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150911_0924'),
    ]

    operations = [
        migrations.RunSQL(
            '''
            DO $$
            BEGIN
            IF NOT EXISTS (SELECT relname FROM pg_class WHERE relname='core_user') THEN 
                CREATE TABLE "core_user" ("id" serial NOT NULL PRIMARY KEY, "password" varchar(128) NOT NULL, "last_login" timestamp with time zone NULL, "is_superuser" boolean NOT NULL, "email" varchar(255) NOT NULL UNIQUE, "is_staff" boolean NOT NULL, "is_active" boolean NOT NULL, "date_joined" timestamp with time zone NOT NULL);
                CREATE TABLE "core_user_groups" ("id" serial NOT NULL PRIMARY KEY, "user_id" integer NOT NULL, "group_id" integer NOT NULL, UNIQUE ("user_id", "group_id"));
                CREATE TABLE "core_user_user_permissions" ("id" serial NOT NULL PRIMARY KEY, "user_id" integer NOT NULL, "permission_id" integer NOT NULL, UNIQUE ("user_id", "permission_id"));
                CREATE INDEX "core_user_email_2e990014d0f3994e_like" ON "core_user" ("email" varchar_pattern_ops);
                ALTER TABLE "core_user_groups" ADD CONSTRAINT "core_user_groups_user_id_5705f02eb1c0e97e_fk_core_user_id" FOREIGN KEY ("user_id") REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED;
                ALTER TABLE "core_user_groups" ADD CONSTRAINT "core_user_groups_group_id_60c277e676aaba04_fk_auth_group_id" FOREIGN KEY ("group_id") REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED;
                CREATE INDEX "core_user_groups_e8701ad4" ON "core_user_groups" ("user_id");
                CREATE INDEX "core_user_groups_0e939a4f" ON "core_user_groups" ("group_id");
                ALTER TABLE "core_user_user_permissions" ADD CONSTRAINT "core_user_user_permissi_user_id_74bb4fb73b3dbed_fk_core_user_id" FOREIGN KEY ("user_id") REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED;
                ALTER TABLE "core_user_user_permissions" ADD CONSTRAINT "core_user__permission_id_7f7434aef5769519_fk_auth_permission_id" FOREIGN KEY ("permission_id") REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED;
                CREATE INDEX "core_user_user_permissions_e8701ad4" ON "core_user_user_permissions" ("user_id");
                CREATE INDEX "core_user_user_permissions_8373b171" ON "core_user_user_permissions" ("permission_id");
            END IF;
            END$$;
            '''
        ),
    ]
