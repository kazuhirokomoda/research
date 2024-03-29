#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import math
import numpy

# input1: ...list.txt (list of twitter IDs that are included in the LDA model)
# input2: model_final.theta (document(user)-topic matrix)
# output: 
# 

username2userid = dict()
userid2username = dict()
userid2topic_distribution = dict()
dist_matrix = dict()
sim_matrix = dict()

## for queries
queryid2topic_distribution = dict()
dist_matrix_query = dict()
sim_matrix_query = dict()

# username
username = ''

def init():
    global username2userid, userid2username, userid2topic_distribution, queryid2topic_distribution

    fp_list = open('friends_LDA4_list.txt')
    lines_list = fp_list.readlines()
    for line_list in lines_list:
        number_name = line_list[:-1].split(' ')
        username2userid[number_name[1].replace('.txt','')] = int(number_name[0])-1 
        userid2username[int(number_name[0])-1] = number_name[1].replace('.txt','')
    
    fp_theta = open('model-final.theta')
    lines_theta = fp_theta.readlines()
    userid = 0
    for line_theta in lines_theta:
        tmp_list = []
        distribution = line_theta[:-2].split(' ')

        for a_dist in distribution:
            tmp_list.append(float(a_dist))

        userid2topic_distribution[userid] = tmp_list
        userid += 1

    fp_query = open('query.txt.theta')
    lines_query = fp_query.readlines()
    queryid = 0
    for line_query in lines_query:
        tmp_list = []
        distribution = line_query[:-2].split(' ')

        for a_dist in distribution:
            tmp_list.append(float(a_dist))

        queryid2topic_distribution[queryid] = tmp_list
        queryid += 1


def set_username(_username):
    global username
    username = _username
    print 'Username: ' + username
    print ''


def calculate_dist_matrix():
    global dist_matrix    

    user_num = len(userid2topic_distribution)
    topic_num = len(userid2topic_distribution[0])

    # dist_matrix
    for i in range(user_num):

        dist_matrix[i] = dict()
        for j in range(user_num):

            # calculate dist(i,j)
            DT_i = userid2topic_distribution[i]
            DT_j = userid2topic_distribution[j]
            M = [(x+y)/2 for count_x,x in enumerate(DT_i) for count_y,y in enumerate(DT_j) if count_x==count_y]
            # may be easier if you use 
            # (1) M = map(lambda x, y: (x + y) / 2.0, DT_i, DT_j)
            # (2) Array... M = (DT_i + DT_j) / 2.0 if DT_i and DT_j are Array type.
            
            D_KL_i = 0.0
            D_KL_j = 0.0
            for k in range(topic_num):
                D_KL_i += DT_i[k]*math.log10(DT_i[k]/M[k])
                D_KL_j += DT_j[k]*math.log10(DT_j[k]/M[k])

            D_JS = (D_KL_i + D_KL_j)/2 # Jensen-Shannon Divergence
            dist_i_j = math.sqrt(2*D_JS)

            # dist_matrix
            dist_matrix[i][j] = dist_i_j


    print '--Topical Difference--'
    print 'Users who are similar to the user ' + str(username2userid[username]) + ' (' + username + '): '
    for k, v in sorted(dist_matrix[username2userid[username]].items(), key=lambda x:x[1]):
        print userid2username[k], v
    print ''


def calculate_dist_matrix_query():
    global dist_matrix_query    

    query_num = len(queryid2topic_distribution)
    topic_num = len(queryid2topic_distribution[0])
    user_num = len(userid2topic_distribution) # user

    # dist_matrix
    for i in range(query_num):

        dist_matrix_query[i] = dict()
        for j in range(user_num):

            # calculate dist(i,j)
            DT_i = queryid2topic_distribution[i]
            DT_j = userid2topic_distribution[j]
            M = [(x+y)/2 for count_x,x in enumerate(DT_i) for count_y,y in enumerate(DT_j) if count_x==count_y]

            D_KL_i = 0.0
            D_KL_j = 0.0
            for k in range(topic_num):
                D_KL_i += DT_i[k]*math.log10(DT_i[k]/M[k])
                D_KL_j += DT_j[k]*math.log10(DT_j[k]/M[k])

            D_JS = (D_KL_i + D_KL_j)/2 # Jensen-Shannon Divergence
            dist_i_j = math.sqrt(2*D_JS)

            # dist_matrix
            # i:query, j:user
            dist_matrix_query[i][j] = dist_i_j


    print '--Queries and Users--'
    print 'Users who are similar to the query: '
    for k, v in sorted(dist_matrix_query[0].items(), key=lambda x:x[1]):
        print userid2username[k], v    
    print ''


def calculate_sim_matrix():
    global sim_matrix

    user_num = len(userid2topic_distribution)
    topic_num = len(userid2topic_distribution[0])

    # sim_matrix
    for i in range(user_num):

        sim_matrix[i] = dict()
        for j in range(user_num):
            # calculate sim(i,j)
            DT_i = userid2topic_distribution[i]
            DT_j = userid2topic_distribution[j]
            product = [x*y for count_x,x in enumerate(DT_i) for count_y,y in enumerate(DT_j) if count_x==count_y]
            sum_product = sum(product)
            sq_DT_i = [x**2 for x in DT_i]
            sq_DT_j = [x**2 for x in DT_j]
            norm_i = math.sqrt(sum(sq_DT_i))
            norm_j = math.sqrt(sum(sq_DT_j))

            sim_i_j = sum_product/(norm_i*norm_j)
            # sim_matrix
            sim_matrix[i][j] = sim_i_j


    print '--Cosine Similarity--'
    print 'Users who are similar to the user ' + str(username2userid[username]) + ' (' + username + '): '
    for k, v in sorted(sim_matrix[username2userid[username]].items(), key=lambda x:x[1], reverse=True):
        print userid2username[k], v
    print ''


def calculate_sim_matrix_query():
    global sim_matrix_query

    query_num = len(queryid2topic_distribution)
    topic_num = len(queryid2topic_distribution[0])
    user_num = len(userid2topic_distribution) # user

    # sim_matrix
    for i in range(query_num):

        sim_matrix_query[i] = dict()
        for j in range(user_num):
            # calculate sim(i,j)
            DT_i = queryid2topic_distribution[i]
            DT_j = userid2topic_distribution[j]
            product = [x*y for count_x,x in enumerate(DT_i) for count_y,y in enumerate(DT_j) if count_x==count_y]
            sum_product = sum(product)
            sq_DT_i = [x**2 for x in DT_i]
            sq_DT_j = [x**2 for x in DT_j]
            norm_i = math.sqrt(sum(sq_DT_i))
            norm_j = math.sqrt(sum(sq_DT_j))

            sim_i_j = sum_product/(norm_i*norm_j)
            # sim_matrix
            sim_matrix_query[i][j] = sim_i_j


    print '--Queries and Users (Cosine Similarity)--'
    print 'Users who are similar to the query: '
    for k, v in sorted(sim_matrix_query[0].items(), key=lambda x:x[1], reverse=True):
        print userid2username[k], v
    print ''



if __name__ == '__main__':
    init()

    set_username('kazuhirokomoda')
    #calculate_dist_matrix()
    #calculate_dist_matrix_query()
    #calculate_sim_matrix()
    #calculate_sim_matrix_query()

    #similar_users('kazuhirokomoda')
