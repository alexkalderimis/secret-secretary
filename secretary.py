import smtplib
from email.mime.text import MIMEText
import yaml
import random
import os
import sys

def inform_santae(text, santae, codenames):

    s = smtplib.SMTP('ppsw.cam.ac.uk')

    for santa in santae:
        giver = santa.giver
        recipient = santa.recipient
        codename = codenames[giver]

        msg = MIMEText(text.format(
            giver.name,
            codename,
            recipient.name,
            "the 13th of December"))

        me = "robo.secretary@intermine.org"
        you = giver.email

        msg['Subject'] = 'Secret Santa Mission Assignment'
        msg['From'] = me
        msg['To'] = you

        try:
            print "Sending email to", you
            s.sendmail(me, [you], msg.as_string())
        except Exception as e:
            print "Sending failed: %s" % e

    s.quit()

class StaffMember(object):
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __hash__(self):
        return 7 * hash(self.name) * hash(self.email)

class Santa(object):
    def __init__(self, giver, recipient):
        self.giver = giver
        self.recipient = recipient

    def __hash__(self):
        return 3 * hash(self.giver) * hash(self.recipient)

def log_pairs(santae, codenames):
    for santa in santae:
        giver = santa.giver
        recipient = santa.recipient
        print "%s gives to %s" % (codenames[giver], codenames[recipient])

# Not a hugely efficient algorithm, but perfectly usable for small groups.
def main():
    send_mail = "send" in sys.argv
    with open("data/participants.yaml", "r") as f:
        staff = [StaffMember(name, email) for name, email in yaml.load(f.read()).items()]
    with open("data/reindeer.yaml", "r") as f:
        reindeer = yaml.load(f.read())
    with open("data/message.text", "r") as f:
        message_templ = f.read()

    givers = set(staff)
    recipients = set(staff)
    codenames = dict(zip(staff, random.sample(reindeer, len(staff))))
    santae = []

    # Pair up each giver to a recipient, but none to themselves.
    n = 0
    max_n = len(givers) * len(givers)
    while len(givers):
        n = n + 1
        if n > max_n: # Probably reached an impass at the end, reset
            givers = set(staff)
            recipients = set(staff)
            santae = []
            n = 0
        else:
            giver = random.choice(list(givers))
            recipient = random.choice(list(recipients))
            if giver is not recipient:
                givers.remove(giver)
                recipients.remove(recipient)
                santae.append(Santa(giver, recipient))

    log_pairs(santae, codenames)
    if send_mail:
        inform_santae(message_templ, santae, codenames)

if __name__ == "__main__":
    main()
