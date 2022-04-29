import csv
import pysam
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mt


eval = open('output/eval_cl.txt', 'a')
#eval.write("Edge" + "\t" + "Cluster" + "\t" + "St" + "\n")


edges = ['edge_1', 'edge_10', 'edge_100', 'edge_101', 'edge_102', 'edge_103', 'edge_104', 'edge_105', 'edge_106',
         'edge_107', 'edge_108', 'edge_109', 'edge_11', 'edge_110', 'edge_111', 'edge_112', 'edge_113', 'edge_114',
         'edge_115', 'edge_116', 'edge_12', 'edge_13', 'edge_14', 'edge_15', 'edge_16', 'edge_17', 'edge_18', 'edge_19',
         'edge_2', 'edge_20', 'edge_21', 'edge_22', 'edge_23', 'edge_24', 'edge_25', 'edge_26', 'edge_27', 'edge_28',
         'edge_29', 'edge_3', 'edge_30', 'edge_31', 'edge_32', 'edge_33', 'edge_34', 'edge_35', 'edge_36', 'edge_37',
         'edge_38', 'edge_39', 'edge_4', 'edge_40', 'edge_41', 'edge_42', 'edge_43', 'edge_44', 'edge_45', 'edge_46',
         'edge_47', 'edge_48', 'edge_49', 'edge_5', 'edge_50', 'edge_51', 'edge_52', 'edge_53', 'edge_54', 'edge_55',
         'edge_56', 'edge_57', 'edge_58', 'edge_59', 'edge_6', 'edge_60', 'edge_61', 'edge_62', 'edge_63', 'edge_64',
         'edge_65', 'edge_66', 'edge_67', 'edge_68', 'edge_69', 'edge_7', 'edge_70', 'edge_71', 'edge_72', 'edge_73',
         'edge_74', 'edge_75', 'edge_76', 'edge_77', 'edge_78', 'edge_79', 'edge_8', 'edge_80', 'edge_81', 'edge_82',
         'edge_83', 'edge_84', 'edge_85', 'edge_86', 'edge_87', 'edge_88', 'edge_89', 'edge_9', 'edge_90', 'edge_91',
         'edge_92', 'edge_93', 'edge_94', 'edge_95', 'edge_96', 'edge_97', 'edge_98', 'edge_99']


R = 1
I = 1000
clipp = 100
min_mapping_quality = 20
min_base_quality = 0
min_al_len = 1000
de_max = 0.05
AF = 0.1
import re
from collections import Counter

for edge in edges:
    try:
        cl = pd.read_csv("output/clusters/clusters_%s_%s_%s.csv" % (edge, I, AF), keep_default_na=False)
        clusters = sorted(set(cl.loc[cl['Cluster'] != 'NA']['Cluster'].values))
        for cluster in clusters:
            res=[]
            for read in cl.loc[cl['Cluster'] == cluster]['ReadName'].values:
                res.append(re.sub(".*\._","",read))
            stat=int(Counter(res).most_common()[0][1])/len(res)
            eval.write(edge + "\t" + str(cluster) + "\t" + str(stat) + "\n")


    except(FileNotFoundError): continue
eval.close()