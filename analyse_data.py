from egonetwork_analysis import EgoNetworkAnalyzer

network_data_filename = "random_network.csv"
group_members = pd.read_csv(network_data_filename)
group_members = group_members[group_members["user_id_from"] != group_members["user_id_to"]] # Removing the self_edges
weighted_network = group_members.groupby(["user_id_from", "user_id_to"]).agg(common_convo_count=("convo_id", "nunique")).sort_values("common_convo_count", ascending=False).reset_index()

weight_col = "common_convo_count"
from_col = "user_id_from"
to_col = "user_id_to"

analyzer = EgoNetworkAnalyzer(weighted_network, from_col, to_col, weight_col)
results = analyzer.calculate_ego_networks_metrics(multi_thread=True, n_threads=23)
# alpha_threshold = 0.1
# results = multi_thread_network_metrics(weighted_network, from_col, to_col, weight_col)
df = pd.DataFrame(results)
df.to_csv(f"ego_networks_metrics_{utils.formatted_now(sepDate='_', sepTime='_', sep='_')}.csv")
        
