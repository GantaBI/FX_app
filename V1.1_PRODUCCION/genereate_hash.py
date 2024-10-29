





#%%
import pickle
from pathlib import Path

import streamlit_authenticator as stauth


# %%

import yaml

with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

#%%

hashed_passwords = stauth.Hasher(['abc', 'def']).generate()
# %%
hashed_passwords




# %%

import pickle
from pathlib import Path

import streamlit_authenticator as stauth

names = ["Peter Parker", "Rebecca Miller", "demosjd@gantabi.com"]
usernames = ["pparker", "rmiller", "demosjd@gantabi.com"]
passwords = ["XXX", "XXX", "demoFxCadera"]

hashed_passwords = stauth.Hasher(passwords).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)
# %%
