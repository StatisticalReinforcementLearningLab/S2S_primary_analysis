from datetime import datetime
from datetime import timedelta
import pytz

# get datetime from timestamp:
def date_time(intime):
    return (datetime.fromtimestamp(int(intime)/1000, tz=pytz.timezone('America/Chicago')))

# define intervention:

def intervention(row):
    val = np.where((row['operation'] == 'EMI_INFO') and (row['isStress'] == True), 'class_stress',  # available_stress
                   np.where((row['operation'] == 'EMI_INFO') and (row['isStress'] == False), 'class_notStress',  # available_notStress
                            np.where((row['id'] == 'EMI') and (row['status'] == 'DELIVERED'), 'delivered', 'other')))  # delivered, other.
    return val

def minute_rounder(t):
    # Rounds to nearest minute by adding a timedelta minute if seconds >= 30
    return (t.replace(second=0, microsecond=0, minute=t.minute, hour=t.hour)
            + timedelta(minutes=t.second//30))

# create function to extract the elements in a every key's list within
# a dictionary:

def Extract(dict, el):
    return [item[el] for item in dict.values()]

# define scatterplot:

def scatterplot(x_data, y_data, x_label, y_label, title):
    fig, ax = plt.subplots()
    ax.scatter(x_data, y_data, s=30, color='#539caf', alpha=0.75)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xlim([min(id_df.date_time), max(id_df.date_time)])
    fig.autofmt_xdate()

def get_part_of_day(hour):
    return (
        "morning" if 5 <= hour <= 11
        else
        "afternoon" if 12 <= hour <= 17
        else
        "evening" if 18 <= hour <= 22
        else
        "night")
