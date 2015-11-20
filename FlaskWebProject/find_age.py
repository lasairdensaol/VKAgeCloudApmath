import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import networkx as nx
#import os
from collections import Counter
import datetime as dt
import comm as community

from FlaskWebProject import vk_api

# from matplotlib import rc, rcParams
# font = {'family': 'Droid Sans',
#         'weight': 'normal'}
# rc('font', **font)
#
#
# colors = [(0.10588235294117647, 0.6196078431372549, 0.4666666666666667),
# (0.8509803921568627, 0.37254901960784315, 0.00784313725490196),
# (0.4588235294117647, 0.4392156862745098, 0.7019607843137254),
# (0.9058823529411765, 0.1607843137254902, 0.5411764705882353),
# (0.4, 0.6509803921568628, 0.11764705882352941),
# (0.9019607843137255, 0.6705882352941176, 0.00784313725490196),
# (0.6509803921568628, 0.4627450980392157, 0.11372549019607843)]
#
# rcParams['figure.figsize'] = (10, 6)
# rcParams['figure.dpi'] = 150
# rcParams['axes.color_cycle'] = colors
# rcParams['lines.linewidth'] = 2
# rcParams['axes.facecolor'] = 'white'
# rcParams['font.size'] = 14
# rcParams['patch.edgecolor'] = 'white'
# rcParams['patch.facecolor'] = colors[0]
# rcParams['font.family'] = 'StixGeneral'

fields = ['first_name', 'last_name', 'bdate','sex',
         'city.title',
         'universities.0.name',
         'schools.0.name', 'schools.0.year_graduated']

def transform_user_profile(user_profile):
    return [vk_api.JsonUtils.json_path(user_profile, field, default=None) for field in fields]

year = dt.datetime.now().year

def map_age(x):
    if x is not None:
        splited = x.split('.')
        if len(splited) == 3:
            return year - int(splited[2])
    return None

def average_moda(c, n, ave_moda):
    for k in c.keys():
        if c[k] == max(c.values()):
               if n != 0:
                   ave_moda.append((ave_moda.pop() + k)/(n + 1))
                   continue

               ave_moda.append(k)
               n = n + 1
    return ave_moda

def average(ccce):
    if ccce:
        return np.sum([ccce[k]*k for k in ccce.keys()]) / np.sum(ccce.values())
    else:
        return 0

def find_key(dic, v):
    res = []
    for k in dic.keys():
        if dic[k] == v:
            res.append(k)
    return res

def find_age_1(df):
    has_age = pd.notnull(df['age'])
    count_has_age = Counter(has_age)[True]

    if count_has_age == 0:
        return 0
    else:
        return int(df['age'].sum()/count_has_age)

def find_age_2(count_f_in_comm, new_df):
    ave_moda = []
    for i in range(len(count_f_in_comm)):
        n = 0
        if count_f_in_comm.values()[i] > 3:
            tmp_df = Counter(new_df[new_df['community'] == i]['age'])
            if len(tmp_df) == 0:
                continue

            ave_moda = average_moda(tmp_df, n, ave_moda)

    if len(ave_moda) == 0:
        return 0
    else:
        return int(np.sum(ave_moda)/len(ave_moda))

def find_age_3(count_f_in_comm, new_df):
    huge_comm = max(count_f_in_comm.values())
    nums_of_hugest_comm = []

    for k in count_f_in_comm.keys():
        if count_f_in_comm[k] == huge_comm:
            nums_of_hugest_comm.append(k)


    ave_moda_2 = []

    for i in nums_of_hugest_comm:
        n = 0
        tmp_df = Counter(new_df[new_df['community'] == i]['age'])
        if len(tmp_df) == 0:
            continue

        ave_moda_2 = average_moda(tmp_df, n, ave_moda_2)

    if len(ave_moda_2)  == 0:
        return 0
    else:
        return int(np.sum(ave_moda_2)/len(ave_moda_2))

def find_age_5(count_f_in_comm, new_df):
    mean_var = dict()

    for i in count_f_in_comm.keys():
        tmp_df = new_df[new_df['community'] == i]['age']
        if len(tmp_df) > 1:
            mean_var[i] = [np.var(tmp_df), np.mean(tmp_df)]

    if len(mean_var) <= 1:
        return 0
    else:
        sum_var_1 = np.sum([x[0] for x in mean_var.values()])
        sum_var_2 = np.sum([sum_var_1 - x[0] for x in mean_var.values()])

        for x in mean_var.keys():
            mean_var[x].append((sum_var_1 - mean_var[x][0])/sum_var_2)

        tmp1 = [x[1]*x[2] for x in mean_var.values()]

        tmp1 = np.sum(tmp1)

        tmp1 = int(tmp1)

        return tmp1

def find_age_4(count_f_in_comm, new_df):
    variance = dict()

    for i in count_f_in_comm.keys():
        tmp_df = new_df[new_df['community'] == i]['age']
        if len(tmp_df) > 1:
            variance[i] = np.var(tmp_df)

    if len(variance) == 0:
        return 0
    else:
        find_min = min(variance.values())
        k = find_key(variance,find_min)

        if len(k) > 1:
            ave = []
            for i in k:
                comm_min_var = Counter(new_df[new_df['community'] == i]['age'])
                ave.append(average(comm_min_var))
            return int(np.sum(ave)/len(ave))
        else:
            comm_min_var = new_df[new_df['community'] == k[0]]['age']
            return int(np.sum(comm_min_var)/len(comm_min_var))

def find_user_network(user_id):
 	api = vk_api.VkAPI()

 	friends_ids = api.get_friends(user_id)
 	friends_ids_set = set(friends_ids)

 	user_network = { user_id : friends_ids }

 	for friend_id in friends_ids:
 		try:
 			friend_friends_ids = api.get_friends(friend_id)
 			user_network[friend_id] = [x for x in friend_friends_ids if x in friends_ids_set]
 		except:
 			pass

 	friend_profiles = api.get_user_profiles(friends_ids)

 	return [friend_profiles, user_network]
	
def find_user_age(user_id):

    inf = find_user_network(user_id)

    index = [int(fp['id']) for fp in inf[0]]

    #return [1,2,3,4,user_id]

    data = [transform_user_profile(fp) for fp in inf[0]]
	
    df = pd.DataFrame(index=index, data=data, columns=fields)
    
    df['age'] = df.loc[:, 'bdate'].map(map_age)

    graph = nx.Graph()
    for user, friends in inf[1].iteritems():
    	for friend in friends:
    		graph.add_edge(user, friend)

    graph.remove_node(user_id)
    #
    # plt.figure(figsize=(7, 7))
    #
    # return [1,2,3,4,user_id]
    #
    # nx.draw_spring(graph, node_size=8, alpha=0.4)
    #
    # return [1,2,3,4,user_id]

    # exist_img = os.listdir(r'FlaskWebProject\static\images\\')
    #
    # if str(user_id) + '.png' not in exist_img:
    # 	plt.savefig(r'FlaskWebProject\static\images\\' + str(user_id) + '.png')
    #
    # plt.close()

    communities = community.best_partition(graph)

    df['community'] = df.index.map(lambda x : communities[x] if x in communities else None)

    new_df = df[df['age'] >0][:]
    count_f_in_comm = Counter(communities.values())

    age_1 = find_age_1(df)

    age_2 = find_age_2(count_f_in_comm, new_df)

    age_3 = find_age_3(count_f_in_comm, new_df)

    age_4 = find_age_4(count_f_in_comm, new_df)

    age_5 = find_age_5(count_f_in_comm, new_df)

    return [age_1, age_2, age_3, age_4, age_5]