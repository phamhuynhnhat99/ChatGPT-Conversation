import os, glob
import pandas as pd

all_labels = ["Positive", "Negative", "Neutral", "Unknown"]

def post_processing(gptOutcome):
    for label in all_labels:
        if label in gptOutcome:
            return label
    return "Unknown"


def just_do_it(pp_name="Post_Processing"):
    df = pd.DataFrame()
    path = os.path.join(os.path.dirname(os.pardir), pp_name)
    
    for filename in glob.glob(os.path.join(path, '*.csv')):
        tmp_df = pd.read_csv(filename)
        df = pd.concat([df, tmp_df])
    
    Label_X = [post_processing(_) for _ in list(df["Label"])]
    df["Label_X"] = Label_X

    res_path = os.path.join(path, "Label_X.csv")
    df = df.reset_index(drop=True)
    df.to_csv(res_path, index=False)


if __name__ == "__main__":
    just_do_it()