from mailin import Mailin
import csv

m = Mailin("https://api.sendinblue.com/v2.0", "vHmXBYOLTaMIyENj")
email_from = "sunny@auxledger.org"
# email_from = "sagar.tanna@auxesisgroup.com"
# email_from = "Jitender.Bhutani@auxesisgroup.com"
file_path = '/home/auxesis/Downloads/email_test_sample.csv'


def get_html(name):
    body = 'Dear ' + name + ',<br><br>I hope you are doing very well. The year has seen enormous growth in Blockchain Technology where the idea is sky rocketing with its vast possibilities.<br><br>'
    body += "<b><u><a href='https://auxesisgroup.com/'>Auxesis Group</a></u></b>, the global leader in Blockchain services and among <b><u><a href='https://www.rise.global/blockchain-100'>The Top 100 Most Influential Blockchain Company</a></u></b> is evolving its next version of <b><u><a href='https://auxledger.org/'>Auxledger infrastructure</a></u></b> to suit the enterprise requirements in a more advanced form. Auxledger which has currently <b>on-boarded over 53 Million population</b> with the partner state governments of India and <b>NITI Aayog</b> is coming up with the version to create a <b>Blockchain which will empower tomorrow's decentralised internet.</b><br><br>"
    body += "We are delighted to invite you at the webinar where <b>Akash Gaurav</b>, CEO of Auxesis Group will talk about how Auxledger turned out to be <b>the world's largest Blockchain network.</b> For Blockchain and technology enthusiasts he will also share Auxledger idea to build a scalable, flexible and interoperable Blockchain infrastructure.<br><br>"
    body += "<b>Title:</b> Building Blockchain for a Billion Population<br>"
    body += "<b>Schedule:</b> July 21st, 2018, 4pm IST @FBlive<br>"
    body += "<b>FB Link:</b> http://bit.ly/fblivebillion<br><br>"
    body += "Subscribe now, so you don't miss the opportunity to learn about the new generation of internet, decentralised!<br><br>"
    body += "Thanks,<br>"
    body += "Sunny Kumar<br>"
    body += "Co-Founder<br>"
    body += "<u><a href='https://auxledger.org/'>Auxledger Foundation</a></u>"
    return body


def send_email(name, email):
    email_dict = {
        "to": {email: email},
        "from": [email_from, "Sunny Kumar"],
        "subject": "Webinar Invitation | Building Blockchain for a Billion Population | July 21st, 4PM IST",
        "html": get_html(name)
    }

    result = m.send_email(email_dict)


try:

    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            try:
                send_email(row[1], row[2])
            except Exception as e:
                continue
            print row[1] + ' ' + row[2]

    print 'success'
except Exception as e:
    print e
