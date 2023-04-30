#Importing libraries

import numpy as np
from scipy.stats import norm
import pandas as pd
import matplotlib.pyplot as plt

# Generating demand scenarios
def generate_demand_scenarios(month, N, dataset, start, end ):

    # Filter data by month
    dataset_month = dataset[dataset['MONTH'] == month]

    # Calculate mean and std for each day and hour
    df_mean = dataset_month.groupby(['DAY', 'HOUR'])['NET_LOAD'].mean()
    df_std = dataset_month.groupby(['DAY', 'HOUR'])['NET_LOAD'].std()

    # Normal distribution probability of each segment
    segment1 = [norm.pdf(df_mean[i,j], loc=df_mean[i,j], scale=df_std[i,j]) for i in [*range(start,end)] for j in [*range(1,25)]]
    segment2 = [norm.pdf(df_mean[i,j]+df_std[i,j], loc=df_mean[i,j], scale=df_std[i,j]) for i in [*range(start,end)] for j in [*range(1,25)]]
    segment3 = [norm.pdf(df_mean[i,j]-df_std[i,j], loc=df_mean[i,j], scale=df_std[i,j]) for i in [*range(start,end)] for j in [*range(1,25)]]

    # Normalize the probability values
    prob_norm1 = [segment1[i]*1000/((segment1[i]+segment2[i]+segment3[i])*1000) for i in [*range((end-start)*24)]]
    prob_norm2 = [segment2[i]*1000/((segment1[i]+segment2[i]+segment3[i])*1000) for i in [*range((end-start)*24)]]
    prob_norm3 = [segment3[i]*1000/((segment1[i]+segment2[i]+segment3[i])*1000) for i in [*range((end-start)*24)]]

    # Accumulated normalized probability
    prob_acc1 = [prob_norm1[i] for i in [*range(len(prob_norm1))]]
    prob_acc2 = [prob_norm1[i]+prob_norm2[i] for i in [*range(len(prob_norm1))]]
    prob_acc3 = [prob_norm1[i]+prob_norm2[i]+prob_norm3[i] for i in [*range(len(prob_norm1))]]

    # Convert dataframes to lists
    m=pd.DataFrame(df_mean)
    m = m.reset_index(drop=True)
    m.index = pd.RangeIndex(0, 720)
    m_list = m.values.tolist()

    # Monte-carlo simulation
    std=pd.DataFrame(df_std)
    std = std.reset_index(drop=True)
    std.index = pd.RangeIndex(0, 720)
    std_list = std.values.tolist()
    scenario_prob = []
    day_values = []
    for i in range(N):
      scenario = []
      day_prob = 1
      day_prob = np.float128(day_prob)
      for j in range((end-start)*24):
        rand = np.random.uniform(0,1)
        # rand=abs(np.random.randn())
        if rand <= prob_acc1[j]:
            scenario.append(m_list[j][0]-std_list[j][0])
            day_prob *= prob_norm1[j]

        elif rand <= prob_acc2[j]:
            scenario.append(m_list[j][0])
            day_prob *= prob_norm2[j]

        else:
            scenario.append(m_list[j][0]+std_list[j][0])
            day_prob *= prob_norm3[j]

      scenario_prob.append(day_prob)
      day_values.append(scenario)

    # Normalized scenario probability
    scenario_prob_norm = [scenario_prob[i]/sum(scenario_prob) for i in range(N)]

    return (day_values,scenario_prob_norm)

# Format demand scenarios
def format_demand_scenarios(day_values):
    c=pd.DataFrame(day_values)
    demand = {}
    for x in day_values:
        h=len(x)
    for i in range(h):
        demand[i] = {}
        for j in range(len(day_values)):
            demand[i][j+1] = c.iloc[j, i]
    return(demand)

# Plot demand scenarios
def plot_demand_scenarios(day_values, scenario_prob_norm, name=None):
    num_scenarios = len(day_values)
    plt.figure(figsize=(15, 7))
    for i in range(num_scenarios):
        plt.plot(day_values[i], label='Scenario ' + str(i+1) + ' (Prob: {:.0%})'.format(scenario_prob_norm[i]))
    plt.xlabel("Hour")
    plt.ylabel("Demand [kW]")
    if name == None:
        pass
    else:
        plt.title(""+str(name))
    plt.legend()
    plt.show()