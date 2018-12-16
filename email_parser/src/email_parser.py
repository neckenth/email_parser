import pandas as pd
import numpy as np
import glob
import email.parser
import math


def remove_wacka(s):
    return s.replace('<', '').replace('>', '')


def generate_emails_df():

    # create empty dataframe
    df = pd.DataFrame()

    # parse .mail files and format/collect metadata in df
    for f in glob.glob('../../raw_emails/*.mail'):

        with open(f) as payload:
            full_content = email.parser.Parser().parse(payload)
            message_id = remove_wacka(full_content['Message-ID'].split('@')[0])
            reply_id = (
                remove_wacka(full_content['In-Reply-To'].split('@')[0]) if full_content['In-Reply-To'] else np.NaN)
            e_body = full_content.get_payload()
            e_from = full_content['From']
            from_address = remove_wacka(e_from.split('<')[1])
            e_to = full_content['To']
            to_addresses = [x.split('<')[1].replace('>', '')
                            for x in e_to.split(', ')]
            e_subj = full_content['Subject']
            date = pd.to_datetime(full_content['Date'])
            row = {
                'Message-ID': message_id,
                'In-Reply-To': reply_id,
                'Date': date,
                'From': e_from,
                'From email': from_address,
                'To': e_to,
                'To email': to_addresses,
                'Subject': e_subj,
                'Body': e_body,
            }
            df = df.append(other=row, ignore_index=True, sort=True)
    df = df.sort_values(['Date']).reset_index(
        drop=True)  # sort rows by date asc
    return df


def identify_spam(df):
 # identify spam
    df.loc[:, 'Spam'] = df.loc[:, 'From email'].map(
        lambda x: True if 'promo' in x.lower() else False)
    return df


def identify_starters(df):
    # identify starts of conversations
    df.loc[:, 'Starter'] = df.apply(
        lambda x: True if ('re:' not in x.loc['Subject'].lower() and 'fw:' not in x.loc['Subject'].lower()) and math.isnan(float(x.loc['In-Reply-To'])) else False, axis=1)

    return df


def create_starters_list(df):
    starters = []

    for i in df.index:  # store conversation starters in starters list for future iteration
        if df.loc[i, 'Starter'] == True:
            starters.append(df.loc[i, 'Message-ID'])
    return starters


def conversationalize(df):
    # df with two additional columns for indicating Starter and Spam
    df = identify_starters(identify_spam(df))
    starters = create_starters_list(df)  # starters list
    convos = []  # list of lists - !final product!

    # separate emails into conversation lists based on each starter
    for x in starters:

        # emails with no replies - conversations by default
        if x not in df.loc[:, 'In-Reply-To'].values:
            convos.append([x])

        # subsequent messages
        for i in df.index:  # iterate through rows of df to get data for individual emails

            # metadata for starter email for comparison
            if df.loc[i, 'Message-ID'] == x:
                this_subj = df.loc[i, 'Subject']
                sender = df.loc[i, 'From email']
                to_list = df.loc[i, 'To email']

            # for appending to corresponding convo sub-list
            next_msg_id = df.loc[i, 'Message-ID']

            # identify *direct* replies to starters
            if df.loc[i, 'In-Reply-To'] == x:
                convos.append([x, next_msg_id])

            # if starter subject in reply subject and `from` in reply in `to` from starter
            if this_subj in df.loc[i, 'Subject'] and ('re' in df.loc[i, 'Subject'].lower() or 'fw' in df.loc[i, 'Subject'].lower()):
                if (sender in df.loc[i, 'To email'] or sender in df.loc[i, 'From email']):
                    if df.loc[i, 'Message-ID'] not in starters and int(df.loc[i, 'Message-ID']) > int(x):
                        convo_index = starters.index(x)
                        if df.loc[i, 'Message-ID'] not in convos[convo_index]:
                            convos[convo_index].append(df.loc[i, 'Message-ID'])

    return convos


df = generate_emails_df()

convos = conversationalize(df)
print convos
