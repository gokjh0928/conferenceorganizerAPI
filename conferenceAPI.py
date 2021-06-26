import requests
import pprint
import datetime
from IPython.display import clear_output as co
from collections import defaultdict


def main():
    # get data
    res = requests.get("https://ct-mock-tech-assessment.herokuapp.com/")
    if res.status_code != 200:
        print("Failed to get data")
    data = res.json()['partners']

    ####### Creating the defaultdicts needed to calculate best dates #######
    # dates is a defaultdict containing key:value pairs of (country):(set of unique dates)
    # emails is a defaultdict containing a defaultdict (key):(key:value) -> (country):{(unique date):(emails for that unique date)}
    dates = defaultdict(set)
    emails = defaultdict(lambda: defaultdict(set))

    # get the country of each partner and set value to the set of unique available dates for that country
    # per country, for each unique date, there is an associated set of unqiue emails for ppl available at that date

    for partner in data:
        country = partner['country']
        datelist = partner['availableDates']
        # makes the dates into a tuple
        for date in datelist:
            dateentry = tuple(date.split('-'))
            dates[country].add(dateentry)
            emails[country][tuple(dateentry)].add(partner['email'])

    ####### Calculate best dates per country #######

    # best_dates is list of tuples -> (country, best date for that country, day following best date, and attendee count)
    best_dates = []

    # go through each country
    for country in emails:
        most, best_date, best_next_date = 0, None, None

        # go through each date tuple for this country
        for date in emails[country]:
            curr = 0
            # convert the date into a datetime object
            dt = datetime.date(year=int(date[0]), month=int(
                date[1]), day=int(date[2]))
            # get next day
            dt += datetime.timedelta(days=1)
            # convert that into a string
            nextdate = (f"{dt.year}", f"{dt.month:02}", f"{dt.day:02}")

            # check if current date and next date have same email(partner can attend both days)
            # if so, increment curr
            for email in emails[country][date]:
                if nextdate in emails[country] and email in emails[country][nextdate]:
                    curr += 1
            # if curr is greater than most, it means current date has the most available participants
            if curr > most:
                most = curr
                best_date = date
                best_next_date = nextdate

        # Now for this country, append the best date available
        best_dates.append((country, best_date, best_next_date, most))

    #pprint.pprint(dict(emails), sort_dicts=False)

    # Now convert in a format like the sample solution
    sol = []
    for best_data in best_dates:
        attendees = []
        for email in emails[best_data[0]][best_data[1]]:
            if email in emails[best_data[0]][best_data[2]]:
                attendees.append(email)
        sol.append({
            'attendeeCount': best_data[3],
            'attendees': attendees,
            'name': best_data[0],
            'startDate': '-'.join(best_data[1])
        })

    pprint.pprint(sol)

    res = requests.post(
        url="https://ct-mock-tech-assessment.herokuapp.com/", json=sol)
    print(res.status_code)


main()
