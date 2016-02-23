#!/usr/bin/env python
import random
from itertools import *
from themeconf import *


def get_pay_table(themeid):
    return THEME_CONFIG[themeid]['pay']

def get_lines(themeid):
    return ALLLINES[themeid]

def get_reels(themeid,freespin):
    if freespin==3:
        return THEME_CONFIG[themeid]['reels_H']
    if freespin==2:
        return THEME_CONFIG[themeid]['reels_W']
    return THEME_CONFIG[themeid]['reels_F'] if freespin else THEME_CONFIG[themeid]['reels_N']

def random_reels(themeid,freespin=0):
    ret = []
    reels = get_reels(themeid,freespin)
    i=0
    for l in THEME_CONFIG[themeid]['rows']:
        idx = random.randint(0,len(reels[i])-1)
        if idx+l<=len(reels[i]):
            ret.append(reels[i][idx:idx+l])
        else:
            ret.append((reels[i]+reels[i])[idx:idx+l])
        i+=1
    return ret

import copy
fairy_wild_pos=[(2,2)]
fairy_free_time=0
def spin_core(themeid,freespin,linecount):
    global fairy_wild_pos
    global fairy_free_time
    paytable=get_pay_table(themeid)
    itemlist1=random_reels(themeid,freespin)
    curlines = get_lines(themeid)
    resultlist = []
    bonus = 0
    sumreward = 0
    scatter = 0
    five=six=0
    # how many columns
    cols = len(THEME_CONFIG[themeid]['rows'])
    itemlist=copy.deepcopy(itemlist1)

    if themeid==4:
        for i in range(len(itemlist)):
            if itemlist[i].count(2)>0:
                itemlist[i]=[2]*len(itemlist[i])
    #hui gu niang
    if themeid==6:
        if freespin==1:
            r=random.random()<0.45
            for i in range(len(itemlist)):
                for j in range(len(itemlist[i])):
                    if itemlist[i][j]==12 and r:
                        itemlist[i][j]=3
                    if itemlist[i][j]<0:
                        if r:
                            itemlist[i][j]=2
                        else:
                            itemlist[i][j]*=-1
    if freespin==2:
        if themeid not in (3,4,6,7,8,9):
            flag=1
            if freespin==2:
                for i in range(len(itemlist)):
                    for j in range(len(itemlist[i])):
                        if itemlist[i][j]==-1:
                            itemlist[i][j]=2
                            flag=0
            if flag:
                print 'error found in wild configuration, no -1 in itemlist, program exits', itemlist
                exit(-1)
        elif themeid==3:
            x=random.randint(1,10)
            if x<=6 or x==10:
                itemlist[1]=[2,2,2,2]
                for i in (0,2,3,4,5):
                    for j in range(len(itemlist[i])):
                        if itemlist[i][j]<0:
                            if  i in (0,2):
                                itemlist[i][j]=2
                            else:
                                if x!=10:
                                    itemlist[i][j]*=-1
            if 6<x<10 or x==10:
                itemlist[4]=[2,2,2,2]
                for i in (0,1,2,3,5):
                    for j in range(len(itemlist[i])):
                        if itemlist[i][j]<0:
                            if  i in (3,5):
                                itemlist[i][j]=2
                            else:
                                if x!=10:
                                    itemlist[i][j]*=-1
    if themeid==7 and freespin==1:
        for x, y in fairy_wild_pos:
            itemlist[x][y]=2
        fairy_wild_pos=[]
        for i in range(len(itemlist)):
            for j in range(len(itemlist[i])):
                if itemlist[i][j]==2:
                    fairy_wild_pos.append((i,j))
        fairy_free_time+=1
        if fairy_free_time==7:
            fairy_free_time=0
            fairy_wild_pos=[(2,2)]

    if themeid==8:
        if freespin==1:
            f=random.random()<0.2
            flag=0
            for i in range(len(itemlist)):
                for j in range(len(itemlist[i])):
                    if itemlist[i][j]<0:
                        if f:
                            itemlist[i][j]=2
                            flag=1
                        else:
                            itemlist[i][j]*=-1
            assert(not( flag==0 and f))

        else:
            f=random.random()
            k=2
            s=0
            for x in THEME_CONFIG[8]['weight']:
                s+=x
                k+=1
                if s>=f:
                    break

            for i in range(len(itemlist)):
                for j in range(len(itemlist[i])):
                    if itemlist[i][j]<0:
                        itemlist[i][j]=k

    for i in range(linecount):
        last_k = 2
        bonus = 0
        longest_length = -1
        longest_id = 0
        longest_wild=0
        for j in range(cols):
            k = itemlist[j][curlines[i][j]]
            if last_k==2 and k>2:
                last_k = k
            if last_k==k or k==2:
                if last_k>2 and j+1>longest_length:
                    longest_length = j+1
                    longest_id = last_k
                if k==last_k==2:
                    longest_wild = j+1
            else:
                last_k = -1
        reward = 0
        if longest_id > 0:
            longest_length = min(longest_length,len(paytable[longest_id]))
            if paytable[longest_id][longest_length-1]>0:
                resultlist.append([i,longest_length])
            reward = max(reward,paytable[longest_id][longest_length-1])
            if longest_length==5: five=1
            if longest_length==6: six=1
        if 0:#longest_wild>0:
            longest_length=longest_wild
            longest_length=min(longest_length,len(paytable[3]))
            reward = max(reward,paytable[3][longest_length-1])

        sumreward += reward
    bonus = sum(j.count(0) for j in itemlist)
    scatter = sum(j.count(1) for j in itemlist)
    if bonus>=3 and scatter>=3:
        print themeid, itemlist
        exit('both bonus and scatter')
    return [itemlist,resultlist,sumreward,bonus,scatter, five, six]

SPINTYPE=["normal spin", "free spin", "wild spin", 'high_spin']
def spin_result(themeid,freespin,run_times=10000):
    if  themeid==7 and freespin==1:
        run_times*=7
    linecount=len(ALLLINES[themeid])
    total_cost=run_times*linecount
    totalwin=max_reward=scatter_times=bonus_times=win_times=0
    bigwin=megawin=superwin=0
    five=six=0
    allwins=[]
    for _ in range(run_times):
        ret=spin_core(themeid,freespin, linecount)
        win=ret[2]
        if ret[2]>0:
            win_times+=1
        if ret[-2]:
            five+=1
        if ret[-1]:
            six+=1
        if ret[3]>=3:
            bonus_times+=1
            win+=linecount*THEME_CONFIG[themeid]['bonus_win']
        if ret[4]>=3:
            assert(freespin!=1)
            scatter_times+=1
            if themeid!=4:
                a=[spin_core(themeid,1,linecount)[2] for f in range(7)]
            else:
                a=[]
                for freetime in range(7):
                    f=spin_core(themeid,1,linecount)
                    a.append(f[2] if f[0][2].count(2)!=3 else f[2]<<1)
            win+=sum(a)
        totalwin+=win
        if   win>=18*linecount: superwin+=1
        elif win>=12*linecount: megawin+=1
        elif win>=6*linecount: bigwin+=1
        max_reward=max(max_reward, win)
        allwins.append(win)
    print '-----------theme %d: %s------------------' %  (themeid, SPINTYPE[freespin])
    print 'max_reward/bet',  max_reward*1.0/linecount
    print 'scatter_times ratio: ', scatter_times*1.0/run_times,'bonus_times ratio: ', bonus_times*1.0/run_times
    print 'win_times/run_times: ', win_times*1.0/run_times, 'total_win/win_times: ', totalwin*1.0/win_times
    print 'bigwin, megawin, superwin', bigwin*1.0/run_times, megawin*1.0/run_times, superwin*1.0/run_times
    print 'five in line: ', five, ', six in line: ', six
    print 'total_win %d, total_cost %d, return rate %f' % (totalwin, total_cost, totalwin*1.0/total_cost)
    group= [(k, len(list(v))) for k, v in groupby(allwins, key=lambda x: x>0)]
    print 'max winning streak', max([v for k,v in group if k]+[0]),  ', max losing streak', max([v for k,v in group if not k]+[1])
    return totalwin*1.0/total_cost
    #aver=totalwin*1.0/run_times
    #print 'fangcha', sum(map(lambda win: (win-aver)*(win-aver), allwins))/run_times
def check():
    for themeid in THEME_CONFIG.keys():
        for t in  ('reels_N', 'reels_F', 'reels_W', 'reels_H'):
            if 0 in THEME_CONFIG[themeid][t][0]+THEME_CONFIG[themeid][t][4]:
                print t,  THEME_CONFIG[themeid][t][0]+THEME_CONFIG[themeid][t][4]
                exit('0 in wrong column, theme %d' % themeid)
            if 1 in THEME_CONFIG[themeid][t][1]+THEME_CONFIG[themeid][t][3]:
                print t,THEME_CONFIG[themeid][t][1]+THEME_CONFIG[themeid][t][3]
                exit('1 in wrong column, theme %d' % themeid)
            for i in range(len(THEME_CONFIG[themeid]['rows'])):
                l = THEME_CONFIG[themeid]['rows'][i]
                x = THEME_CONFIG[themeid][t][i]
                last=-10000
                if 1:#themeid not in (2,3):
                    for i in range(len(x)*2):
                        checknums=(0,1)if themeid!=4 else (0,1,2)
                        if x[i%len(x)] in checknums:
                            if i-last<l:
                                print  t,  i, last, l, x
                                exit('theme %d, 0 1 in same column' % themeid)
                            last=i
                if t=='reel_W' and themeid==2 and i in (2,3,4):
                    for i in range(4,len(x)):
                        if x[i-4:i].count(-1)==0:
                            exit('theme 2 wild fail')

if __name__=='__main__':
    from sys import argv

    check()
    try:
        run_times=int(argv[1])
        themeids=map(int, argv[2:]) if len(argv)>2 else THEME_CONFIG.keys()
        for themeid in themeids:
            for i in range(4):
                spin_result(themeid,i,run_times=run_times)
    except Exception, e:
        print e
        for themeid in THEME_CONFIG.keys():
            for i in range(4):
                spin_result(themeid,i)
