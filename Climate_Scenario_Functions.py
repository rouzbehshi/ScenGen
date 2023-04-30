# Importing libraries
import numpy as np
from scipy.stats import norm
import pandas as pd
import matplotlib.pyplot as plt

# Preprocessing the datasets
def solarirrad_preprocessing(dataset, month):
    dataset = pd.DataFrame(dataset)
    dataset['time'] = pd.to_datetime(dataset['time'])
    year_dataset=dataset[(dataset['time'].dt.year >= 2020) & (dataset['time'].dt.year <= 2030)]
    month_dataset = year_dataset[year_dataset['time'].dt.month == month]
    month_dataset = month_dataset.sort_values(by='time')
    month_dataset = month_dataset.reset_index(drop=True)
    daily_dataset = month_dataset.iloc[:,-1]
    df=pd.DataFrame(daily_dataset)
    result_dict = {}
    for i in range(0, len(df), 30):
        result_dict[i] = df.iloc[i:i+30,-1].tolist()
    result_dict_values = {key: value for key, value in result_dict.items()}
    result_list = list(result_dict_values.values())

    return result_list

def t_avg_preprocessing(t_avg, year, month):
    t_avg = pd.DataFrame(t_avg)
    t_avg['time'] = pd.to_datetime(t_avg['time'])
    t_avg_year = t_avg[t_avg['time'].dt.year == year]
    month_t_avg = t_avg_year[t_avg_year['time'].dt.month == month]
    month_t_avg = month_t_avg.sort_values(by='time')
    month_t_avg = month_t_avg.reset_index(drop=True)
    daily_t_avg = month_t_avg['Avg_temp']
    return daily_t_avg

# Generating climate scenarios
def generate_solarirrad_scenarios(dataset, N):
    # Mean and standard deviation of each day
    mean = [np.mean([dataset[i][j] for i in range(len(dataset))]) for j in range(30)]
    stdev = [np.std([dataset[i][j] for i in range(len(dataset))]) for j in range(30)]

    # Normal distribution probability of each segment
    segment1 = [norm.pdf(mean[i], loc=mean[i], scale=stdev[i]) for i in range(30)]
    segment2 = [norm.pdf(mean[i]+stdev[i], loc=mean[i], scale=stdev[i]) for i in range(30)]
    segment3 = [norm.pdf(mean[i]-stdev[i], loc=mean[i], scale=stdev[i]) for i in range(30)]

    # Normalize the probability values
    prob_norm1 = [segment1[i]/(segment1[i]+segment2[i]+segment3[i]) for i in range(30)]
    prob_norm2 = [segment2[i]/(segment1[i]+segment2[i]+segment3[i]) for i in range(30)]
    prob_norm3 = [segment3[i]/(segment1[i]+segment2[i]+segment3[i]) for i in range(30)]

    # Accumulated normalized probability
    prob_acc1 = [prob_norm1[i] for i in range(30)]
    prob_acc2 = [prob_norm1[i]+prob_norm2[i] for i in range(30)]
    prob_acc3 = [prob_norm1[i]+prob_norm2[i]+prob_norm3[i] for i in range(30)]

    # Scenario probability
    scenario_prob = []
    day_values = []
    for i in range(N):
        scenario = []
        day_prob = 1
        for j in range(30):
            rand = np.random.uniform(0,1)
            if rand <= prob_acc1[j]:
                scenario.append(mean[j]-stdev[j])
                day_prob *= prob_norm1[j]
            elif rand <= prob_acc2[j]:
                scenario.append(mean[j])
                day_prob *= prob_norm2[j]
            else:
                scenario.append(mean[j]+stdev[j])
                day_prob *= prob_norm3[j]
        scenario_prob.append(day_prob)
        day_values.append(scenario)

    # Normalized scenario probability
    scenario_prob_norm = [scenario_prob[i]/sum(scenario_prob) for i in range(N)]

    return day_values, scenario_prob_norm

# Plot climate scenarios
def plot_data_and_climate_scenarios(dataset, day_values, scenario_prob_norm,name=None):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18,6))

    # plot the input data
    for i in range(len(dataset)):
        ax1.plot(dataset[i], label='Year '+str(i+2020))
    ax1.legend(loc='best')
    if name==None:
        pass
    else:
        ax1.set_title(name)


    N = len(day_values)

    # Plot each scenario
    for i in range(N):
        ax2.plot(day_values[i], label='Scenario ' + str(i+1) + ' (Prob: {:.0%})'.format(scenario_prob_norm[i]))

    # Add legend
    plt.legend()
    ax1.set_xlabel('Day')
    ax1.set_ylabel('Solar irradiance [W/m^2]')
    ax2.set_xlabel('Day')
    ax2.set_ylabel('Solar irradiance [W/m^2]')
    ax2.set_title('Generated scenarios')
    # Show plot
    plt.show()

# Converting daily average solar irradiance to daily sum
def solarirrad_daily_avg_to_daily_sum(day_values,sunlight_hour):
  solar_capacity = [[day_value[i]*sunlight_hour for i in range(30)] for day_value in day_values]
  return solar_capacity

# Power output of a 100 [W] PV
def pv_generation(daily_irrad_scenario, daily_t_avg, N):
    pv_generation = [[100 * daily_irrad_scenario[i][j] / 1000 * (1 - 0.0049 * (daily_t_avg[j] + daily_irrad_scenario[i][j] / 1000 * 30 - 25)) for j in range(30)] for i in range(N)]
    return pv_generation

# Historical solar Irradiance coefficients
def solar_irrad_hourly_coeff(month, solar_irrad_hourly):
    solar_irrad_hourly = pd.DataFrame(solar_irrad_hourly)
    solar_irrad_hourly['time'] = pd.to_datetime(solar_irrad_hourly['time'])
    september_solar_irrad_hourly = solar_irrad_hourly[solar_irrad_hourly['time'].dt.month == month]
    september_solar_irrad_hourly.loc[:, 'day'] = september_solar_irrad_hourly['time'].dt.date
    sum_gi = september_solar_irrad_hourly.groupby('day')['G(i)'].transform('sum')
    september_solar_irrad_hourly.loc[:, 'norm_gi'] = september_solar_irrad_hourly['G(i)'] / sum_gi
    september_solar_irrad_hourly = september_solar_irrad_hourly.sort_values(by='time')
    september_solar_irrad_hourly = september_solar_irrad_hourly.reset_index(drop=True)
    return september_solar_irrad_hourly

# Converting daily PV power output to hourly
def daily_to_hourly_pv_generation(daily_pv_generation, solar_irrad_hourly_coeff, N):
    capacity_factor_hourly = [[daily_pv_generation[i][j] * solar_irrad_hourly_coeff.loc[k, 'norm_gi']
                               for k in range(j*24,(j+1)*24)]
                              for i in range(N) for j in range(30)]
    return capacity_factor_hourly

# Format PV scenarios
def format_pv_scenarios(hourly_pv_generation, N, start_day, end_day):
    D = end_day - start_day
    df4 = []
    extract = []
    for i in range(N):
        first_day = i * 30
        last_day = (i + 1) * 30
        extract.append(hourly_pv_generation.iloc[first_day + start_day : first_day + end_day, :])

    df_list = []
    for sub_list in extract:
        df = pd.DataFrame(sub_list)
        df_list.append(df)
    extracted_hourly_pv_generation = pd.concat(df_list)

    extracted_hourly_pv_generation = extracted_hourly_pv_generation.reset_index()
    extracted_hourly_pv_generation = extracted_hourly_pv_generation.T
    extracted_hourly_pv_generation = extracted_hourly_pv_generation.iloc[1:, :]

    for i in range(0, N * D, D):
        cols = [extracted_hourly_pv_generation.iloc[:, j] for j in range(i, i + D)]
        df3 = pd.concat(cols, axis=0)
        df4.append(df3)

    extracted_capacity_factor_hourly_for_model = pd.DataFrame()
    for i in [*range(len(df4))]:
        extracted_capacity_factor_hourly_for_model[i] = df4[i]
    extracted_capacity_factor_hourly_for_model = extracted_capacity_factor_hourly_for_model.reset_index()
    extracted_capacity_factor_hourly_for_model = extracted_capacity_factor_hourly_for_model.iloc[:, 1:]

    data = extracted_capacity_factor_hourly_for_model.to_dict(orient='index')
    pv_generation_hourly = {i: {j + 1: data[i][j] for j in data[i]} for i in data}
    return pv_generation_hourly

# Plot PV scenarios (CFPV)
def plot_pv_scenarios(capacity_factor_hourly, daily_irrad_prob_norm,start, end, N, name=None):
    fig, axs = plt.subplots(N, 1, figsize=(10, 14))

    for i, ax in enumerate(axs.flatten()):
        start_row = i * 30
        end_row = (i + 1) * 30
        for j in range(start_row + start-1, start_row + end-1):
            ax.plot(capacity_factor_hourly.columns, capacity_factor_hourly.iloc[j,:], label='Day ' + str(j  - start_row+1)+' (prob = '+str(round(daily_irrad_prob_norm[i],2)))
        if name==None:
            ax.set_title("Capacity factor from Day "+str(start)+ " to Day "+str(end)+ " in Scenario " + str(i+1))
        else:
            ax.set_title("Capacity factor from Day "+str(start)+ " to Day "+str(end)+ " in Scenario " + str(i+1)+ ' ('+ str(name)+')')

        ax.legend()
        ax.set_xlabel('Hour')
        ax.set_ylabel('Capacity factor [in Percent]')
    fig.subplots_adjust(wspace=0.5, hspace=1)
    plt.tight_layout()