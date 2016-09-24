"""
Joanna Han 

Riot Coding Challenge: Find the most efficient spell in the game. 

General Approach:

Read Riot Games stat-data-v1.2 API and requested spells and stats of champs only.
Filtered out resources used, cost, and effect. Filtered out spells that 
did not have AP or AD measurements. Compared the costs of remaining spells 
with their respective quantitative effects. Seemed to be linearly correlated, so 
cost became the x-array and effect became the y-array. 
The spells with the highest slope would be the ones with highest cost efficiency. 
"""

import json
import unicodedata
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

json_data=open('/Users/Joanna/Desktop/Riot_League_API_v3.json').read()
data=json.loads(json_data)
damage_dict={} #dictionary defining type of damage/buff from spells
effect_dict={} #dictionary defining damage done from spells
resource_dict={} #dictionary defining type of resource needed for spells
cost_dict={} #dictionary defining amount of resources needed for spells
label_dict={} #dictionary defining effect type needed in calculations
original_data=data
data = data["data"]

#function to get value of specific nested dictionary path (listpath)
def get_value(mapDict, listpath): #listpath - [most inclusive idx -> least inclusive idx]
    return reduce(lambda d, idx: d[idx], listpath, mapDict)

Q_final={}
W_final={}
E_final={}
R_final={}


#iterates through champs and labels all spells 
for champ in data:
	temp=get_value(data, [champ, "spells"])
	Qspell=temp[0]
	Wspell=temp[1]
	Espell=temp[2]
	Rspell=temp[3]
	temp_tot=[Qspell,Wspell,Espell,Rspell]
	indexes={0:'Q',1:'W',2:'E',3:'R'}
	#print temp

	#returns resource, effect (damage dealt), and cost of all spells
	for idx, spell in enumerate(temp_tot): #spell: value of spells
		for attribute in spell: #attribute: keys in spells
			if attribute=="vars":
				damage_type=spell["vars"]
				for damage in damage_type:
					damage_dict[champ+'_'+indexes[idx]]= damage["link"] #analyzes spell type
					#print champ, indexes[idx], "damage/buff type:", damage["link"] #prints out damage or buff type 
			if attribute=="effect":
				effect=spell[attribute]
				effect_dict[champ+'_'+indexes[idx]]= effect
				#print champ, indexes[idx], "effect", effect[1]
			if attribute=="resource":
				resource=spell[attribute]
				resource_dict[champ+'_'+indexes[idx]]= resource
				#print champ, indexes[idx], "resource", resource
			if attribute=="cost":
				cost=spell[attribute]
				cost_dict[champ+'_'+indexes[idx]]= cost
				#print champ, indexes[idx], "cost", cost
		if spell["leveltip"]["label"]!=None:
			label=spell["leveltip"]["label"]
			label_dict[champ+'_'+indexes[idx]]= label
			#print champ, indexes[idx], "label", label


#filter out only ability power and attack damage in all dictionaries
deleted_keys=[]
deleted_values=[]
for key, value in damage_dict.iteritems():
	value=unicodedata.normalize('NFKD',value).encode('ascii','ignore') #convert unicode to string
	#filters out non-ap or ad measurable spells (could be used for other analyses like most efficient cooldown rate or most efficient special)
	if value != "spelldamage" and value != "attackdamage" and value != "bonusattackdamage" and value != "@dynamic.abilitypower" and value != "@dynamic.attackdamage":
		deleted_keys.append(key)
		deleted_values.append(value)
#print deleted_values
#print deleted_keys

for key in deleted_keys:
	#print key
	del damage_dict[key]
	del effect_dict[key]
	del resource_dict[key]
	del cost_dict[key]
	del label_dict[key]

#take the intersection of all the dictionaries for fair comparison
all_dictionaries=[damage_dict,effect_dict,resource_dict,cost_dict, label_dict]


#defines intersection of keys in 2 dictionaries
def intersection_2_dicts(s1,s2):
	common_keys=[]
	for key in s1:
		if key in s2 and key!=None:
			common_keys.append(key)
	return common_keys
#print "hello", intersection_2_dicts(damage_dict,effect_dict)

#defines intersection of keys iterating through a list of dictionaries		
def intersect_dicts(all_dicts):
	return reduce(intersection_2_dicts, all_dicts)
#get all intersecting keys 
for i in all_dictionaries:
	all_common_keys=intersect_dicts(all_dictionaries)
#print all_common_keys
#print len(all_common_keys)


ddict={}
edict={}
rdict={}
cdict={}
ldict={}

#filter dictionaries to include only common keys
def filter_dict(dictionary, new_dict):
	for key in dictionary:
		if key in all_common_keys:
			new_dict[key]=dictionary[key]
filter_dict(damage_dict, ddict)
filter_dict(effect_dict, edict)
filter_dict(resource_dict, rdict)
filter_dict(cost_dict, cdict)
filter_dict(label_dict, ldict)

#sort dictionaries based on key
def sort_dict(dictionary, new_dict):
	sorted_keys=sorted(dictionary)
	for key in sorted_keys:
		new_dict[key]=dictionary[key]

ddict2={}
edict2={}
rdict2={}
cdict2={}
ldict2={}

sort_dict(ddict,ddict2)
sort_dict(edict,edict2)
sort_dict(rdict,rdict2)
sort_dict(cdict,cdict2)
sort_dict(ldict,ldict2)

#clean up effect dictionary, removes cost repeats and 'none' in effects
for e_key, e_value in edict2.iteritems():
	for l_key,l_value in ldict2.iteritems():
		for idx,val in enumerate(e_value):
			if val in cdict2.values():
				e_value.remove(val)
				l_value=l_value[:idx]+l_value[idx+1:]
			if val == None:
				e_value.remove(val)
				l_value=l_value[:idx]+l_value[idx+1:]
#print label_dict
#print ldict

keep_effects={}
for l_idx, l_val in ldict2.iteritems():
	for i,j in enumerate(l_val):
		j=unicodedata.normalize('NFKD',j).encode('ascii','ignore') #convert unicode to string
	 	if (("Damage" or "Heal" or "Health")in j) and (("Ratio") not in j):
	 		keep_effects[l_idx]=i
keep_effects2={}
sort_dict(keep_effects,keep_effects2)

#initialize new list of wanted effect values
new_vals=[]

#append wanted effect values to list
for key,value in keep_effects2.iteritems():
	for i in edict2.values():
		if len(i)>=value+1: 
			new_vals.append(i[value])


#iterate simultaenously and update keep_effects2 to include values instead of indices
for i,j in zip(new_vals,keep_effects2):
	keep_effects2[j]=i    #keep_effects2 is new dictionary on effect outputs

#initialize new dictionary on efficiences 
efficiency_dict={}

#calculate most efficient spell based on output (effect, y_axis) vs cost (x_axis)
#efficiency_dict returns slopes/efficiency of all pertinent spells
for (cost_idx,cost_value) in cdict2.iteritems():
	for (effect_idx,effect_value) in keep_effects2.iteritems():	
		cost_x=np.asarray(cost_value)
		effect_y=np.asarray(effect_value)
		if len(cost_x)==len(effect_y) and cost_idx==effect_idx:
			slope, intercept, r_value, p_value, std_err =stats.linregress(cost_x,effect_y)
			if np.isnan(slope)!=True: #Filters out all 'nan' values generated
				efficiency_dict[cost_idx]=slope

#print dictionary with all champion spell costs
print "all champ spell costs: ", cdict2

#print dictionary with all champion spell effects
print "all champ spell effects: ", edict2

#print dictionary with champ spells (key) and efficiency values (from slope of linear regression of cost vs effect)			
print "efficiency (slope) of champion spells: ", efficiency_dict

#print spell with highest slope
#highest slope means most cost efficiency: lesser cost for more effect
print "most efficient spell:" , max(efficiency_dict,key=efficiency_dict.get)

		





