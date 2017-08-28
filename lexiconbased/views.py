from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
# from django.core.files.storage import FileSystemStorage
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from lexiconbased.models import Result

import re, string

try:
    import json
except:
    import simplejson as json


def showberanda(request):
    return render(request, 'index.html',)

def showsentimenanalisis(request):
    return render(request, 'sentiment_analysis.html')

def showbantuan(request):
    return render(request, 'bantuan.html')

def get_tweets(request):
    if request.POST:

        import tweepy, sys, jsonpickle

        consumer_key = 'K6V0CCCWRTrmk582ETAepQ77q'
        consumer_secret = 'T9q1U8hO6AKG8znSbsvjR7gu6eCGvxR6d1S4KJjCrPI8vvzndz'

        qry = '@Telkomsel AND (pulsa OR sinyal OR harga OR kualitas OR kuota OR internet OR jaringan OR pelayanan)'
        maxTweets = 1000  # Isi sembarang nilai sesuai kebutuhan anda
        tweetsPerQry = 100  # Jangan isi lebih dari 100, ndak boleh oleh Twitter
        t = datetime.now()
        formatted_time = t.strftime('%d-%m-%y %H.%M')
        fname = 'Tweets_' + formatted_time

        auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        if (not api):
            sys.exit('Autentikasi gagal, mohon cek "Consumer Key" & "Consumer Secret" Twitter anda')

        sinceId = None
        max_id = -1
        tweetCount = 0

        with open(fname + '.json', 'w') as f:
            while tweetCount < maxTweets:
                try:
                    if (max_id <= 0):
                        if (not sinceId):
                            new_tweets = api.search(q=qry, count=tweetsPerQry, tweet_mode='extended')
                        else:
                            new_tweets = api.search(q=qry, count=tweetsPerQry, since_id=sinceId, tweet_mode='extended')
                    else:
                        if (not sinceId):
                            new_tweets = api.search(q=qry, count=tweetsPerQry, max_id=str(max_id - 1), tweet_mode='extended')
                        else:
                            new_tweets = api.search(q=qry, count=tweetsPerQry, max_id=str(max_id - 1), since_id=sinceId, tweet_mode='extended')
                    if not new_tweets:
                        print('Tidak ada lagi Tweet ditemukan dengan Query="{0}"'.format(qry));
                        break
                    for tweet in new_tweets:
                        if (tweet._json['user']["name"] != "Telkomsel" and "?" not in tweet._json["full_text"] and tweet._json['metadata']["iso_language_code"] == "in"):
                            f.write(jsonpickle.encode(tweet._json, unpicklable=False) + '\n')
                            # text = tweet._json["full_text"]
                            # text = re.sub(r"(?:\|https?| https?|https? \://)\S+", "", text)
                            # character = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                            #              'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
                            # for i in range(len(character)):
                            #     charac_long = 5
                            #     while charac_long >= 2:
                            #         char = character[i] * charac_long
                            #         text = text.replace(char, character[i])
                            #         charac_long -= 1
                            # text = ' '.join(word.strip(string.punctuation) for word in text.split())

                    tweetCount += len(new_tweets)
                    max_id = new_tweets[-1].id
                except tweepy.TweepError as e:
                    print("some error : " + str(e));
                    break

        """messages.add_message(request, messages.INFO, 'Tweets telah tersimpan pada filename: {1}'.format(tweetCount, fname))
        messages.add_message(request, messages.INFO, 'Jumlah Tweets telah tersimpan: %.0f' % tweetCount)"""
        fo = open(fname + '.json', 'r')
        fw = open(fname + '.txt', 'w')

        for line in fo:
            try:
                tweet = json.loads(line)
                text = ' '.join(word.strip(string.punctuation) for word in tweet['full_text'].split())
                text = re.sub(r"(?:\@ | @|@|https?| https?|https? \://)\S+", "", text)
                character = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                             'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '.']
                for i in range(len(character)):
                    charac_long = 5
                    while charac_long >= 2:
                        char = character[i] * charac_long
                        text = text.replace(char, character[i])
                        charac_long -= 1
                #text = ' '.join(word.strip(string.punctuation) for word in text.split())
                text = re.sub(r"\n", "", text)
                fw.write(text + "\n")
            except:
                continue

        import nltk

        testing_data = '/Users/achmed/Documents/data/testing.txt'
        pos_words = '/Users/achmed/PycharmProjects/positive.txt'
        neg_words = '/Users/achmed/PycharmProjects/negative.txt'

        def read_opinion_lexicon(fileName):
            dataFile = open(fileName, "r")
            word_set = set()
            for line in dataFile:
                line = line.strip()
                if line not in word_set:
                    word_set.add(line)
            dataFile.close()
            return word_set

        positive_words = read_opinion_lexicon(pos_words)
        negative_words = read_opinion_lexicon(neg_words)

        fo = open(fname + '.txt', 'r')
        Result.objects.all().delete()
        global sentpos_count, sentneg_count, sentnet_count
        sentpos_count = 0
        sentneg_count = 0
        sentnet_count = 0
        negation_words = ['tidak', 'bukan', 'gak', 'enggak', 'belum', 'ga', 'tdk', 'tak', 'malah']

        for line in fo:
            sentence = line
            kalimat = sentence.split()
            doc_words = [w.lower() for w in kalimat]
            pos_count = 0
            neg_count = 0

            for w in doc_words:
                if w in positive_words:
                    if (doc_words[doc_words.index(w) - 1] in negation_words):
                        neg_count -= 1
                    else:
                        pos_count += 1
                if w in negative_words:
                    if (doc_words[doc_words.index(w) - 1] in negation_words):
                        pos_count += 1
                    else:
                        neg_count -= 1
            sum = pos_count + neg_count

            if (sum == 0):
                classify_result = "netral"
                sentnet_count += 1
                pos_score = 0.5
                neg_score = 0.5
            else:
                pos_score = pos_count / sum
                neg_score = neg_count / sum

                if (pos_score > neg_score):
                    classify_result = "positif"
                    sentpos_count += 1
                else:
                    classify_result = "negatif"
                    sentneg_count += 1

            sentiment2 = Result(sentiment=sentence, classification=classify_result)
            sentiment2.save()


        #classifier.show_most_informative_features()

        #test_corpus, _ = load_corpus(testing_data)
        #test_set_features = [(doc_features(d), c) for (d, c) in test_corpus]

        #print(nltk.classify.accuracy(classifier, test_set_features))

    return render(request, 'sentiment_analysis.html', {'obj': Result.objects.all()})
