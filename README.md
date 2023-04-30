# Scenario Generation

<p align="justify">  
This repository explains the process of a hybrid scenario generation module with a scenario tree and Monte Carlo simulation. 
Each scenario is a possible realization of the random variables along with their probability of occurrence ($\Pi_s$). The scenario generation utilizes climate projection datasets and demand forecasts to generate electricity demand and supply scenarios.
Different scenario trees can be structured depending on the number of climate and demand models. The following figure shows an example of a scenario tree consisting of four climates (C1-C4) and three demand (D1-D3) models. As none of the climate and demand models have priority over the other, by considering the same probability of occurrence of all models, the probability of each branch is:
  
$\Pi_{Branch}=\frac{1}{Number of climate models}\cdot \frac{1}{Number of demand models}$
  
<p align="center">
<img src="https://github.com/rouzbehshi/ScenGen/blob/1c49562a26687c1b82563a39de9cc2b1dd4f486a/Figures/Fig7.jpg"  alt="Scenario tree" title="Scenario tree" width="400" >
</p>

## Methodology

In the next step, the Monte-Carlo simulation generates $N_s$ number of scenarios based on the mean and standard deviation of values of each climate variable and electricity demand on each tree branch. The Monte Carlo simulation procedure is adopted from the paper titled " *An efficient scenario-based stochastic programming framework for multi-objective optimal micro-grid operation* " by Niknam et al. [[1]](https://doi.org/10.1016/j.apenergy.2012.04.017). The Monte Carlo simulation steps are as follows:

1. The normal distribution of each time step is calculated based on the mean ($m$) and standard deviation ($\delta$) of each step's values in all years (e.g., $m(G_{day1})=mean(G_{day1,2020}, G_{day1,2021},..., G_{day1,2030})$ ).
2. The normal distribution functions are obtained for all time steps. 
3. Each function is divided into three segments ($l$), each by a $\delta$ distance ($l_1=m,l_2=m-\delta,l_3=m+\delta$). Depending on the desired level of preciseness, the number of segments can be increased.

<p align="center">
<img src="https://github.com/rouzbehshi/ScenGen/blob/1c49562a26687c1b82563a39de9cc2b1dd4f486a/Figures/Fig9.png"   width="400" >
</p>

4. The cumulated probability of segments is normalized to unity based on the following equation in a way in which their summation becomes equal to 1 ( $\Pi_{l_1}^{N} + \Pi_{l_2}^{N} + \Pi_{l_3}^{N} = 1$ ):

$$ \Pi_{l_i}^{N}=\frac{\Pi_{l_i}}{\sum_{i} {\Pi_{l_i}}} \quad i\in{\{1,2,3\}} $$

5. A random number is generated for each time step. The segment with a probability less or equal to the random number is selected as the value of that step, and the corresponding probability is the probability of that segment ($\pi_{l_{s,t}}$). 

<p align="center">
<img src="https://github.com/rouzbehshi/ScenGen/blob/1c49562a26687c1b82563a39de9cc2b1dd4f486a/Figures/Fig8.png"   width="400" >
</p>

6. The probability of all sample data (SD) is normalized using the equation:

$$ \Pi_{SD} = \frac{\Pi_{l_{s,t}}} {\sum_{s=1} \prod_{t=1} \Pi_{l_{s,t}}} $$

By knowing the probability of each sample data obtained from step 6, the probability of each scenario is 
$\Pi_s=\Pi_{Branch}\cdot\Pi_{SD}$ .


## Climate Scenarios

Climate projection datasets obtained from Global Climate Models (GCMs) are used as input to generate the climate scenarios. GCMs have been developed to forecast the future climate. Daily solar irradiance and maximum/minimum temperature are extracted from 2020 to 2030 from 2 climate models (MIROC and CNRM-CM5) in two scenarios (RCP 4.5 and RCP 8.5).

The first step after importing the climate model dataset is preprocessing. 
The ```solarirrad_preprocessing``` convert the time index of the solar irradiance dataset to pandas' date and time first and extracts the daily values of solar irradiance for the desired ```month```. 

```generate_solarirrad_scenarios``` generates $N$ scenarios for each input ```dataset```. The outputs of this function are the values of scenario ```day_values``` and their corresponding probability ```scenario_prob_norm```.```plot_data_and_climate_scenarios``` function is used to plot the results. In the following figures, the left figures show daily solar irradiance in each day for the years 2020 to 2030, and the right figures show the generated scenarios: 

<p align="center">
<img src="https://github.com/rouzbehshi/ScenGen/blob/df1cca5250e814eb3e493dc948870d51c50cf024/Figures/cnrm-45.png"   width="600" >
</p>
<p align="center">
<img src="https://github.com/rouzbehshi/ScenGen/blob/df1cca5250e814eb3e493dc948870d51c50cf024/Figures/cnrm-85.png"   width="600" >
</p>
<p align="center">
<img src="https://github.com/rouzbehshi/ScenGen/blob/df1cca5250e814eb3e493dc948870d51c50cf024/Figures/miroc45.png"   width="600" >
</p>
<p align="center">
<img src="https://github.com/rouzbehshi/ScenGen/blob/df1cca5250e814eb3e493dc948870d51c50cf024/Figures/miroc85.png"   width="600" >
</p>

The values of solar irradiance are daily average.  To find the total power output of PV each day, first, the daily average values are converted to daily sum by multiplying the sunlight hour of each day in the ``` solarirrad_daily_avg_to_daily_sum ``` function.
In the next step, the daily power output of a PV with 100 $W_Nominal$ is calculated with ```pv_generation``` as follows:

$$ P_{PV}(t) = P_{STC} \cdot n\cdot \frac{E_m (t)}{E_{STC}}\cdot \[ 1+k\cdot (T_m (t)-T_{STC}) \] $$

Where $P_{PV} (t)$ is the power output of PV, $P_{STC}$ is the maximum power output of PV in the standard test condition,  $E_m (t)$ $[\frac{W}{m^2}]$ is the solar irradiance at time t, $E_{STC}$ is the solar irradiance in standard test condition ($= 1000 [\frac{W}{m^2}]$), $n$ is the number of PV panels, $k$ is the temperature coefficient ($= -0.0049 [\frac{1}{^{\circ} C}]$), $T_{STC}$ is the temperature of PV in standard test condition ($= 25^{\circ} C$), and $T_m (t)$ is the PV temperature and is calculated as follows:

$$ T_{m}(t)=T_{amb}+{\mathcal{E}}_{PV}\cdot \frac{{E_{m}(t)}}{E_{STC}} $$

$$ T_{amb}=\frac{T_{max}+T_{min}}{2} $$

Where $T_{amb}$ is the ambient temperature and ${\mathcal{E}}_{PV}$ is the constant given by manufacturer (= 30).
To convert the PV daily power output to hourly, it is assumed that the position of the sun each day across all years is the same, and only the intensity of solar irradiance will change each year. As a result, the hourly solar irradiance of a typical year is imported, and the ```solar_irrad_hourly_coeff``` function is used to normalize the hourly solar irradiance of each day. The power output of PV at each hour is then calculated by obtained normalized coefficients and the daily power output with the ```daily_to_hourly_pv_generation``` function. The hourly power output of PV in each scenario is plotted with the ```plot_pv_scenarios``` function. The following figures show the power output of the PV for CNRM-CM5 RCP4.5 for two representative days:

<p align="center">
<img src="https://github.com/rouzbehshi/ScenGen/blob/df1cca5250e814eb3e493dc948870d51c50cf024/Figures/cnrm45-hourly.png"   width="600" >
</p>

```format_pv_scenarios``` function is used to reshape the output to be used in the final step, scenario tree generation.

</p>

## Demand Scenarios
The same procedure as Climate Scenarios is adopted to generate N scenarios based on different demand models. ```generate_demand_scenarios``` function inputs the demand model dataset, the required number of scenarios, and the study's month, start, and end date. The outputs of this function are the values of scenario ```day_values``` and their corresponding probability ```scenario_prob_norm```. ```plot_demand_scenarios``` function is used to plot the results. ```format_demand_scenarios``` function is used to reshape the output to be used in the final step, scenario tree generation.. The following figure shows five scenarios extracted from a demand model with their corresponding probability.

<p align="center">
<img src="https://github.com/rouzbehshi/ScenGen/blob/df1cca5250e814eb3e493dc948870d51c50cf024/Figures/Fig17.png"   width="600" >
</p>

## Scenario Tree
In the Final step, the generated PV and Demand scenarios are combined to find the values of the scenario tree. First, the scenario values and probabilities for each branch are calculated by ```combine_scenario_branch``` and ```combine_probability_branch``` functions. In the next step, the scenario values and probabilities of the scenario tree are converted to a list with ```combine_scenario_tree``` and ``` combine_probability_tree``` functions. ```reformat_scenarios``` is used to reformat the values of the scenario tree to be used in future studies. By considering five scenarios extracted from each of the four climate models and three demand models, the final scenario tree contains 300 scenarios. The following figure shows the cumulative probability of all scenarios in the scenario tree.

<p align="center">
<img src="https://github.com/rouzbehshi/ScenGen/blob/8b2b24392ad4da996cf72b3a2b98f40575dcd6dc/Figures/Fig26.png"   width="600" >
</p>
