# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flatman import app, db
from flatman.models import *
from datetime import datetime, timedelta
import random

db.drop_all()
db.create_all()

group = Group()
group.name = "Fernsehstudio"

jauch = User()
jauch.username = "jauch"
jauch.displayname = u"Günther Jauch"
jauch.password = "hunter2"
jauch.email = "jauch@example.com"
jauch.group = group

gause = User()
gause.username = "gause"
gause.displayname = "Gundula Gause"
gause.password = "hunter2"
gause.email = "gause@example.com"
gause.group = group

raab = User()
raab.username = "raab"
raab.displayname = "Stefan Raab"
raab.password = "hunter2"
raab.email = "raab@example.com"
raab.group = group

task = Task()
task.title = "Kaffe kochen"
task.description = "2 Liter pro Stunde, stark"
task.repeating = "interval"
task.assignment = "one"
task.skippable = False
task.interval_days = 1
task.interval_start = datetime(2014, 4, 6, 12, 00)
task.assignee = gause
task.group = group

task = Task()
task.title = "Staubsaugen"
task.description = u"Wöchentlich müssen Studiofußboden, Gang, Geräteraum, Umkleide und der Aufzug gesaugt und bei Bedarf gewischt werden."
task.repeating = "interval"
task.assigment = "order"
task.skippable = False
task.interval_days = 7
task.interval_start = datetime(2014, 3, 31, 16, 00)
task.deadline = datetime(2014, 4, 7, 16, 00)
task.assignee = jauch
task.group = group

task = Task()
task.title = u"Müll rausbringen"
task.description = u""
task.repeating = "ondemand"
task.assignment = "one"
task.assignee = jauch
task.group = group

task = Task()
task.title = "Neue Krawatten kaufen"
task.description = u"Bitte ein paar hübsche, bunte Krawatten, und vielleicht ein zwei Fliegen."
task.repeating = "single"
task.assignment = "all"
task.deadline = datetime(2014, 4, 21)
task.group = group

task = Task()
task.title = "Putzmittel kaufen"
task.description = u""
task.repeating = "ondemand"
task.assignment = "order"
task.skippable = False
task.assignee = gause
task.group = group


aldi = ShoppingCategory("ALDI", group)
edeka = ShoppingCategory("Edeka", group)
sonstiges = ShoppingCategory("Sonstiges", group)

item = ShoppingItem("1kg", "Tomaten", aldi)
item = ShoppingItem("2 Dosen", "Mais", aldi)
item = ShoppingItem("", "Frischeiwaffeln", aldi)
item = ShoppingItem("1", "Bohrmaschine").group = group
item = ShoppingItem("2 Flaschen", u"Holunderblütensirup", edeka).description = u"Den für 2.95€ gleich links um die Ecke im Regal, oben rechts, beim Himbeersaft."

db.session.add(group)
db.session.commit()
