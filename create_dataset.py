import pandas as pd
import gzip
import pickle


# This class is designed to extract the data out of Julian McAuley dataset
class DataProvider:

    def __init__(self, category):
        self.category = category

    def get_all_data_points(self):
        df = DataProvider.get_df(self.data_path)
        return df

    @staticmethod
    def parse_from_gzip(path):
        # for memory issues
        max_extract = 100000
        count = 0
        g = gzip.open(path, 'rb')
        for l in g:
            if count < max_extract:
                yield eval(l)
            else:
                return
            count += 1


    @staticmethod
    def get_df(path):
        i = 0
        df = {}
        for d in DataProvider.parse_from_gzip(path):
            df[i] = d
            i += 1
        return pd.DataFrame.from_dict(df, orient='index')


class ReviewDataProvider(DataProvider):
    def __init__(self, category):
        super().__init__(category)
        self.data_path = "data/reviews_{}_5.json.gz".format(self.category)
        self.reviews_path = "data/X_{}_5.pkl".format(self.category)
        self.labels_path = "data/y_{}_5.pkl".format(self.category)


    def balance_dataset(self, df, max_length):
        neutral = 3
        df_pos = df[df["overall"] > neutral]
        df_neg = df[df["overall"] < neutral]
        pos_reviews = df_pos["reviewText"].tolist()
        neg_reviews = df_neg["reviewText"].tolist()
        min_length = min(len(pos_reviews), len(neg_reviews))
        if min_length < max_length:
            print("Warning, you asked for {} examples, but there are only {} for {}".format(max_length,
                                                                                            min_length, self.category))
        if min_length > max_length:
            min_length = max_length
        # keeps the dataset balanced
        pos_reviews = pos_reviews[:min_length]
        neg_reviews = neg_reviews[:min_length]
        reviews = neg_reviews + pos_reviews
        labels = [0] * min_length + [1] * min_length
        return reviews, labels

    def construct_dataset(self, sample_size):
        reviews_df = self.get_all_data_points()
        reviews, labels = self.balance_dataset(reviews_df, sample_size)
        with open(self.reviews_path, 'wb') as f:
            pickle.dump(reviews, f)
        with open(self.labels_path, 'wb') as f:
            pickle.dump(labels, f)
        return reviews, labels
