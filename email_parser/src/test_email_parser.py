import unittest
import pandas as pd
import numpy as np
import math
from pandas.io.json import json_normalize
from email_parser import remove_wacka, generate_emails_df, conversationalize


class TestEmailParser(unittest.TestCase):

    def setUp(self):
        self.data = [
            {
                'Body': 'Hi both, can you let me know ideal times for meeting please?',
                'Date': '2017-11-02 18:58:15',
                'From': 'Carmella Draeger <carmella@example.com>',
                'From email': 'carmella@example.com',
                'To': 'Celia Prince <celia@example.com>, Alisson Silva <alisson@example.com>',
                'To email': ['celia@example.com', 'alisson@example.com'],
                'In-Reply-To': np.NaN,
                'Message-ID': 1,
                'Subject': 'Meeting'
            },
            {
                'Body': 'From our cruise partner! Check it out! https://redhot.deals/g91js940/bargain-cruises-caribbean',
                'Date': '2017-11-06 10:22:00',
                'From': 'Red Hot Deals!!! <promotions@example.com>',
                'From email': 'promotions@example.com',
                'To': 'Carmella Draeger <carmella@example.com>',
                'To email': ['carmella@example.com'],
                'In-Reply-To': np.NaN,
                'Message-ID': 5,
                'Subject': 'Fidget spinners REDUCED TO CLEAR'
            },
            {
                'Body':
                '''
                Hey Carmella, 
                Tuesday would be best for me. I\'m otherwise very busy. 
                Best, Celia
                > Hi both, can you let me know ideal times for meeting please?
                ''',
                'Date': '2017-11-02 20:38:12',
                'From': 'Celia Prince <celia@example.com>',
                'From email': 'celia@example.com',
                'To': 'Carmella Draeger <carmella@example.com>',
                'To email': ['carmella@example.com'],
                'In-Reply-To': 1,
                'Message-ID': 2,
                'Subject': 'RE: Meeting'
            },
            {
                'Body':
                '''
                "Forwarded message: Great meeting!

                Summary:
                - Alisson will circulate minutes within a week
                - Carm to confirm everything with Iyana
                - Celia to get back on costing

                > [-Iyana]
                >
                > Ok we're all free today so let's go shortly.
                >
                > I'll text you both when I find a room.
                >
                >> Really excited to see where you three get to on this!
                >>
                >>> Hey Carmella,
                >>>
                >>> Tuesday would be best for me. I'm otherwise very busy.
                >>>
                >>> Best,
                >>> Celia
                >>>>
                >>>>> Hi both, can you let me know ideal times for meeting please?
                "
                ''',
                'Date': '2017-11-05 08:01:02',
                'From': 'Carmella Draeger <carmella@example.com>',
                'From email': 'carmella@example.com',
                'To': 'Iyana Novak <iyana@example.com>',
                'To email': ['iyana@example.com'],
                'In-Reply-To': np.NaN,
                'Message-ID': 11,
                'Subject': 'Fw: Meeting'
            }
        ]

    def test_remove_wacka(self):
        self.assertEqual(remove_wacka('<test>'), 'test')
        self.assertEqual(remove_wacka('<test'), 'test')
        self.assertEqual(remove_wacka('test>'), 'test')

    def test_generate_df(self):
        # test df structure
        expected_columns = ['Body', 'Date', 'From', 'From email',
                            'To', 'To email', 'In-Reply-To', 'Message-ID', 'Subject']
        dataframe = json_normalize(self.data)
        actual_columns = dataframe.columns
        self.assertEqual(set(expected_columns), set(actual_columns))

    def test_spam_identification(self):
        dataframe = json_normalize(self.data)
        dataframe.loc[:, 'Spam'] = dataframe.loc[:, 'From email'].map(
            lambda x: True if 'promo' in x.lower() else False)
        correct_spam = [False, True, False, False]
        self.assertEqual(dataframe.loc[:, 'Spam'].tolist(), correct_spam)

    def test_starter_identification(self):
        dataframe = json_normalize(self.data)
        dataframe.loc[:, 'Starter'] = dataframe.apply(
            lambda x: True if ('re:' not in x.loc['Subject'].lower() and 'fw:' not in x.loc['Subject'].lower()) and math.isnan(float(x.loc['In-Reply-To'])) else False, axis=1)
        correct_starters = [True, True, False, False]
        self.assertEqual(
            dataframe.loc[:, 'Starter'].tolist(), correct_starters)

    # def test_conversationalize(self):
    #     pass

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
