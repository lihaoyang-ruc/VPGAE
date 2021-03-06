import time
import dataset
import math
import my_cost_model
import argparse

import VPGAE
import column
import row
import optimal
import hillclimb

import numpy as np

from unnecessary_data_read import fraction_of_unnecessary_data_read
from reconstruction_joins import number_of_joins
from workload_class import VPGAE_Workload, Workload

parser = argparse.ArgumentParser(description='VPGAE')
parser.add_argument('--dataset', default="TPC-H", type=str, help='name of the experiment you want to run. (options: TPC_H, TPC_DS, random_dataset, HAP).')

# TPC-H benchmark experiments
def TPC_H_exp():
	use_OPTIMAL = False
	dataset_ = dataset.tpch_workload(10)

	beam_costs = []
	kmeans_costs = []
	hill_costs = []
	column_costs = []
	row_costs = []
	optimal_costs = []
	hyrise_costs = []
	navathe_costs = []
	o2p_costs = []

	beam_partitions_list = []
	kmeans_partitions_list = []
	hill_partitions_list = []
	column_partitions_list = []
	row_partitions_list = []
	optimal_partitions_list = []
	hyrise_partitions_list = []
	navathe_partitions_list = []
	o2p_partitions_list = []

	workload_list = []

	for i,data in enumerate(dataset_):
		workload = Workload(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8])
		vpgae_workload = VPGAE_Workload(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8])

		num_node = vpgae_workload.affinity_matrix.shape[0]

		beam_cost, beam_partitions = VPGAE.partition(algo_type="VPGAE-B",workload=vpgae_workload, n_hid=num_node, n_dim=2*num_node, k=2, origin_candidate_length=6, beam_search_width=3)
		kmeans_cost, kmeans_partitions = VPGAE.partition(algo_type="VPGAE",workload=vpgae_workload, n_hid=num_node, n_dim=2*num_node, k=2)
		
		hill_cost, hill_partitions = hillclimb.partition(workload=workload)
		column_cost, column_partitions = column.partition(workload=workload)
		row_cost, row_partitions = row.partition(workload=workload)
		if use_OPTIMAL:
			optimal_cost, optimal_partitions = optimal.partition(workload=workload)
			optimal_costs.append(optimal_cost)
			optimal_partitions_list.append(optimal_partitions)
		
		beam_costs.append(beam_cost)
		kmeans_costs.append(kmeans_cost)
		hill_costs.append(hill_cost)
		column_costs.append(column_cost)
		row_costs.append(row_cost)
		
		beam_partitions_list.append(beam_partitions)
		kmeans_partitions_list.append(kmeans_partitions)
		hill_partitions_list.append(hill_partitions)
		column_partitions_list.append(column_partitions)
		row_partitions_list.append(row_partitions)

		workload_list.append(workload)

	hyrise_partitions_list = [[[8, 3], [2], [6, 5], [7], [4], [1]],
							[[13, 12], [2], [15], [14], [11], [3], [7], [6], [9], [16, 4], [10, 8], [1], [5]],
							[[3], [8], [6], [5], [1, 2], [9], [4], [7]],
							[[6], [7], [2], [5], [3], [1, 4]],
							[[9, 8], [3], [5], [4], [2], [1], [6], [7]],
							[[5], [4], [3], [2, 1]],
							[[3], [2, 1], [4]],
							[[1, 2], [3]]]
	
	for i in range(len(workload_list)):
		hyrise_costs.append(my_cost_model.calculate_cost_fair(hyrise_partitions_list[i],workload_list[i]))

	navathe_partitions_list = [[[7, 3], [6, 5], [4], [2], [8], [1]],
							[[16, 10], [9], [15], [13, 12], [3], [7, 6], [11], [5], [2], [14], [8], [4], [1]],
							[[7, 3], [6], [5], [2], [4], [8], [9], [1]],
							[[7, 6], [3], [4], [2], [5], [1]],
							[[9, 3], [7], [4], [6], [5], [2], [8], [1]],
							[[5, 4], [3, 2, 1]],
							[[4], [3, 2, 1]],
							[[3], [2, 1]]]
	
	for i in range(len(workload_list)):
		navathe_costs.append(my_cost_model.calculate_cost_fair(navathe_partitions_list[i],workload_list[i]))

	o2p_partitions_list = [[[7, 3], [5], [6], [4], [2], [8], [1]],
							[[16, 10], [9], [15], [12], [13], [3], [7, 6], [11], [5, 2], [14], [8], [4], [1]],
							[[7, 6, 3], [5], [2], [8, 4], [9], [1]],
							[[7, 6], [3], [4], [2], [5], [1]],
							[[9, 3], [7, 4], [6], [5], [2], [8], [1]],
							[[5, 4], [3, 2, 1]],
							[[4], [3, 2, 1]],
							[[2, 1], [3]]]

	for i in range(len(workload_list)):
		o2p_costs.append(my_cost_model.calculate_cost_fair(o2p_partitions_list[i],workload_list[i]))

	print("VPGAE-B costs on 8 tables:", beam_costs)
	print("VPGAE costs on 8 tables:", kmeans_costs)
	print("HILLCLIMB costs on 8 tables:", hill_costs)
	print("COLUMN costs on 8 tables:", column_costs)
	print("ROW costs on 8 tables:", row_costs)

	print("HYRISE costs on 24 tables:", hyrise_costs)
	print("NAVATHE costs on 24 tables:", navathe_costs)
	print("O2P costs on 24 tables:", o2p_costs)

	if use_OPTIMAL:
		print("OPTIMAL costs on 8 tables:", optimal_costs)
	
	print("Unnecessary data read of VPGAE-B:", fraction_of_unnecessary_data_read(beam_partitions_list, workload_list))
	print("Unnecessary data read of VPGAE:", fraction_of_unnecessary_data_read(kmeans_partitions_list, workload_list))
	print("Unnecessary data read of HILLCLIMB:", fraction_of_unnecessary_data_read(hill_partitions_list, workload_list))
	print("Unnecessary data read of COLUMN:", fraction_of_unnecessary_data_read(column_partitions_list, workload_list))
	print("Unnecessary data read of ROW:", fraction_of_unnecessary_data_read(row_partitions_list, workload_list))

	print("Unnecessary data read of HYRISE:", fraction_of_unnecessary_data_read(hyrise_partitions_list, workload_list))
	print("Unnecessary data read of NAVATHE:", fraction_of_unnecessary_data_read(navathe_partitions_list, workload_list))
	print("Unnecessary data read of O2P:", fraction_of_unnecessary_data_read(o2p_partitions_list, workload_list))
	if use_OPTIMAL:
		print("Unnecessary data read of OPTIMAL:", fraction_of_unnecessary_data_read(optimal_partitions_list, workload_list))

	column_RJ = np.sum(number_of_joins(column_partitions_list, workload_list))
	if column_RJ == 0:
		print("column reconstruction joins = 0")
	else:
		print("normalized reconstruction joins of VPGAE-B:", np.sum(number_of_joins(beam_partitions_list, workload_list))/column_RJ)
		print("normalized reconstruction joins of VPGAE:", np.sum(number_of_joins(kmeans_partitions_list, workload_list))/column_RJ)
		print("normalized reconstruction joins of HILLCLIMB:", np.sum(number_of_joins(hill_partitions_list, workload_list))/column_RJ)
		print("normalized reconstruction joins of COLUMN:", column_RJ/column_RJ)
		print("normalized reconstruction joins of ROW:", np.sum(number_of_joins(row_partitions_list, workload_list))/column_RJ)
		
		print("normalized reconstruction joins of HYRISE:", np.sum(number_of_joins(hyrise_partitions_list, workload_list))/column_RJ)
		print("normalized reconstruction joins of NAVATHE:", np.sum(number_of_joins(navathe_partitions_list, workload_list))/column_RJ)
		print("normalized reconstruction joins of O2P:", np.sum(number_of_joins(o2p_partitions_list, workload_list))/column_RJ)
		if use_OPTIMAL:
			print("normalized reconstruction joins of OPTIMAL:", np.sum(number_of_joins(optimal_partitions_list, workload_list))/column_RJ)

	print("--------------------")



# TPC-DS benchmark experiments
def TPC_DS_exp():
	dataset_ = dataset.tpcds_workload()
	beam_costs = []
	kmeans_costs = []
	hill_costs = []
	column_costs = []
	row_costs = []
	hyrise_costs = []
	navathe_costs = []
	o2p_costs = []
	
	beam_partitions_list = []
	kmeans_partitions_list = []
	hill_partitions_list = []
	column_partitions_list = []
	row_partitions_list = []
	workload_list = []
	hyrise_partitions_list = []
	navathe_partitions_list = []
	o2p_partitions_list = []

	for i,data in enumerate(dataset_):
		workload = Workload(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8])
		vpgae_workload = VPGAE_Workload(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8])
		
		num_node = vpgae_workload.affinity_matrix.shape[0]

		beam_cost, beam_partitions = VPGAE.partition(algo_type="VPGAE-B", workload=vpgae_workload, n_hid=num_node, n_dim=2*num_node, k=2, origin_candidate_length=6, beam_search_width=3)
		kmeans_cost, kmeans_partitions = VPGAE.partition(algo_type="VPGAE", workload=vpgae_workload, n_hid=num_node, n_dim=2*num_node, k=2)
		
		hill_cost, hill_partitions = hillclimb.partition(workload=workload)
		column_cost, column_partitions = column.partition(workload=workload)
		row_cost, row_partitions = row.partition(workload=workload)

		beam_costs.append(beam_cost)
		kmeans_costs.append(kmeans_cost)
		hill_costs.append(hill_cost)
		column_costs.append(column_cost)
		row_costs.append(row_cost)

		beam_partitions_list.append(beam_partitions)
		kmeans_partitions_list.append(kmeans_partitions)
		hill_partitions_list.append(hill_partitions)
		column_partitions_list.append(column_partitions)
		row_partitions_list.append(row_partitions)
		workload_list.append(workload)
	
	hyrise_partitions_list = [[[11], [10], [7], [13, 8, 6, 5, 4, 3, 2], [12], [9, 1]],
						[[9, 8, 7, 6, 5], [2], [4, 3], [1]],
						[[3, 1], [10], [15], [8], [9], [7], [11], [4], [28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 14, 13, 12, 6, 5, 2]],
						[[3, 1], [14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 2]],
						[[3, 1], [6, 5, 4, 2]],
						[[5, 4, 3, 1], [10, 9, 8, 7, 6, 2]],
						[[3, 1], [2]],
						[[3, 2, 1]],
						[[15, 14], [22], [12], [13], [2], [1], [11], [20, 19, 18, 17, 16, 10, 7, 6, 5, 4, 3], [21], [9, 8]],
						[[29, 27, 22, 21, 20, 19, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 5, 4, 3], [25], [24], [26], [23, 7], [18], [28], [2], [6, 1]],
						[[12, 2], [7, 1], [31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 11, 10, 9, 8, 6, 5, 4, 3]],
						[[10, 9], [2], [4, 3], [5], [11, 8], [1], [18, 17, 16, 15, 14, 13, 12, 7, 6]],
						[[5, 1], [26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 4, 3, 2]],
						[[5], [20, 19, 18, 17, 16, 15, 14, 13, 12, 8, 7, 6, 4, 2, 1], [11, 10, 9, 3]],
						[[1], [2], [4], [3], [5]],
						[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]],
						[[15, 10, 1], [19, 18, 17, 16, 14, 13, 12, 11, 9, 8, 7, 6, 5, 4, 3, 2]],
						[[1, 2, 3, 4, 5, 6, 7, 8, 9]],
						[[4, 2, 1], [3]],
						[[27, 12, 8, 1], [26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 11, 10, 9, 7, 6, 5, 4, 3, 2]],
						[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]],
						[[16, 15, 14, 3, 1], [34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 2]],
						[[28, 21, 19, 17, 16, 5], [4], [15, 14, 12, 3], [34, 33, 32, 31, 30, 29, 27, 26, 25, 24, 23, 20, 18, 13, 11, 10, 9, 8, 7, 6, 2], [22, 1]],
						[[20], [9], [4], [13], [3], [14], [1], [8], [23, 7], [2], [22, 21, 19, 18, 15, 12], [17], [16], [11, 5], [10, 6]]
						]

	for i in range(len(workload_list)):
		hyrise_costs.append(my_cost_model.calculate_cost_fair(hyrise_partitions_list[i],workload_list[i]))

	navathe_partitions_list = 	[[[13, 12], [11], [9], [10], [7], [2], [3], [4], [5], [6], [8], [1]],
							[[9, 4, 3, 2], [5], [6], [7], [8], [1]],
							[[28, 8], [10], [9], [7, 3], [4], [11], [15], [2], [5], [6], [12], [13], [14], [16], [17], [18], [19], [20], [21], [22], [23], [24], [25], [26], [27], [1]],
							[[14], [13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]],
							[[6], [5, 4, 3, 2, 1]],
							[[10], [5, 4, 3], [2], [6], [7], [8], [9], [1]],
							[[3, 1], [2]],
							[[3, 2, 1]],
							[[20, 12], [15, 14], [8], [21], [9], [13], [11], [22], [2], [3], [4], [5], [6], [7], [10], [16], [17], [18], [19], [1]],
							[[29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]],
							[[31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]],
							[[18, 3], [11, 8], [10, 9], [5], [4], [2], [6], [7], [12], [13], [14], [15], [16], [17], [1]],
							[[26], [25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]],
							[[20], [2], [11, 10, 9, 3], [4], [5], [6], [7], [8], [12], [13], [14], [15], [16], [17], [18], [19], [1]],
							[[3, 2], [5, 4, 1]],
							[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]],
							[[19], [15, 10], [2], [3], [4], [5], [6], [7], [8], [9], [11], [12], [13], [14], [16], [17], [18], [1]],
							[[1, 2, 3, 4, 5, 6, 7, 8, 9]],
							[[3], [4, 2, 1]],
							[[26], [27, 12, 8], [2], [3], [4], [5], [6], [7], [9], [10], [11], [13], [14], [15], [16], [17], [18], [19], [20], [21], [22], [23], [24], [25], [1]],
							[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]],
							[[34], [16, 15, 14, 3], [2], [4], [5], [6], [7], [8], [9], [10], [11], [12], [13], [17], [18], [19], [20], [21], [22], [23], [24], [25], [26], [27], [28], [29], [30], [31], [32], [33], [1]],
							[[34, 4], [28, 21, 19, 17, 16, 5], [22], [15, 14, 12, 3], [2], [6], [7], [8], [9], [10], [11], [13], [18], [20], [23], [24], [25], [26], [27], [29], [30], [31], [32], [33], [1]],
							[[22, 9], [20, 13], [16], [23, 7], [11, 5], [14], [3], [8], [4], [10, 6], [17], [2], [12], [15], [18], [19], [21], [1]]
							]

	for i in range(len(workload_list)):
		navathe_costs.append(my_cost_model.calculate_cost_fair(navathe_partitions_list[i],workload_list[i]))

	o2p_partitions_list = 	[[[13, 12], [11], [9], [10], [7], [2], [3], [8, 6, 5, 4], [1]],
						[[9, 4, 3, 2], [8, 7, 6, 5], [1]],
						[[28, 8], [10], [9], [7], [3], [4], [11], [15, 2], [5], [6], [12], [13], [14], [16], [17], [18], [19], [20], [21], [22], [23], [24], [25], [26], [27], [1]],
						[[14], [13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]],
						[[6], [5, 4, 3, 2, 1]],
						[[10], [3], [4], [5], [9, 8, 7, 6, 2], [1]],
						[[3, 1], [2]],
						[[3],[2,1]],
						[[20, 12], [14], [15], [8], [21], [9], [13], [11], [22], [2], [3], [4], [5], [6], [7], [10], [16], [17], [18], [19], [1]],
						[[29, 7], [28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 6, 5, 4, 3, 2, 1]],
						[[31, 12], [30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]],
						[[18, 3], [11, 8], [10, 9], [5], [4], [2], [6], [7], [12], [13], [14], [15], [16], [17], [1]],
						[[26], [25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]],
						[[20, 2], [11, 10, 9, 3], [5, 4], [19, 18, 17, 16, 15, 14, 13, 12, 8, 7, 6, 1]],
						[[3, 2], [5, 4, 1]],
						[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]],
						[[19], [18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]],
						[[1, 2, 3, 4, 5, 6, 7, 8, 9]],
						[[4, 2, 1], [3]],
						[[26], [27, 12, 8], [25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 11, 10, 9, 7, 6, 5, 4, 3, 2], [1]],
						[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]],
						[[34], [3], [14], [15], [16], [2], [4], [5], [6], [7], [8], [9], [10], [11], [12], [13], [17], [18], [19], [20], [21], [22], [23], [24], [25], [33, 32, 31, 30, 29, 28, 27, 26], [1]],
						[[34, 4], [28, 21, 19, 17, 16, 5], [22], [3], [12], [14], [15], [2], [6], [7], [8], [9], [10], [11], [13], [18], [20], [23], [24], [25], [26], [27], [29], [30], [31], [32], [33], [1]],
						[[22, 9], [13], [20], [16], [7], [23], [5], [14, 11], [3], [8], [4], [6], [10], [17], [2], [12], [15], [18], [19], [21], [1]]
						]
	
	for i in range(len(workload_list)):
		o2p_costs.append(my_cost_model.calculate_cost_fair(o2p_partitions_list[i],workload_list[i]))

	print("VPGAE-B costs on 24 tables:", beam_costs)
	print("VPGAE costs on 24 tables:", kmeans_costs)
	print("HILLCLIMB costs on 24 tables:", hill_costs)
	print("COLUMN costs on 24 tables:", column_costs)
	print("ROW costs on 24 tables:", row_costs)

	print("HYRISE costs on 24 tables:", hyrise_costs)
	print("NAVATHE costs on 24 tables:", navathe_costs)
	print("O2P costs on 24 tables:", o2p_costs)
	
	print("Unnecessary data read of VPGAE-B:", fraction_of_unnecessary_data_read(beam_partitions_list, workload_list))
	print("Unnecessary data read of VPGAE:", fraction_of_unnecessary_data_read(kmeans_partitions_list, workload_list))
	print("Unnecessary data read of HILLCLIMB:", fraction_of_unnecessary_data_read(hill_partitions_list, workload_list))
	print("Unnecessary data read of COLUMN:", fraction_of_unnecessary_data_read(column_partitions_list, workload_list))
	print("Unnecessary data read of ROW:", fraction_of_unnecessary_data_read(row_partitions_list, workload_list))

	print("Unnecessary data read of HYRISE:", fraction_of_unnecessary_data_read(hyrise_partitions_list, workload_list))
	print("Unnecessary data read of NAVATHE:", fraction_of_unnecessary_data_read(navathe_partitions_list, workload_list))
	print("Unnecessary data read of O2P:", fraction_of_unnecessary_data_read(o2p_partitions_list, workload_list))

	column_RJ = np.sum(number_of_joins(column_partitions_list, workload_list))
	if column_RJ == 0:
		print("column reconstruction joins = 0")
	else:
		print("normalized reconstruction joins of VPGAE-B:", np.sum(number_of_joins(beam_partitions_list, workload_list))/column_RJ)
		print("normalized reconstruction joins of VPGAE:", np.sum(number_of_joins(kmeans_partitions_list, workload_list))/column_RJ)
		print("normalized reconstruction joins of HILLCLIMB:", np.sum(number_of_joins(hill_partitions_list, workload_list))/column_RJ)
		print("normalized reconstruction joins of COLUMN:", column_RJ/column_RJ)
		print("normalized reconstruction joins of ROW:", np.sum(number_of_joins(row_partitions_list, workload_list))/column_RJ)

		print("normalized reconstruction joins of HYRISE:", np.sum(number_of_joins(hyrise_partitions_list, workload_list))/column_RJ)
		print("normalized reconstruction joins of NAVATHE:", np.sum(number_of_joins(navathe_partitions_list, workload_list))/column_RJ)
		print("normalized reconstruction joins of O2P:", np.sum(number_of_joins(o2p_partitions_list, workload_list))/column_RJ)

	print("--------------------")



# random dataset experiments
def random_dataset_exp():
	attributes_num = [200]
	for a_num in attributes_num:
		print("tables have {} attributes.".format(a_num))
		w_num = 40
		dataset_ = dataset.random_generator(num = w_num, a_num_range = [a_num,a_num])
		
		beam_costs = []
		kmeans_costs = []
		hill_costs = []
		column_costs = []
		
		beam_times = []
		kmeans_times = []
		hill_times = []
		
		for i,data in enumerate(dataset_):
			workload = Workload(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8])
			vpgae_workload = VPGAE_Workload(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8])
			num_node = vpgae_workload.affinity_matrix.shape[0]

			t2=time.time()
			kmeans_cost, kmeans_partitions = VPGAE.partition(algo_type="VPGAE", workload=vpgae_workload, n_hid=num_node, n_dim=2*num_node, k=2)
			kmeans_time=time.time()-t2
			print("VPGAE cost:{}, time:{:.3f}".format(kmeans_cost,kmeans_time))

			t1=time.time()
			beam_cost, beam_partitions = VPGAE.partition(algo_type="VPGAE-B", workload=vpgae_workload, n_hid=num_node, n_dim=2*num_node, k=2, origin_candidate_length=6, beam_search_width=3)
			# beam_cost, beam_partitions = 0,[]
			beam_time=time.time()-t1
			print("VPGAE-B cost:{}, time:{:.3f}".format(beam_cost,beam_time))
			
			t3=time.time()
			hill_cost, hill_partitions = hillclimb.partition(workload=workload)
			# hill_cost, hill_partitions = 0,[]
			hill_time=time.time()-t3
			print("HILLCLIMB cost:{}, time:{:.3f}".format(hill_cost,hill_time))
			print("")

			column_cost, column_partitions = column.partition(workload=workload)

			beam_costs.append(beam_cost)
			kmeans_costs.append(kmeans_cost)
			
			hill_costs.append(hill_cost)
			column_costs.append(column_cost)

			beam_times.append(beam_time)
			kmeans_times.append(kmeans_time)
			
			hill_times.append(hill_time)

		print("Avg. VPGAE cost:{}".format(np.mean(kmeans_costs)))
		print("Avg. VPGAE-B cost:{}".format(np.mean(beam_costs)))
		
		print("Avg. HILLCLIMB cost:{}".format(np.mean(hill_costs)))
		print("Avg. COLUMN cost:{}".format(np.mean(column_costs)))
		
		print("Avg. VPGAE-B time:{}".format(np.mean(beam_times)))
		print("Avg. VPGAE time:{}".format(np.mean(kmeans_times)))
		
		print("Avg. HILLCLIMB time:{}".format(np.mean(hill_times)))

		print("--------------------")


# HAP benchmark experiments
def HAP_exp():
	queries_number_list = [19]
	dataset_ = dataset.HAP_example(queries_number_list)
	for i,data in enumerate(dataset_):
		print("Workload has {} queries.".format(queries_number_list[i]))
		workload = Workload(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8])
		vpgae_workload = VPGAE_Workload(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8])
		num_node = vpgae_workload.affinity_matrix.shape[0]

		t1=time.time()
		kmeans_cost, kmeans_partitions = VPGAE.partition(algo_type="VPGAE", workload=vpgae_workload, n_hid=num_node, n_dim=2*num_node, k=2)
		kmeans_time=time.time()-t1
		print("VPGAE cost on HAP wide table (example):",kmeans_cost)
		print("VPGAE time:{}".format(kmeans_time))

		t2=time.time()
		beam_cost, beam_partitions = VPGAE.partition(algo_type="VPGAE-B", workload=vpgae_workload, n_hid=num_node, n_dim=2*num_node, k=2, origin_candidate_length=6, beam_search_width=3)
		beam_time = time.time()-t2
		print("VPGAE-B cost on HAP wide table (example):",beam_cost)
		print("VPGAE-B time:{}".format(beam_time))

		column_cost, column_partitions = column.partition(workload=workload)
		print("COLUMN layout cost on HAP wide table (example):",column_cost)

		row_cost, row_partitions = row.partition(workload=workload)
		print("ROW layout cost on HAP wide table (example):",row_cost)

		t3=time.time()
		hill_cost, hill_partitions = hillclimb.partition(workload=workload)
		hill_time=time.time()-t3
		print("HILLCLIMB cost on HAP wide table (example):",hill_cost)
		print("HILLCLIMB time:{}".format(hill_time))

		print("--------------------")

if __name__ == "__main__":
	args = parser.parse_args()
	dataset_name = args.dataset
	if dataset_name == "TPC-H":
		TPC_H_exp()
	elif dataset_name == "TPC-DS":
		TPC_DS_exp()
	elif dataset_name == "random":
		random_dataset_exp()
	elif dataset_name == "HAP":
		HAP_exp()
	else:
		raise ValueError("no such dataset, available options: \n1.TPC-H \n2.TPC-DS \n3.random \n4.HAP")