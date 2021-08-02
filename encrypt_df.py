from egonetwork_analysis import EgoNetworkAnalyzer
import pandas as pd
key = 'arandokey16bytes'


members_filename = "members_export.csv"
members = pd.read_csv(members_filename)
members = members.drop(["user_name",  "convo_name"], axis=1)
print(f"Members dtypes:\n {members.dtypes}\n")
members_enc = EgoNetworkAnalyzer.encrypt_df(members, key)
members_enc.to_csv("random_network.csv")

all_users_filename = "users_list_export.csv"
all_users = pd.read_csv(all_users_filename)
all_users = all_users.drop(["user_name"], axis=1)
print(f"All Users dtypes:\n {all_users.dtypes}\n")
all_users_enc = EgoNetworkAnalyzer.encrypt_df(all_users, key)
all_users_enc.to_csv("random_users_list.csv")


# Decrypt to double check
members_enc = pd.read_csv("random_network.csv")
print(f"Members ENC dtypes:\n {members_enc.dtypes}\n")
members = EgoNetworkAnalyzer.decrypt_df(members_enc, key)
members.to_csv("random_network_dec.csv")

all_users_enc = pd.read_csv("random_users_list.csv")
print(f"All Users ENC dtypes:\n {all_users_enc.dtypes}\n")
all_users = EgoNetworkAnalyzer.decrypt_df(all_users_enc, key)
all_users.to_csv("random_users_list_dec.csv")
