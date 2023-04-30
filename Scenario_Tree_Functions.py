#Combining climate and demand scenario VALUES of each scenario tree BRANCH
def combine_scenario_branch(climate, demand):
    climate_combined = {}
    demand_combined = {}
    for i in range(48):
        climate_combined[i] = []
        demand_combined[i] = []
        for j in range(1,6):
            for k in range(1,6):
                climate_combined[i].append(climate[i][j])
                demand_combined[i].append(demand[i][k])
    return climate_combined, demand_combined

#Combining climate and demand scenario PROBABILITIES of each scenario tree BRANCH
def combine_probability_branch(climate_probability, demand_probability,N_Branch):
  combined_probs = []
  for demand_prob in demand_probability:
    for climate_capacity_probability in climate_probability:
      combined_probs.append(round(demand_prob*climate_capacity_probability*N_Branch,5))
  return combined_probs

#Combining scenario VALUES of the TREE
def combine_scenario_tree(dict_list):
    # create an empty dictionary to store the combined values
    combined_dict = {}

    # get the number of dictionaries in the input list
    N_dictionaries = len(dict_list)

    # loop over each dictionary
    for i in range(N_dictionaries):
        current_dict = dict_list[i]

        # loop over each list in the current dictionary
        for j in range(48):
            # if this is the first dictionary, initialize the list in the combined dictionary
            if i == 0:
                combined_dict[j] = []

            # append the values from the current list to the corresponding list in the combined dictionary
            combined_dict[j].extend(current_dict[j])

    # return the combined dictionary
    return combined_dict

#Combining scenario PROBABILITIES of the TREE
def combine_probability_tree(lists):
    # create an empty list to store the combined values
    combined_list = []

    # loop over each list
    for lst in lists:
        # append the values from the current list to the combined list
        combined_list.extend(lst)

    # return the combined list
    return combined_list

# Reformatting the output for the optimization module
def reformat_scenarios(original_list):
    return {key: {index + 1: value for index, value in enumerate(val)} for key, val in original_list.items()}
