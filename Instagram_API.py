# -*- coding: utf-8 -*-

from textblob import TextBlob
from InstagramAPI import InstagramAPI
from datetime import datetime
import os 

# **************************************************
user_name = ""
password = ""
hashtag = "perspolis"
post_count = int(input("Number of post you want:"))
count = int(input("Number of comment you want per post:"))
until_date = input("date:")
#count = int(input("Number of comment you want per post"))
#local_path = input("Local path for save data")

v = TextBlob(hashtag)
try:
    name = str(v.translate(to = 'en'))
except:
     name = str(hashtag)

print("*******************************************")
API = InstagramAPI(user_name, password)
API.login()
print("*************************************")

# ***** get detail post ****************************

posts = []
post_max_id = ''
has_more_posts = True
step = 0

# ***** get post posts  *******************************************************

while has_more_posts:
    _ = API.getHashtagFeed(hashtag, post_max_id)
    # for first request that return about 80 posts
    if(step == 0):
        for t in (API.LastJson['ranked_items']):
            posts.append(t)
        for n in (API.LastJson['items']):
            posts.append(n)
    default = []
    try:
        x = API.LastJson.get("items",default)
    except:
        print("Nonetyp")
    if(x !=  []):
        for h in reversed(API.LastJson['items']):
            posts.append(h)
    try:
        has_more_posts = API.LastJson.get('more_available', False)
    except:
        print("NoneType")
    # evaluate stop conditions
    if post_count and len(posts) >= post_count:
        posts = posts[:post_count]
        has_more_posts = False
        print ("stopped by count") 
        if until_date:
            older_post = posts[-1]['caption']
            try:
                dt = datetime.utcfromtimestamp(older_post.get('created_at_utc', 0))
            except:
                print("error data")
            # only check all records if the last is older than stop condition
            try:
                if dt.isoformat() <= until_date:
                    # keep comments after until_date
                    posts = [
                        c
                        for c in posts
                        if datetime.utcfromtimestamp(c.get('created_at_utc', 0)) > until_date
                    ]
                    # stop loop
                    has_more_posts = False
            except:
                print('error date')
            print ("stopped by until_date")
     # next page
    if has_more_posts:
        post_max_id = API.LastJson.get('next_max_id', '')
    step = step+1
    print(step)

media_id = []
for j in posts:
        media_id.append(j['id'])
     
print (media_id)

# **** all_posts @*************************************************************************

postss =  open ("temp.csv","w", encoding="utf-8")
for c in posts:
    try:
        postss.write(c['caption']['user']['username']+","+str(datetime.utcfromtimestamp(c['caption']['created_at_utc']))+","+str(c['id'])+","+str(c['location']['lat'])+","+str(c['location']['lng'])+","+str(c['comment_count'])+","+str(c['like_count'])+","+c['caption']['text'].replace("\n"," ").replace("\r\n"," ").replace("\\n"," ").replace(" \n"," ").replace(","," ")+"\n")
    except:
        print('Nonetype')
postss.close()

f=open("temp.csv","r",encoding="utf-8")
f1=open("all_posts.csv","w",encoding="utf-8")
for LL in f:
    s=LL.split(",")
    if len(s)<8:
        print ("\n**************************")
    else:
        f1.write(LL)
f.close()
f1.close()
os.remove("temp.csv")

# **** posts @*************************************************************************

num = 0
postss =  open ("temp.csv","w",encoding="utf-8")
for c in posts:
    try:
        postss.write(c['caption']['user']['username']+","+str(datetime.utcfromtimestamp(c['caption']['created_at_utc']))+","+c['caption']['text'].replace("\n"," ").replace("\r\n"," ").replace("\\n"," ").replace(" \n"," ").replace(","," ")+"\n")
    except:
        print('Nonetype')
        num = num +1
postss.close()

f=open("temp.csv","r",encoding="utf-8")
f1=open("posts.csv","w",encoding="utf-8")
for LL in f:
    s=LL.split(",")
    if len(s)<2:
        print ("\n**************************")
    else:
        f1.write(LL)
f.close()
f1.close()
os.remove("temp.csv")
    
# ***** get comments for posts ************************************************

commentss = []
st = 1
for med_id in media_id:
    max_id = ''
    comments = []
    has_more_comments = True
    # stop conditions, the script will end when first of them will be true
    while has_more_comments:
        _ = API.getMediaComments(med_id, max_id=max_id)
        # comments' page come from older to newer, lets preserve desc order in full list
        default = []
        x = API.LastJson.get("comments",default)
        if(x !=  []):
            for c in reversed(API.LastJson['comments']):
                comments.append(c)
        has_more_comments = API.LastJson.get('has_more_comments', False)
        # evaluate stop conditions
        if count and len(comments) >= count:
            comments = comments[:count]
            # stop loop
            has_more_comments = False
            print ("stopped by count")
        if (len(comments) !=0):
            if until_date:
                older_comment = comments[-1]
                dt = datetime.utcfromtimestamp(older_comment.get('created_at_utc', 0))
                # only check all records if the last is older than stop condition
                try:
                    if dt.isoformat() <= until_date:
    #                    # keep comments after until_date
                        comments = [
                            c
                            for c in comments
                            if datetime.utcfromtimestamp(c.get('created_at_utc', 0)) > until_date
                        ]
    #                     stop loop
                        has_more_comments = False
                except:
                    print('error date')
    #            print "stopped by until_date"
        # next page
        if has_more_comments:
            max_id = API.LastJson.get('next_max_id', '')
    commentss.append(comments)
    print(st)
    st = st +1
    
# **** media_id with all comments *************************************************************************

media_and_comments = open("temp.csv","w", encoding="utf-8")
i=0
for i in range(post_count):
    s = ""
    # a = 1
    for c in commentss[i]:
        try:
           s = c['user']['username']+","+str(datetime.utcfromtimestamp(c['created_at_utc']))+","+c['text'].replace("\n"," ").replace("\r\n"," ").replace("\\n"," ").replace(" \n"," ").replace(","," ")
           media_and_comments.write(str(media_id[i])+","+s+"\n")
        except:
            print("Ridim")
            
media_and_comments.close()

f=open("temp.csv","r", encoding="utf-8")
f1=open("media_comment.csv","w", encoding="utf-8")
for LL in f:
    s=LL.split(",")
    if len(s)<3:
        print ("\n**************************")
    else:
        f1.write(LL)
f.close()
f1.close()
os.remove("temp.csv")

