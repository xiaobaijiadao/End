from gen_rank_train_data import RankTrainDataGen

import logging
import pandas as pd

cls = ['9001', '9012']

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler("rank_c1.txt", mode='w')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


logger.info("read data")


for c in cls:
    logger.info("-----cls--: {}".format(c))
    rtd = RankTrainDataGen(c, logger)
    rtd.run()
    rtd.out('../data/trainSet/rank')