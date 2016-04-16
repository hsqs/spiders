
from weibo import weibo_miner


if __name__ == '__main__':
    target = {
        # user_id : page_num
        2663489000: 1
    }

    wm = weibo_miner.miner(target)
